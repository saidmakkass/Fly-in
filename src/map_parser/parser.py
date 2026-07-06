from typing import List, cast

from .classes import Token, TokenType, Zone, Connection, Map
from .errors import ParsingError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos: int = 0
        self.zones: List[Zone] = list()
        self.connections: List[Connection] = list()

    def __peek(self, offset: int = 0) -> Token:
        return self.tokens[self.pos + offset]

    def __advance(self) -> None:
        token = self.__peek()
        if token.type != TokenType.EOF:
            self.pos += 1

    def __expect(
        self, type: TokenType, value: str | int | None = None
    ) -> Token:
        token = self.__peek()
        if token.type != type:
            raise ParsingError(
                token.location,
                f"Expecting {type.name} Got {token.type.name}",
            )
        if value is not None:
            if token.value != value:
                raise ParsingError(
                    token.location,
                    f"Expecting {value} Got {token.value}",
                )
        self.__advance()
        return token

    def __parse_nb_drones(self) -> int:
        self.__expect(TokenType.IDENTIFIER, "nb_drones")
        self.__expect(TokenType.COLON)
        return cast(int, self.__expect(TokenType.INTEGER).value)

    def __parse_Zone(self, kind: str = "hub") -> Zone:
        name: str
        x: int
        y: int
        zone_type: str = "normal"
        color: str | None = None
        max_drones: int = 1

        self.__expect(TokenType.COLON)
        token = self.__expect(TokenType.IDENTIFIER)
        name = cast(str, token.value)
        if self.__peek().type == TokenType.DASH:
            self.__advance()
            x = cast(int, self.__expect(TokenType.INTEGER).value) * -1
        else:
            x = cast(int, self.__expect(TokenType.INTEGER).value)
        if self.__peek().type == TokenType.DASH:
            self.__advance()
            y = cast(int, self.__expect(TokenType.INTEGER).value) * -1
        else:
            y = cast(int, self.__expect(TokenType.INTEGER).value)
        if self.__peek().type == TokenType.LBRACKET:
            self.__advance()
            while self.__peek().type != TokenType.RBRACKET:
                token = self.__expect(TokenType.IDENTIFIER)
                match token.value:
                    case "zone":
                        self.__expect(TokenType.EQUALS)
                        token = self.__expect(TokenType.IDENTIFIER)
                        try:
                            zone_type = cast(str, token.value)
                        except KeyError:
                            raise ParsingError(
                                token.location,
                                f"Unknown Hub Type: {token.value}",
                            )
                    case "color":
                        self.__expect(TokenType.EQUALS)
                        color = cast(
                            str, self.__expect(TokenType.IDENTIFIER).value
                        )
                    case "max_drones":
                        self.__expect(TokenType.EQUALS)
                        max_drones = cast(
                            int, self.__expect(TokenType.INTEGER).value
                        )
                    case _:
                        raise ParsingError(
                            token.location,
                            f"Unknown Key '{token.value}'",
                        )
            self.__expect(TokenType.RBRACKET)
        self.__expect(TokenType.NEWLINE)
        return Zone(kind, name, x, y, zone_type, color, max_drones)

    def __parse_connection(self) -> Connection:
        zone_a: str
        zone_b: str

        max_link_capacity: int = 1

        self.__expect(TokenType.COLON)
        token = self.__expect(TokenType.IDENTIFIER)
        zone_a = cast(str, token.value)
        self.__expect(TokenType.DASH)
        token = self.__expect(TokenType.IDENTIFIER)
        zone_b = cast(str, token.value)

        if self.__peek().type == TokenType.LBRACKET:
            self.__advance()
            if self.__peek().type != TokenType.RBRACKET:
                self.__expect(TokenType.IDENTIFIER, "max_link_capacity")
                self.__expect(TokenType.EQUALS)
                max_link_capacity = cast(
                    int, self.__expect(TokenType.INTEGER).value
                )
            self.__expect(TokenType.RBRACKET)
        self.__expect(TokenType.NEWLINE)

        return Connection(zone_a, zone_b, max_link_capacity)

    def parse(self) -> Map:

        nb_drones = self.__parse_nb_drones()
        self.__expect(TokenType.NEWLINE)
        while self.__peek().type != TokenType.EOF:
            token = self.__expect(TokenType.IDENTIFIER)
            match token.value:
                case "start_hub":
                    self.zones.append(self.__parse_Zone("start_hub"))
                case "end_hub":
                    self.zones.append(self.__parse_Zone("end_hub"))
                case "hub":
                    self.zones.append(self.__parse_Zone())
                case "connection":
                    self.connections.append(self.__parse_connection())
                case _:
                    raise ParsingError(
                        token.location,
                        f"Unknown Identifier: '{token.value}'",
                    )
        return Map(nb_drones, self.zones, self.connections)


if __name__ == "__main__":
    from .lexer import Lexer
    from .errors import LexerError

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

    parser = Parser(tokens)
    map = parser.parse()
    print(map.nb_drones)
    print(*map.zones, sep="\n")
    print(*map.connections, sep="\n")
