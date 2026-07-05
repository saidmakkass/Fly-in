from enum import Enum, auto
from dataclasses import dataclass
from typing import List

from .errors import LexerError


class TokenType(Enum):
    IDENTIFIER = auto()
    INTEGER = auto()

    COLON = auto()
    EQUALS = auto()
    DASH = auto()

    LBRACKET = auto()
    RBRACKET = auto()

    NEWLINE = auto()
    EOF = auto()


@dataclass(slots=True)
class Token:
    type: TokenType
    value: str | int | None

    line: int
    column: int


class Lexer:
    def __init__(self, input: str):
        self.lines = [f"{l}\n" for l in input.split("\n")]
        self.line = 1
        self.column = 1
        self.eof = False

    def __peek(self) -> str:
        if self.eof or not self.lines[self.line - 1]:
            return ""
        return self.lines[self.line - 1][self.column - 1]

    def __advance(self) -> None:
        assert not self.eof, "should not advance when at EOF"
        prev_line = self.line
        line_length = len(self.lines[self.line - 1])
        self.column += 1
        if self.column > line_length:
            self.column = 1
            self.line += 1
            if self.line > len(self.lines):
                self.eof = True
                self.line = prev_line
                self.column = line_length

    def __skip_whitespace(self) -> None:
        while not self.eof:
            char = self.__peek()
            if char.isspace() and char != '\n':
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

    def __read_integer(self) -> int:
        integer = ""
        while True:
            char = self.__peek()
            if not char or char in " :[=-]\n":
                break
            if not char.isdecimal():
                raise LexerError(self.line, self.column)
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
            token_line = self.line
            token_column = self.column
            char = self.__peek()
            if char == ":":
                output.append(
                    Token(TokenType.COLON, None, token_line, token_column)
                )
                self.__advance()
            elif char == "[":
                output.append(
                    Token(TokenType.LBRACKET, None, token_line, token_column)
                )
                self.__advance()
            elif char == "]":
                output.append(
                    Token(TokenType.RBRACKET, None, token_line, token_column)
                )
                self.__advance()
            elif char == "=":
                output.append(
                    Token(TokenType.EQUALS, None, token_line, token_column)
                )
                self.__advance()
            elif char == "-":
                output.append(
                    Token(TokenType.DASH, None, token_line, token_column)
                )
                self.__advance()
            elif char == "\n":
                if output and output[-1].type != TokenType.NEWLINE:
                    output.append(
                        Token(TokenType.NEWLINE, None, token_line, token_column)
                    )
                self.__advance()
            elif char == "#":
                self.__read_comment()
            elif char.isdigit():
                integer = self.__read_integer()
                output.append(
                    Token(TokenType.INTEGER, integer, token_line, token_column)
                )
            else:
                identifier = self.__read_identifier()
                if not identifier:
                    break
                output.append(
                    Token(
                        TokenType.IDENTIFIER,
                        identifier,
                        token_line,
                        token_column,
                    )
                )
        output.append(Token(TokenType.EOF, None, self.line, self.column))
        return output


if __name__ == "__main__":

    # print a random token from map
    from random import randint

    with open("maps/challenger/01_the_impossible_dream.txt", "r") as f:
        file = f.read()
    lexer = Lexer(file)
    tokens = lexer.evaluate()
    token = tokens[randint(0, len(tokens) - 1)]
    print(
        "maps/challenger/01_the_impossible_dream.txt:"
        f"{token.line}:{token.column} - {token}"
    )

    # print last token
    with open("maps/challenger/01_the_impossible_dream.txt", "r") as f:
        file = f.read()
    lexer = Lexer(file)
    tokens = lexer.evaluate()
    token = tokens[-1]
    print(
        "maps/challenger/01_the_impossible_dream.txt:"
        f"{token.line}:{token.column} - {token}"
    )

    # print first token
    with open("maps/challenger/01_the_impossible_dream.txt", "r") as f:
        file = f.read()
    lexer = Lexer(file)
    tokens = lexer.evaluate()
    token = tokens[0]
    print(
        "maps/challenger/01_the_impossible_dream.txt:"
        f"{token.line}:{token.column} - {token}"
    )
