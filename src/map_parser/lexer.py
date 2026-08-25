from typing import List

from .classes import Token, TokenType, Location
from .errors import LexingError


class Lexer:
    """Simple lexer turning file lines into a stream of tokens.

    Args:
        file_lines: Lines of the input file to tokenize.
        file_path: Path used for token locations.
    """
    def __init__(self, file_lines: List[str], file_path: str):
        self.lines = file_lines
        self.file_path = file_path
        self.line = 1
        self.column = 1
        self.eof = False

    def __peek(self) -> str:
        """Return the current character without advancing; empty on EOF."""
        if not self.lines:
            return ""
        if self.eof or not self.lines[self.line - 1].strip():
            return ""
        return self.lines[self.line - 1][self.column - 1]

    def __advance(self) -> None:
        """Advance the current position by one character, updating EOF."""
        if self.eof:
            return
        line_length = len(self.lines[self.line - 1])
        self.column += 1
        if self.column > line_length:
            if self.line < len(self.lines):
                self.column = 1
                self.line += 1
            else:
                self.eof = True
                self.column = line_length + 1

    def __read_space(self) -> bool:
        """Consume whitespace."""
        create_token = False
        while not self.eof:
            char = self.__peek()
            if not char:
                self.__advance()
                create_token = False
            elif char.isspace() and char != "\n":
                self.__advance()
                create_token = True
            else:
                break
        return create_token

    def __read_identifier(self) -> str:
        """Read an identifier (until a delimiter) and return it."""
        identifier = ""
        while True:
            char = self.__peek()
            if not char or char in " :[=-]#\n":
                break
            identifier += char
            self.__advance()
        return identifier

    def __read_name(self) -> str:
        """Read a name token (allows spaces until dash or newline)."""
        name = ""
        while True:
            char = self.__peek()
            if not char or char in " -\n":
                break
            name += char
            self.__advance()
        return name

    def __read_integer(self) -> int:
        """Read an integer token and return it; raise on invalid digits."""
        integer = ""
        token_location = Location(self.file_path, self.line, self.column)
        while True:
            char = self.__peek()
            if not char or char in " :[=-]#\n":
                break
            if not char.isdecimal():
                raise LexingError(
                    token_location,
                    "Invalid Integer",
                )
            integer += char
            self.__advance()
        return int(integer)

    def __read_comment(self) -> None:
        """Skip characters until the end of the current line."""
        while not self.eof and self.__peek() != "\n":
            self.__advance()

    def evaluate(self) -> List[Token]:
        """Tokenize the input lines and return the list of tokens."""
        if not self.lines:
            raise LexingError(Location(self.file_path, 1, 1), "Empty File")
        output: List[Token] = list()
        while not self.eof:
            token_location = Location(self.file_path, self.line, self.column)
            if (
                self.__read_space()
                and output
                and output[-1].type != TokenType.NEWLINE
            ):
                output.append(Token(TokenType.SPACE, None, token_location))
            token_location = Location(self.file_path, self.line, self.column)
            char = self.__peek()
            if char.isdigit():
                integer = self.__read_integer()
                output.append(
                    Token(TokenType.INTEGER, integer, token_location)
                )
            elif len(output) >= 3 and (
                (
                    output[-3].type == TokenType.IDENTIFIER
                    and output[-2].type == TokenType.COLON
                    and output[-1].type == TokenType.SPACE
                )
                or (
                    output[-2].type == TokenType.NAME
                    and output[-1].type == TokenType.DASH
                )
            ):
                name = self.__read_name()
                output.append(Token(TokenType.NAME, name, token_location))
            elif char == ":":
                output.append(Token(TokenType.COLON, None, token_location))
                self.__advance()
            elif char == "[":
                output.append(Token(TokenType.LBRACKET, None, token_location))
                self.__advance()
            elif char == "]":
                output.append(Token(TokenType.RBRACKET, None, token_location))
                self.__advance()
            elif char == "=":
                output.append(Token(TokenType.EQUALS, None, token_location))
                self.__advance()
            elif char == "-":
                output.append(Token(TokenType.DASH, None, token_location))
                self.__advance()
                self.should_skip_whitespace = False
                continue
            elif char == "+":
                output.append(Token(TokenType.PLUS, None, token_location))
                self.__advance()
                self.should_skip_whitespace = False
                continue
            elif char == "\n":
                if output and output[-1].type != TokenType.NEWLINE:
                    output.append(
                        Token(TokenType.NEWLINE, None, token_location)
                    )
                self.__advance()
            elif char == "#":
                self.__read_comment()
            else:
                identifier = self.__read_identifier()
                if not identifier:
                    break
                output.append(
                    Token(TokenType.IDENTIFIER, identifier, token_location)
                )
            self.should_skip_whitespace = True
        output.append(
            Token(
                TokenType.EOF,
                None,
                Location(self.file_path, self.line, self.column),
            )
        )
        return output
