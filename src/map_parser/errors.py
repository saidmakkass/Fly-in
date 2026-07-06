from .classes import Location


class ParsingError(Exception):
    def __init__(self, location: Location, message: str = "Invalid Syntax"):
        self.location = location
        super().__init__(f"Error: {message} - '{location}'")


class LexerError(Exception):
    def __init__(self, location: Location, message: str = "Invalid Token"):
        self.location = location
        super().__init__(f"Error: {message} - '{location}'")
