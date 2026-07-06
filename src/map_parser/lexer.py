from typing import List

from .classes import Token, TokenType, Location
from .errors import LexingError


class Lexer:
    def __init__(self, file_lines: List[str], file_path: str):
        self.lines = file_lines
        self.file_path = file_path
        self.line = 1
        self.column = 1
        self.should_skip_whitespace = True
        self.eof = False

    def __peek(self) -> str:
        if not self.lines:
            return ""
        if self.eof or not self.lines[self.line - 1]:
            return ""
        return self.lines[self.line - 1][self.column - 1]

    def __advance(self) -> None:
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

    def __skip_whitespace(self) -> None:
        if not self.should_skip_whitespace:
            return
        while not self.eof:
            char = self.__peek()
            if char.isspace() and char != "\n":
                self.__advance()
            else:
                return

    def __read_identifier(self) -> str:
        identifier = ""
        while True:
            char = self.__peek()
            if not char or char in " :[=-]\n":
                break
            identifier += char
            self.__advance()
        return identifier

    def __read_name(self) -> str:
        name = ""
        while True:
            char = self.__peek()
            if not char or char in " -\n":
                break
            name += char
            self.__advance()
        return name

    def __read_integer(self) -> int:
        integer = ""
        token_location = Location(self.file_path, self.line, self.column)
        while True:
            char = self.__peek()
            if not char or char in " :[=-]\n":
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
        while not self.eof and self.__peek() != "\n":
            self.__advance()
        self.__advance()

    def evaluate(self) -> List[Token]:
        output: List[Token] = list()
        while not self.eof:
            self.__skip_whitespace()
            token_location = Location(self.file_path, self.line, self.column)
            char = self.__peek()
            if char.isspace() and char != "\n":
                raise LexingError(token_location, "Invalid Spacing")
            if char.isdigit():
                integer = self.__read_integer()
                output.append(
                    Token(TokenType.INTEGER, integer, token_location)
                )
            elif len(output) >= 2 and (
                (
                    output[-2].type == TokenType.IDENTIFIER
                    and output[-1].type == TokenType.COLON
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
