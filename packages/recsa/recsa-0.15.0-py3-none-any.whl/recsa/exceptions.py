"""
**********
Exceptions
**********

Base exceptions and errors for RECSA.
"""


class RecsaException(Exception):
    """Base exception for the RECSA package."""
    pass


class RecsaTypeError(RecsaException):
    pass


class RecsaValueError(RecsaException):
    pass


class RecsaParsingError(RecsaException):
	"""Base class for parsing errors."""
	pass


class RecsaLoadingError(RecsaException):
    pass


class RecsaNotImplementedError(RecsaException):
    pass


class RecsaRuntimeError(RecsaException):
    pass


class RecsaFileExistsError(RecsaValueError):
    pass
