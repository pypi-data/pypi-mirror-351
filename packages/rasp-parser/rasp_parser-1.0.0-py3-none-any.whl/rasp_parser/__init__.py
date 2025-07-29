"""
RASP File Parser Library for Python

A library for parsing rocket motor data files in RASP format (.eng files).
Supports cubic spline integration for accurate total impulse calculations
when scipy is available, with fallback to Simpson's rule integration.
"""

__version__ = "1.0.0"
__author__ = "gituser12981u2"
__email__ = "squarer.human-0t@icloud.com"
__license__ = "MIT"

# Core imports
from .models import RASPMotor, ThrustCurvePoint
from .core import RASPParser, load_rasp_motor, load_rasp_motors
from .validation import MotorValidator, validate_motor
from .exceptions import (
    RASPParseError,
    RASPFileNotFoundError,
    RASPFormatError,
    RASPHeaderError,
    RASPThrustCurveError,
    RASPValidationError,
)

# Convenience imports at package level
__all__ = [
    # Main classes
    "RASPMotor",
    "ThrustCurvePoint",
    "RASPParser",
    "MotorValidator",
    # Convenience functions
    "load_rasp_motor",
    "load_rasp_motors",
    "validate_motor",
    # Exceptions
    "RASPParseError",
    "RASPFileNotFoundError",
    "RASPFormatError",
    "RASPHeaderError",
    "RASPThrustCurveError",
    "RASPValidationError",
    # Metadata
    "__version__",
]

# Optional scipy status
try:
    from scipy.interpolate import UnivariateSpline

    SCIPY_AVAILABLE = True
    del UnivariateSpline  # Clean up namespace
except ImportError:
    SCIPY_AVAILABLE = False


def get_integration_method() -> str:
    """Return the active integration method"""
    return "cubic_spline" if SCIPY_AVAILABLE else "adaptive_simpson"
