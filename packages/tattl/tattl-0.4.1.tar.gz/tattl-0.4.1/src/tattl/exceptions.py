class TATTLException(Exception):
    """Raised when the data given does not conform to the ``dataclass``.

    This is the base exception for all TATTL exceptions."""


class ValidationException(TATTLException):
    """Indicates that the type of a field in the data differs from the type of the ``dataclass``
    field with the same name.
    """

    pass


class MissingFieldException(TATTLException):
    """Indicates that the data is missing a required field in the ``dataclass``."""
