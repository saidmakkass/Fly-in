from typing import List

from .classes import Token, TokenType, Location
from .errors import LexerError


class Lexer:
    def __init__(self, file_lines: List[str], file_path: str):
        self.lines = file_lines
        self.file_path = file_path
        self.line = 1
        self.column = 1
        self.eof = False

    def __peek(self) -> str:
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

    def __read_integer(self) -> int:
        integer = ""
        token_location = Location(self.file_path, self.line, self.column)
        while True:
            char = self.__peek()
            if not char or char in " :[=-]\n":
                break
            if not char.isdecimal():
                raise LexerError(
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
            if char == ":":
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
            elif char == "\n":
                if output and output[-1].type != TokenType.NEWLINE:
                    output.append(
                        Token(TokenType.NEWLINE, None, token_location)
                    )
                self.__advance()
            elif char == "#":
                self.__read_comment()
            elif char.isdigit():
                integer = self.__read_integer()
                output.append(
                    Token(TokenType.INTEGER, integer, token_location)
                )
            else:
                identifier = self.__read_identifier()
                if not identifier:
                    break
                output.append(
                    Token(TokenType.IDENTIFIER, identifier, token_location)
                )
        output.append(
            Token(
                TokenType.EOF,
                None,
                Location(self.file_path, self.line, self.column),
            )
        )
        return output


if __name__ == "__main__":

    file_path = "maps/challenger/01_the_impossible_dream.txt"
    try:
        with open(file_path, "r") as f:
            file_lines = f.readlines()
    except FileNotFoundError:
        raise ValueError("File Not Found")
    except NotADirectoryError:
        raise ValueError("Not A Directory")
    except IsADirectoryError:
        raise ValueError("Is A Directory")
    except PermissionError:
        raise ValueError("Permission Error")
    except OSError as e:
        raise ValueError(f"{e}")

    lexer = Lexer(file_lines, file_path)
    try:
        tokens = lexer.evaluate()
    except LexerError as e:
        print(e)
        exit()

    from random import randint

    # print a random token from map
    token = tokens[randint(0, len(tokens) - 1)]
    print(token)

    # print last token
    token = tokens[-1]
    print(token)

    # print first token
    token = tokens[0]
    print(token)

    # # print all tokens
    # print(*tokens, sep="\n")
