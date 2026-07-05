from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Set

from .lexer import Token, TokenType
from .errors import ParsingError


class ZoneType(Enum):
    NORMAL = auto()
    BLOCKED = auto()
    RESTRICTED = auto()
    PRIORITY = auto()


@dataclass(slots=True, frozen=True)
class Zone:
    name: str
    x: int
    y: int

    type: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1


@dataclass(slots=True, frozen=True)
class Connection:
    zone_a: Zone
    zone_b: Zone

    max_link_capacity: int = 1

    def __eq__(self, other) -> bool:
        if self.zone_a == other.zone_a and self.zone_b == other.zone_b:
            return True
        elif self.zone_b == other.zone_a and self.zone_a == other.zone_b:
            return True
        else:
            return False


@dataclass(slots=True, frozen=True)
class Map:
    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    hubs: Set[Zone]
    connections: Set[Connection]


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos: int = 0
        self.hubs: List[Zone] = list()
        self.hub_names: Set[str] = set()
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
                token.line,
                token.column,
                f"Expecting {type.name} Got {token.type.name}",
            )
        if value is not None:
            if token.value != value:
                raise ParsingError(
                    token.line,
                    token.column,
                    f"Expecting {value} Got {token.value}",
                )
        self.__advance()
        return token

    def __parse_nb_drones(self) -> int:
        self.__expect(TokenType.IDENTIFIER, "nb_drones")
        self.__expect(TokenType.COLON)
        return self.__expect(TokenType.INTEGER).value

    def __parse_hub(self) -> Zone:
        name: str
        x: int
        y: int
        zone_type: ZoneType = ZoneType.NORMAL
        color: str | None = None
        max_drones: int = 1

        self.__expect(TokenType.COLON)
        token = self.__expect(TokenType.IDENTIFIER)
        name = token.value
        if name in self.hub_names:
            raise ParsingError(
                token.line, token.column, f"Non Unique Hub Name: {name}"
            )
        if self.__peek().type == TokenType.DASH:
            self.__advance()
            x = self.__expect(TokenType.INTEGER).value * -1
        else:
            x = self.__expect(TokenType.INTEGER).value
        if self.__peek().type == TokenType.DASH:
            self.__advance()
            y = self.__expect(TokenType.INTEGER).value * -1
        else:
            y = self.__expect(TokenType.INTEGER).value
        if self.__peek().type == TokenType.LBRACKET:
            self.__advance()
            while self.__peek().type != TokenType.RBRACKET:
                match self.__expect(TokenType.IDENTIFIER).value:
                    case "zone":
                        self.__expect(TokenType.EQUALS)
                        zone_type = self.__expect(TokenType.IDENTIFIER).value
                    case "color":
                        self.__expect(TokenType.EQUALS)
                        color = self.__expect(TokenType.IDENTIFIER).value
                    case "max_drones":
                        self.__expect(TokenType.EQUALS)
                        max_drones = self.__expect(TokenType.INTEGER)
            self.__expect(TokenType.RBRACKET)
        self.__expect(TokenType.NEWLINE)
        return Zone(name, x, y, zone_type, color, max_drones)

    def __parse_connection(self) -> Connection:
        zone_a: Zone
        zone_b: Zone

        max_link_capacity: int = 1

        source_token = self.__peek(-1)
        self.__expect(TokenType.COLON)
        token = self.__expect(TokenType.IDENTIFIER)
        zone_a = token.value
        if zone_a not in self.hub_names:
            raise ParsingError(
                token.line, token.column, f"Unknown Hub: {zone_a}"
            )
        self.__expect(TokenType.DASH)
        token = self.__expect(TokenType.IDENTIFIER)
        zone_b = token.value
        if zone_b not in self.hub_names:
            raise ParsingError(
                token.line, token.column, f"Unknown Hub: {zone_b}"
            )

        if self.__peek().type == TokenType.LBRACKET:
            self.__advance()
            self.__expect(TokenType.IDENTIFIER, "max_link_capacity")
            self.__expect(TokenType.EQUALS)
            max_link_capacity = self.__expect(TokenType.INTEGER).value
            self.__expect(TokenType.RBRACKET)
        self.__expect(TokenType.NEWLINE)

        connection = Connection(zone_a, zone_b, max_link_capacity)
        if any(connection == c for c in self.connections):
            raise ParsingError(
                source_token.line, source_token.column, "Duplicated Connection"
            )
        return connection

    def parse(self) -> Map:
        nb_drones: int
        start_hub: Zone
        end_hub: Zone

        nb_drones = self.__parse_nb_drones()
        self.__expect(TokenType.NEWLINE)
        while self.__peek().type != TokenType.EOF:
            match self.__expect(TokenType.IDENTIFIER).value:
                case "start_hub":
                    start_hub = self.__parse_hub()
                    self.hub_names.add(start_hub.name)
                case "end_hub":
                    end_hub = self.__parse_hub()
                    self.hub_names.add(end_hub.name)
                case "hub":
                    hub = self.__parse_hub()
                    self.hubs.append(hub)
                    self.hub_names.add(hub.name)
                case "connection":
                    self.connections.append(self.__parse_connection())
        return Map(nb_drones, start_hub, end_hub, self.hubs, self.connections)


if __name__ == "__main__":
    from .lexer import Lexer

    with open("maps/challenger/01_the_impossible_dream.txt", "r") as f:
        file = f.read()
    lexer = Lexer(file)
    tokens = lexer.evaluate()
    parser = Parser(tokens)
    map = parser.parse()
    print(
        map.connections
    )
