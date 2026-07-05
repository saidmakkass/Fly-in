class ParsingError(Exception):
    def __init__(
        self, line: int, column: int, message: str = "Invalid Syntax"
    ):
        self.line = line
        self.column = column
        super().__init__(f"Error: {message}, line {line}, column {column}")


class LexerError(Exception):
    def __init__(self, line: int, column: int, message: str = "Invalid Token"):
        self.line = line
        self.column = column
        super().__init__(f"Error: {message}, line {line}, column {column}")
