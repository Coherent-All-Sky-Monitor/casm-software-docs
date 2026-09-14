"""Compose-friendly calibration orchestration and coordinate alignment."""
from __future__ import annotations
import numpy as np
from .results import CalibrationResult
from .svd import SVDCalibrator, SVDConfig
from .matrix import _build_baseline_mask, _build_hermitian_matrix
from .subband import _subband_svd_with_smooth_fit
from .validation import (axis_values, include_mask, visibility_cube,
                         visibility_metadata, availability_mask)


_ORIGINAL_HELPERS = {f.__name__: f for f in (
    _build_baseline_mask, _build_hermitian_matrix, _subband_svd_with_smooth_fit)}


def _helper(name):
    """Honor historical root replacements; otherwise use the module binding."""
    import sys
    exported = getattr(sys.modules[__package__], name)
    return exported if exported is not _ORIGINAL_HELPERS[name] else globals()[name]


def svd_calibrate(fs, ant, *, data, config: SVDConfig | None = None,
                  time_mask=None) -> CalibrationResult:
    """Compose-friendly SVD calibration.

    Must be called as ``svd_calibrate(fs, ant, data=..., ...)``. ``data``
    is keyword-only and required — SVD needs the full N x N Hermitian
    matrix, which can only be built from the full-triangle visibilities,
    not the ref+target subset carried on ``fs``.

    Parameters
    ----------
    fs : :class:`casm_vis_analysis.fringe_stop.FringeStoppedData`
        Output of :func:`casm_vis_analysis.fringe_stop`. Provides
        ``freq_mhz``, ``ref_ant``, ``source`` (provenance).
    ant : :class:`casm_io.AntennaMapping`
        Active set for the matrix (respects ``with_inactive`` overrides).
    data : VisibilityResult or dict-like, keyword-only, required
        The full-triangle visibilities from
        :func:`casm_io.read_visibilities`. Required: SVD needs the full
        N x N Hermitian matrix, which can only be built from all
        baselines (ref+target subset is not enough).
        Requires nonempty ``vis`` (T, F, B), finite ``freq_mhz`` (F,),
        and finite ``time_unix`` (T,). Coordinates on ``fs`` must match
        exactly in value and order; missing fs timestamps use data.
        Reader ``inputs`` metadata is validated and remapped for complete
        active-antenna subtriangles. Ref/targets-only selections are rejected.
    config : :class:`SVDConfig`, optional
        Defaults to ``SVDConfig()`` (per-channel, threshold=4.0,
        ref_ant_idx=0, phase-only).
    time_mask : ndarray of bool, optional
        Per-time-sample mask (True = include in the time average).
        Defaults to ``fs['time_mask']`` if present, otherwise all samples.
        Always intersected with available integrations recorded on data/fs;
        explicit selection cannot include missing or unknown rows.
        This is what makes the difference between "λ₁/λ₂ is great" and
        "λ₁/λ₂ is mush": the source has to be **up** during the averaged
        samples or its signal gets diluted by off-source noise.

    Returns
    -------
    cal : :class:`CalibrationResult`

    Raises
    ------
    ValueError
        For an inactive reference, invalid dimensions, misaligned coordinates,
        malformed masks, or nonfinite selected visibility data. Masks use
        True = include; an all-False time mask cannot be averaged.
    """
    cfg = config if config is not None else SVDConfig()
    try:
        ref_ant = int(fs.get("ref_ant"))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("ref_ant must identify an active antenna") from exc
    if isinstance(fs.get("ref_ant"), (float, np.floating)) and fs["ref_ant"] != ref_ant:
        raise ValueError("ref_ant must be an integer antenna ID")
    source = fs.get("source", "")

    def field(name):
        return data[name] if hasattr(data, "__getitem__") else getattr(data, name)

    active = sorted(ant.active_antennas())
    if ref_ant not in active:
        raise ValueError(f"ref_ant {ref_ant} is not an active antenna")
    if len(active) < 2:
        raise ValueError("calibration requires at least two active antennas")
    from dataclasses import replace
    cfg = replace(cfg, ref_ant_idx=active.index(ref_ant))

    vis_full = visibility_cube(field("vis"))
    input_indices, availability = visibility_metadata(
        data, vis_full.shape, [ant.packet_index(a) for a in active])
    n_time, n_freq, _ = vis_full.shape
    freq_mhz = axis_values(fs["freq_mhz"], n_freq, "fs freq_mhz")
    data_freq = axis_values(field("freq_mhz"), n_freq, "data freq_mhz")
    if not np.array_equal(freq_mhz, data_freq):
        raise ValueError("fs freq_mhz must match data freq_mhz in value and order")
    time_unix = axis_values(field("time_unix"), n_time, "data time_unix")
    if "time_unix" in fs:
        fs_time = axis_values(fs["time_unix"], n_time, "fs time_unix")
        if not np.array_equal(fs_time, time_unix):
            raise ValueError("fs time_unix must match data time_unix in value and order")
    fs_freq_mask = include_mask(fs.get("freq_mask"), n_freq, "freq_mask")

    # Pick the time mask: explicit kwarg wins, otherwise inherit from fs
    # (populated by fringe_stop via find_transit_window).
    if time_mask is None:
        time_mask = fs.get("time_mask")
    time_mask = (include_mask(time_mask, n_time, "time_mask") & availability
                 & availability_mask(fs.get("valid_integrations"), n_time))
    if not time_mask.any():
        raise ValueError("time_mask selects no available integrations (valid_integrations)")
    subband = cfg.subband_size is not None and cfg.subband_size >= 1
    matrix_options = {}
    if input_indices is not None:
        matrix_options["input_indices"] = input_indices
    if subband and not fs_freq_mask.all():
        matrix_options["freq_mask"] = fs_freq_mask

    # Build the Hermitian matrix. Fringe-stops each baseline toward the
    # source BEFORE time-averaging — without that, the rotating
    # geometric phase washes the rank-1 structure out and lambda_1 /
    # lambda_2 collapses.
    vis_avg = _helper("_build_hermitian_matrix")(
        vis_full, ant,
        freq_mhz=freq_mhz, time_unix=time_unix, source=source,
        time_mask=time_mask, **matrix_options,
    )

    # Optional: build a baseline-length mask. Excludes baselines too
    # short to satisfy the rank-1 source assumption for the calibrator
    # source — at 410 MHz, sub-1.5λ baselines see solar corona /
    # Galactic background structure that contaminates lambda_2.
    baseline_mask = None
    if cfg.min_baseline_wavelengths is not None:
        df = ant.dataframe
        positions = np.array([
            df.loc[df["antenna_id"] == a, ["x_m", "y_m", "z_m"]].values[0]
            for a in active
        ])
        baseline_mask = _helper("_build_baseline_mask")(
            positions,
            float(np.max(freq_mhz)),
            cfg.min_baseline_wavelengths,
        )

    # When subband_size is set, route through the subband path that
    # honours fs['freq_mask'] inside each subband mean and fits a
    # smooth per-antenna gain across valid subbands.
    if subband:
        result = _helper("_subband_svd_with_smooth_fit")(
            vis_avg, freq_mhz, fs_freq_mask, cfg,
            baseline_mask=baseline_mask,
        )
    else:
        result = SVDCalibrator(cfg, baseline_mask=baseline_mask).calibrate(vis_avg)

    # Honour the RFI mask carried on fs (or passed explicitly).
    # Behaviour at flagged channels follows ``cfg.masked_band_strategy``:
    #   - 'zero': flags=False, gains=0 (default; safe).
    #   - 'geo_fallback': flags=True, gains=1 (geo-only deploy).
    #   - 'extrapolate': flags=True, gains=polynomial smooth-fit values.
    flags = result.flags.copy()
    gains = result.gains.copy()
    weights = result.weights.copy()
    strategy = getattr(cfg, "masked_band_strategy", "zero")
    if fs.get("freq_mask") is not None:
        rfi = ~fs_freq_mask
        if strategy == "zero":
            flags &= fs_freq_mask
            gains[:, rfi] = 0.0
            weights[:, rfi] = 0.0
        elif strategy == "geo_fallback":
            flags |= rfi
            gains[:, rfi] = 1.0 + 0j
            weights[:, rfi] = 1.0 + 0j
        elif strategy == "extrapolate":
            flags |= rfi
            # Preserve the solver's values, including subband smooth fits.
        else:
            raise ValueError(
                f"Unknown masked_band_strategy={strategy!r}; "
                f"expected 'zero', 'geo_fallback', or 'extrapolate'."
            )

    return {
        "gains": gains,
        "weights": weights,
        "flags": flags,
        "rank1_ratios": result.rank1_ratios,
        "singular_values": result.singular_values,
        "freqs_mhz": freq_mhz,
        "ant_ids": np.asarray(active),
        "ref_ant_id": ref_ant,
        "source": source,
        "layout_version": {},   # populated when AntennaMapping carries provenance
    }
