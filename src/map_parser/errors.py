from .classes import Location


class ValidationError(Exception):
    """Raised when a map validation rule is violated.

    The error message includes the optional `location` where the error
    occurred.
    """
    def __init__(self, location: Location | None, message: str):
        """Create a ValidationError with optional location info."""
        super().__init__(
            f"Error: {message}"
            + (f" - '{location}'" if location is not None else "")
        )


class ParsingError(Exception):
    """Raised when the parser encounters invalid syntax."""
    def __init__(self, location: Location, message: str):
        """Create a ParsingError with the token location and message."""
        super().__init__(f"Error: {message} - '{location}'")


class LexingError(Exception):
    """Raised when the lexer encounters invalid input."""
    def __init__(self, location: Location, message: str):
        """Create a LexingError with the token location and message."""
        super().__init__(f"Error: {message} - '{location}'")
