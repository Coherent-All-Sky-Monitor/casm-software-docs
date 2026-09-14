# Convert a beam dump to a filterbank

```
casm-beamdump-to-fil '/mnt/nvme4/data/casm/beam_dumps/beam_0-63_2026-08-16-03:22:43.dat.*' \
    --out-dir /mnt/nvme3/vishnu/aug16/fil --prefix aug16 --name 3=b03
```

Beam dumps are raw DADA-headered float32 blocks. Folding
([fold a pulsar](fold-b0329.md)) and dynamic spectra
([plot a solar dynamic spectrum](solar-waterfall.md)) both start from a
filterbank, so this conversion is the first step on any new day's data.

## Where dumps live and what a block file holds

Beam dumps land in `/mnt/nvme4/data/casm/beam_dumps/` on the machine that
serves the beam block. corr1 carries beams 0-255 in four 64-beam blocks
(`beam_0-63`, `beam_64-127`, `beam_128-191`, `beam_192-255`); corr2 carries
beams 256-511 in the other four, on corr2's own disk under the same path. The
incoherent beam is corr1 only, in `/mnt/nvme4/data/casm/incoh_beam_dumps/` as
`beam_Incoherent_<UTC>.dat.N`.

Each file is `beam_<block>_<UTC>.dat.N`: a 4096-byte ASCII DADA header then a
float32 payload of shape `[ndump, nbeam, nchan, samps_per_dump]`. One
observation writes many numbered parts, and every part carries its own
`UTC_START`, so a filterbank built from a later part gets the right `tstart`
with no header patching.

`BEAM_DUMP_LIST` in the header is the global request for the whole array. A
block file stores only the listed beams that fall inside its own
`FIRST_BEAM`-`LAST_BEAM` range. The example above requested beams 3, 7 and
213: beams 3 and 7 are in `beam_0-63`, beam 213 is in `beam_192-255`, and each
file holds only its own share. Run one conversion per block file your request
touched.

Disk cost scales with the per-block beam count: 11.7 MB/s per beam at
`BEAM_DUMP_DOWNSAMP 1`, 5.9 MB/s at downsamp 2, 2.9 MB/s at downsamp 4. An
hour of one beam at full rate is 42 GB.

To find out where a beam pointed, query `casm_t2.weights_registry` (which
weights product was live at a given UTC, and the alt/az of each beam under it);
`t3-weights-watch` writes the rows at every reload.

## Convert

The converter streams at constant RAM, reads the dump header itself, and
writes one `.fil` per beam present in the file at `nbits=32`. It is a console
script in `casm_offline_env`:

```
casm-beamdump-to-fil '<glob>' --out-dir DIR [--prefix P] [--name BEAM=NAME]
                     [--source-name NAME] [--max-dumps N]
```

- `<glob>` matches the `.dat.*` parts. Quote it, the tool expands it.
- `--prefix` is prepended to every output basename; a trailing `_` is added
  if you omit it, so `--prefix aug16` gives `aug16_b03.fil`.
- `--name 3=b03` names the output for beam 3. Unnamed beams become `b<NN>`,
  the incoherent beam becomes `IB`.
- `--source-name` defaults to `B0329+54`; the header RA/Dec are fixed to
  B0329+54 and are not CLI-settable. Set them with `casm-fil-clean` if the
  fold needs a different source.
- `--max-dumps N` stops after N dumps, for a quick test.

There is no flag that selects a subset of beams: every requested beam inside
the block is written. Size the output directory for all of them.

Keep output paths short. filtool has a fixed 80-character `rawdatafile`
buffer, so the tool rejects an output path of 79 characters or more.

corr2 blocks are streamed over ssh, nothing is copied to local disk first:

```
casm-beamdump-to-fil 'casm-corr2:/mnt/nvme4/data/casm/beam_dumps/beam_384-447_2026-08-16-03:22:43.dat.*' \
    --out-dir /mnt/nvme3/vishnu/aug16/fil --prefix aug16
```

ssh reads run at 86-89 MB/s against 305-376 MB/s local, so budget roughly 4x
the wall time. The direction only works corr1 -> corr2.

The local run above printed:

```
1 files () | beams [3, 7] | nchan 3072 | tsamp 4.1943 ms | tstart MJD 61268.14077547 | fch1 484.375 foff -0.030517578125
  beam_0-63_2026-08-16-03:22:43.dat.0: 56 dumps (cumulative 56)
DONE: 56 dumps = 2.0 min per beam
  .../aug16_b03.fil  0.35 GB
  .../aug16_b07.fil  0.35 GB
```

## Check the header

```python
from casm_io import FilterbankFile

fil = "/mnt/nvme3/vishnu/aug16/fil/aug16_b03.fil"
fb = FilterbankFile(fil, verbose=False)
print("nchans  ", fb.nchans)
print("tsamp   ", fb.header["tsamp"], "s")
print("tstart  ", fb.header["tstart"], "MJD")
print("nsamples", fb.nsamples)
print("nbeams  ", fb.nbeams)
print("duration", fb.nsamples * fb.header["tsamp"], "s")
```

For this file:

```
nchans   3072
tsamp    0.004194304 s
tstart   61268.14077546913 MJD
nsamples 28672
nbeams   1
duration 120.25908428800001 s
```

### The nbeams trap

`nbeams` must be 1. Files written by the corr1 copy of the converter before
2026-08-19 carry `nbeams` = the number of beams in the whole block, although
each file holds one beam. sigpyproc then reports `nsamples` too small by that
factor and `FilterbankFile` routes the read to its multibeam loader, which
strides the payload wrong and returns interleaved garbage. The corr2 copy was
fixed 2026-08-18, corr1 on 2026-08-19.

Diagnosis: `fb.nbeams > 1` on a per-beam file is the bug. A cross-check is
`fb.nsamples * fb.header["tsamp"]` against the dump's known duration; the
affected files come out short by the block beam count.

Workaround for an affected file, without rewriting it: take the header from
`casm_io`, then memmap the payload with the true sample count.

```python
import numpy as np
from casm_io.filterbank.header import read_sigproc_header
from pathlib import Path

hdr, header_size = read_sigproc_header(fil)
nchans = hdr["nchans"]
# one beam per file regardless of the header's nbeams; 4 bytes per float32 sample
nsamp = (Path(fil).stat().st_size - header_size) // (nchans * 4)
data = np.memmap(fil, dtype=np.float32, mode="r",
                 offset=header_size, shape=(nsamp, nchans))
print(nsamp, data.shape)
```

This is bit-exact against the raw dump. Fixing the header instead is the
better option if the file will be folded, since dspsr and filtool read
`nbeams` too.

## Clean (optional)

```
casm-fil-clean /mnt/nvme3/vishnu/aug16/fil/aug16_b03.fil --out-base aug16_b03_clean \
    --workdir /mnt/nvme3/vishnu/aug16/clean
```

This runs the validated filtool pass through apptainer: `kadaneF 8 4` time-domain
zaps plus `zdot` zero-DM removal, `zapthre -1`, `baseline 8`, float32 out,
writing `<workdir>/<out-base>_01.fil`. Other flags: `--source-name`, `--ra`,
`--dec` (defaults `PSRJ0332+5434`, `03:32:59.4096`, `54:34:43.329`),
`--threads` (default 8). The apptainer image path is a Python-API argument
only.

It refuses `tsamp > 0.1 s`: filtool core-dumps on slow-sampled monitoring
dumps, so cleaning is for search-rate fils only.

When to use it: zdot before trusting any fold or search S/N, at a cost of
about 6% S/N on interference-free data. Skip it for raw comparisons, and skip
it for solar work. The solar waterfall does its own per-channel normalization
and zdot would remove the broadband time-variable signal being measured.

## Quick look

Cut a short interval first, then read it. `split_filterbank` seeks to the
requested samples, so the full file is never loaded.

```python
import matplotlib.pyplot as plt
import numpy as np
from casm_io import FilterbankFile
from casm_io.filterbank import split_filterbank

nsamp_30s = int(round(30.0 / fb.header["tsamp"]))    # 30 s of samples
cut = "/mnt/nvme3/vishnu/aug16/fil/aug16_b03_cut.fil"
split_filterbank(fil, cut, start_sample=nsamp_30s, nsamples=nsamp_30s,
                 verbose=False)

cb = FilterbankFile(cut, verbose=False)
data = cb.data                                        # (nsamples, nchans)
norm = data / np.median(data, axis=0)                 # divide out the bandpass
tfac = 16                                             # ~67 ms time bins
nbin = norm.shape[0] // tfac
img = norm[:nbin * tfac].reshape(nbin, tfac, -1).mean(axis=1)

t_s = np.arange(nbin) * tfac * cb.header["tsamp"]
lo, hi = np.percentile(img, [5, 95])
fig, ax = plt.subplots(figsize=(7.0, 3.6))
# origin="upper": channel 0 is the top of the band (foff is negative)
ax.imshow(img.T, aspect="auto", origin="upper", cmap="viridis",
          vmin=lo, vmax=hi,
          extent=[t_s[0], t_s[-1], cb.freq_mhz[-1], cb.freq_mhz[0]])
ax.set_xlabel("Time since cutout start (s)")
ax.set_ylabel("Frequency (MHz)")
fig.colorbar(ax.images[0], ax=ax, label="Power / channel median")
fig.tight_layout()
plt.show()
```

```{figure} ../_static/tutorials/filterbank/beamdump-quicklook.png
:alt: Dynamic spectrum of 30 seconds of coherent beam 3, frequency 484 to 390 MHz, each channel divided by its median.

Coherent beam 3 from block `beam_0-63`, 30 seconds starting 30 s into the
recording, 67 ms time bins. Each channel is divided by its own median, so the
colour is relative power and the bandpass shape is removed. The band at
476-482 MHz swings by several percent on a few-second timescale; that is
interference, and it is what `casm-fil-clean` removes.
```

What to check before going further: the bandpass should be smooth apart from
known interference bands, the channel medians should all be non-zero, and the
time axis should have no steps at part boundaries. A channel median of zero
means a dead channel and will produce division warnings here.

## Next

- [Fold a pulsar from a beam dump](fold-b0329.md)
- [Plot a solar dynamic spectrum](solar-waterfall.md)

## Provenance

Block file: `/mnt/nvme4/data/casm/beam_dumps/beam_0-63_2026-08-16-03:22:43.dat.0`
(704647168 bytes, single part, `BEAM_DUMP_LIST 3,7,213`,
`BEAM_DUMP_DOWNSAMP 4`, `NCHAN 3072`). Beam 3, converted on corr1 with

```
casm-beamdump-to-fil '/mnt/nvme4/data/casm/beam_dumps/beam_0-63_2026-08-16-03:22:43.dat.*' \
    --out-dir <out> --prefix aug16 --name 3=b03
```

which wrote `aug16_b03.fil` and `aug16_b07.fil` at 0.35 GB each in 3.8 s. The
header values above are `aug16_b03.fil`'s, with `nbeams` 1.

Figure rendered from the Python blocks on this page by
`scripts/render_beamdump_tutorial.py`.
