"""CASM SVD-based beamformer calibration package."""

__version__ = "1.0.0"

from .output import CalibrationWeightsWriter
from .svd import SVDCalibrator, SVDConfig, SVDMode, SVDResult
from .visibility import VisibilityLoader, VisibilityMatrix
from .results import CalibrationResult
from .calibration import svd_calibrate
from .products import save_calibration, plot_calibration
# Retain historical private imports for notebooks and downstream tests.
from .matrix import _build_baseline_mask, _build_hermitian_matrix
from .subband import _subband_svd_with_smooth_fit

__all__ = [
    "SVDCalibrator",
    "SVDConfig",
    "SVDMode",
    "SVDResult",
    "VisibilityLoader",
    "VisibilityMatrix",
    "CalibrationWeightsWriter",
    "CalibrationResult",
    "svd_calibrate",
    "save_calibration",
    "plot_calibration",
]
