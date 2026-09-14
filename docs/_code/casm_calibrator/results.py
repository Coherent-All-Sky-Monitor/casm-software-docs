"""Compose-friendly calibration result schema."""
from typing import TypedDict
import numpy as np

class CalibrationResult(TypedDict, total=False):
    """Compose-friendly calibration output.

    Same content as :class:`SVDResult` plus provenance fields. Returned
    by :func:`svd_calibrate`. ``layout_version`` is stamped when
    available so downstream beam-weight generation can record which
    antenna positions the cal was built against.
    """
    gains: np.ndarray            # (n_ant, n_chan) complex
    weights: np.ndarray          # post-flag complex weights
    flags: np.ndarray            # (n_chan,) bool
    rank1_ratios: np.ndarray
    singular_values: np.ndarray
    freqs_mhz: np.ndarray
    ant_ids: np.ndarray
    ref_ant_id: int
    source: str
    layout_version: dict
