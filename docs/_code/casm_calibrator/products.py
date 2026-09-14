"""Dictionary-based calibration serialization and diagnostic plotting."""
import numpy as np

def save_calibration(cal, path, *, n_time_averaged=0, rfi_mask=None,
                     overwrite=False):
    """Save a :class:`CalibrationResult` dict.

    Output format is chosen by the file extension:

    * ``.h5`` / ``.hdf5`` (preferred): HDF5 with top-level datasets
      ``weights``, ``gains``, ``flags``, ``freqs_hz``, ``freqs_mhz``,
      ``ant_ids``, ``rank1_ratios``, plus attrs ``ref_ant_id``,
      ``source``, ``n_time_averaged``. Consumed by
      ``bf_weights_generator.load_calibration_weights``.
    * ``.npz`` (legacy): same field set, NPZ-archived.

    Reusable from notebooks; mirrors what
    :class:`CalibrationWeightsWriter` does for the legacy ``SVDResult``
    dataclass.

    Parameters
    ----------
    cal : :class:`CalibrationResult`
        From :func:`svd_calibrate`.
    path : str or Path
        Output path. Extension picks the format.
    n_time_averaged : int, optional
        Integration count that went into the time average. Recorded as
        provenance.
    rfi_mask : ndarray of bool, optional
        Per-channel mask (True=good). Combined (AND) with ``cal['flags']``
        before writing. Channels where the combined mask is False have
        their weights and gains zeroed.
    overwrite : bool, optional
        If False (default), raise ``FileExistsError`` when ``path``
        already exists. Pass ``overwrite=True`` to replace the existing
        file. The parent directory is created automatically.
    """
    from pathlib import Path
    p = Path(path)

    if p.exists() and not overwrite:
        raise FileExistsError(
            f"Cal file exists: {p}. Pass overwrite=True to replace."
        )
    p.parent.mkdir(parents=True, exist_ok=True)

    flags = np.asarray(cal["flags"]).copy()
    if rfi_mask is not None:
        flags = flags & np.asarray(rfi_mask, dtype=bool)

    weights = cal["weights"].copy()
    gains = cal["gains"].copy()
    weights[:, ~flags] = 0.0
    gains[:, ~flags] = 0.0

    freqs_mhz = np.asarray(cal["freqs_mhz"], dtype=np.float64)
    freqs_hz = freqs_mhz * 1e6
    ant_ids = np.asarray(cal["ant_ids"], dtype=int)
    rank1 = np.asarray(cal["rank1_ratios"], dtype=np.float64)

    weights64 = weights.astype(np.complex64)
    gains64 = gains.astype(np.complex64)

    ext = p.suffix.lower()
    if ext in (".h5", ".hdf5"):
        import h5py
        with h5py.File(p, "w") as f:
            f.create_dataset("weights", data=weights64, compression="gzip")
            f.create_dataset("gains",   data=gains64,  compression="gzip")
            f.create_dataset("flags",   data=flags,    compression="gzip")
            f.create_dataset("freqs_hz",  data=freqs_hz)
            f.create_dataset("freqs_mhz", data=freqs_mhz)
            f.create_dataset("ant_ids",   data=ant_ids)
            f.create_dataset("rank1_ratios", data=rank1)
            f.attrs["ref_ant_id"]      = int(cal["ref_ant_id"])
            f.attrs["source"]          = str(cal["source"])
            f.attrs["n_time_averaged"] = int(n_time_averaged)
    elif ext == ".npz":
        np.savez_compressed(
            str(p),
            weights=weights64, gains=gains64, flags=flags,
            freqs_hz=freqs_hz, freqs_mhz=freqs_mhz,
            ant_ids=ant_ids, rank1_ratios=rank1,
            ref_ant_id=int(cal["ref_ant_id"]),
            source=str(cal["source"]),
            n_time_averaged=int(n_time_averaged),
        )
    else:
        raise ValueError(
            f"Unsupported extension {ext!r} for {p}. Use .h5 (preferred) or .npz."
        )


def plot_calibration(cal, *, threshold=None, rfi_ranges=None,
                     output_path=None, ant=None):
    """Notebook-friendly diagnostic plots: σ₁/σ₂, gain phase, gain amplitude.

    Returns a list of three matplotlib Figures (rank1, phase, amplitude).
    When ``output_path`` is provided, also saves PNGs alongside it
    (``{base}_rank1.png``, ``{base}_phase.png``, ``{base}_amp.png``).

    Parameters
    ----------
    cal : :class:`CalibrationResult`
    threshold : float, optional
        Drawn as a horizontal line on the σ₁/σ₂ plot. If None, infers
        from the smallest passing ratio.
    rfi_ranges : list of (lo_mhz, hi_mhz), optional
        Shaded as gray bands on each subplot.
    output_path : str or Path, optional
        If given, save PNGs and don't display.
    ant : :class:`AntennaMapping`, optional
        Used for richer per-antenna labels (e.g. "Ant 9 N21E1"). Falls
        back to "Ant N" if not given.
    """
    import matplotlib.pyplot as plt
    from pathlib import Path

    flags = np.asarray(cal["flags"])
    ratios = np.asarray(cal["rank1_ratios"])
    gains = cal["gains"]
    freqs_mhz = np.asarray(cal["freqs_mhz"])
    ant_ids = list(cal["ant_ids"])
    n_ant = gains.shape[0]
    rfi_ranges = rfi_ranges or []

    if threshold is None:
        good = ratios[flags & np.isfinite(ratios)]
        threshold = float(good.min()) if good.size else 4.0

    # Friendly per-antenna labels.
    def _label(aid):
        base = f"Ant {aid}"
        if ant is None:
            return base
        try:
            df = ant.dataframe
            row = df.loc[df.antenna_id == aid].iloc[0]
            grid = (f" {row['row']}{row['col']}"
                    if row.get("row") and row.get("col") else "")
            return f"{base}{grid}"
        except Exception:
            return base
    labels = [_label(a) for a in ant_ids]

    src = cal.get("source", "")

    # 1. σ₁ / σ₂ vs frequency
    fig1, ax = plt.subplots(figsize=(13, 4))
    ratios_clip = np.clip(ratios, 0, 50)
    ax.scatter(freqs_mhz, ratios_clip, c=np.where(flags, "C0", "red"),
               s=4, alpha=0.6)
    ax.axhline(threshold, color="orange", ls="--", lw=1.2,
               label=f"threshold = {threshold:.1f}")
    for lo, hi in rfi_ranges:
        ax.axvspan(lo, hi, alpha=0.08, color="gray")
    n_good = int(flags.sum())
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel(r"$\lambda_1 / \lambda_2$")
    ax.set_title(f"Rank-1 quality ({src}) — {n_good}/{len(flags)} channels passed")
    ax.set_xlim(freqs_mhz[0], freqs_mhz[-1])
    ax.set_ylim(0, max(threshold * 1.5, ratios_clip.max() * 1.05))
    ax.legend(loc="upper right")
    fig1.tight_layout()

    # 2. Per-antenna gain phase
    fig2, ax = plt.subplots(figsize=(13, 4))
    for k in range(n_ant):
        phase = np.angle(gains[k], deg=True).astype(float)
        phase[~flags] = np.nan
        ax.plot(freqs_mhz, phase, lw=0.7, alpha=0.8, label=labels[k])
    for lo, hi in rfi_ranges:
        ax.axvspan(lo, hi, alpha=0.08, color="gray")
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Gain phase (deg)")
    ax.set_title(f"Per-antenna gain phase ({src})")
    ax.set_xlim(freqs_mhz[0], freqs_mhz[-1])
    ax.legend(fontsize=7, ncol=max(1, n_ant // 6),
              loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig2.tight_layout()

    # 3. Per-antenna gain amplitude
    fig3, ax = plt.subplots(figsize=(13, 4))
    for k in range(n_ant):
        amp = np.abs(gains[k]).astype(float)
        amp[~flags] = np.nan
        ax.plot(freqs_mhz, amp, lw=0.7, alpha=0.8, label=labels[k])
    for lo, hi in rfi_ranges:
        ax.axvspan(lo, hi, alpha=0.08, color="gray")
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Gain amplitude")
    ax.set_title(f"Per-antenna gain amplitude ({src})")
    ax.set_xlim(freqs_mhz[0], freqs_mhz[-1])
    ax.legend(fontsize=7, ncol=max(1, n_ant // 6),
              loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig3.tight_layout()

    figs = [fig1, fig2, fig3]
    if output_path is not None:
        base = Path(output_path)
        stem, suffix = base.with_suffix(""), base.suffix or ".png"
        for fig, name in zip(figs, ("rank1", "phase", "amp")):
            fig.savefig(f"{stem}_{name}{suffix}", dpi=150, bbox_inches="tight")
            plt.close(fig)
    else:
        plt.show()
    return figs
