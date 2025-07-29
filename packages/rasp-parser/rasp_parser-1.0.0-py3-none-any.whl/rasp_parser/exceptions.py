"""
Custom exceptions for RASP parser
"""


class RASPParseError(Exception):
    """Exception raised when parsing RASP files fails"""

    pass


class RASPFileNotFoundError(RASPParseError):
    """Raised when a RASP file cannot be found"""

    pass


class RASPFormatError(RASPParseError):
    """Raised when RASP file format is invalid"""

    pass


class RASPHeaderError(RASPFormatError):
    """Raised when RASP header line is malformed"""

    pass


class RASPThrustCurveError(RASPFormatError):
    """Raised when thrust curve data is invalid"""

    pass


class RASPValidationError(RASPParseError):
    """Raised when motor data fails validation"""

    pass
