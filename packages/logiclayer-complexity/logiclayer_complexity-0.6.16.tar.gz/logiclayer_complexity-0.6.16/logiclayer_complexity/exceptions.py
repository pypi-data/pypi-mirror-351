class ComplexityException(Exception):  # noqa: N818
    """Base class for all exceptions in this module."""

    code: int = 500
    message: str = "Backend error"


class ParameterError(ComplexityException):
    """Base class for errors related to the parameters requested by the user."""

    code = 400


class CalculationError(ComplexityException):
    """Base class for errors ocurring during the calculation phase."""
