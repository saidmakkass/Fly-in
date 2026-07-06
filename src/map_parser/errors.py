from .classes import Location


class ValidationError(Exception):
    def __init__(self, location: Location | None, message: str):
        super().__init__(
            f"Error: {message}"
            + (f" - '{location}'" if location is not None else "")
        )


class ParsingError(Exception):
    def __init__(self, location: Location, message: str):
        super().__init__(f"Error: {message} - '{location}'")


class LexingError(Exception):
    def __init__(self, location: Location, message: str):
        super().__init__(f"Error: {message} - '{location}'")
