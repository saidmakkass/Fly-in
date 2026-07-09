from typing import List, Tuple, cast

from .classes import Token, TokenType, Zone, UnvalidatedConnection, Location
from .errors import ParsingError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos: int = 0
        self.zones: List[Zone] = list()
        self.connections: List[UnvalidatedConnection] = list()

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
        self.__expect(TokenType.SPACE)
        if self.__peek().type == TokenType.PLUS:
            self.__advance()
        token = self.__expect(TokenType.INTEGER)
        nb_drones = cast(int, token.value)
        if nb_drones == 0:
            raise ParsingError(token.location, "Non Positive Integer")
        return nb_drones

    def __parse_Zone(self, zone_location: Location, kind: str = "hub") -> Zone:
        name: str
        x: int
        y: int
        zone_type: str = "normal"
        color: str | None = None
        max_drones: int = 1
        parsed_metadata = set()

        self.__expect(TokenType.COLON)
        self.__expect(TokenType.SPACE)
        token = self.__expect(TokenType.NAME)
        name = cast(str, token.value)
        self.__expect(TokenType.SPACE)
        if self.__peek().type == TokenType.DASH:
            self.__advance()
            x = cast(int, self.__expect(TokenType.INTEGER).value) * -1
        else:
            if self.__peek().type == TokenType.PLUS:
                self.__advance()
            x = cast(int, self.__expect(TokenType.INTEGER).value)
        self.__expect(TokenType.SPACE)
        if self.__peek().type == TokenType.DASH:
            self.__advance()
            y = cast(int, self.__expect(TokenType.INTEGER).value) * -1
        else:
            if self.__peek().type == TokenType.PLUS:
                self.__advance()
            y = cast(int, self.__expect(TokenType.INTEGER).value)
        self.__expect(TokenType.SPACE)
        if self.__peek().type == TokenType.LBRACKET:
            self.__advance()
            while self.__peek().type != TokenType.RBRACKET:
                if self.__peek().type == TokenType.SPACE:
                    self.__advance()
                token = self.__expect(TokenType.IDENTIFIER)
                match token.value:
                    case "zone":
                        if "zone" in parsed_metadata:
                            raise ParsingError(
                                token.location, "Duplicated key"
                            )
                        parsed_metadata.add("zone")
                        if self.__peek().type == TokenType.SPACE:
                            self.__advance()
                        self.__expect(TokenType.EQUALS)
                        if self.__peek().type == TokenType.SPACE:
                            self.__advance()
                        token = self.__expect(TokenType.IDENTIFIER)
                        zone_type = cast(str, token.value)
                    case "color":
                        if "color" in parsed_metadata:
                            raise ParsingError(
                                token.location, "Duplicated key"
                            )
                        parsed_metadata.add("color")
                        if self.__peek().type == TokenType.SPACE:
                            self.__advance()
                        self.__expect(TokenType.EQUALS)
                        if self.__peek().type == TokenType.SPACE:
                            self.__advance()
                        color = cast(
                            str, self.__expect(TokenType.IDENTIFIER).value
                        )
                    case "max_drones":
                        if "max_drones" in parsed_metadata:
                            raise ParsingError(
                                token.location, "Duplicated key"
                            )
                        parsed_metadata.add("max_drones")
                        if self.__peek().type == TokenType.SPACE:
                            self.__advance()
                        self.__expect(TokenType.EQUALS)
                        if self.__peek().type == TokenType.SPACE:
                            self.__advance()
                        if self.__peek().type == TokenType.PLUS:
                            self.__advance()
                        token = self.__expect(TokenType.INTEGER)
                        max_drones = cast(int, token.value)
                        if max_drones == 0:
                            raise ParsingError(
                                token.location, "Non Positive Integer"
                            )
                    case _:
                        raise ParsingError(
                            token.location,
                            f"Unknown Key '{token.value}'",
                        )
                if self.__peek().type == TokenType.SPACE:
                    self.__advance()
            self.__expect(TokenType.RBRACKET)
        if self.__peek().type == TokenType.SPACE:
            self.__advance()
        self.__expect(TokenType.NEWLINE).location.line
        return Zone(
            kind, name, x, y, zone_location, zone_type, color, max_drones
        )

    def __parse_connection(
        self, connection_location: Location
    ) -> UnvalidatedConnection:
        zone_a: str
        zone_b: str
        max_link_capacity: int = 1

        self.__expect(TokenType.COLON)
        self.__expect(TokenType.SPACE)
        token = self.__expect(TokenType.NAME)
        zone_a = cast(str, token.value)
        self.__expect(TokenType.DASH)
        token = self.__expect(TokenType.NAME)
        zone_b = cast(str, token.value)

        if self.__peek().type == TokenType.SPACE:
            self.__advance()
        if self.__peek().type == TokenType.LBRACKET:
            self.__advance()
            if self.__peek().type == TokenType.SPACE:
                self.__advance()
            if self.__peek().type != TokenType.RBRACKET:
                self.__expect(TokenType.IDENTIFIER, "max_link_capacity")
                if self.__peek().type == TokenType.SPACE:
                    self.__advance()
                self.__expect(TokenType.EQUALS)
                if self.__peek().type == TokenType.SPACE:
                    self.__advance()
                if self.__peek().type == TokenType.PLUS:
                    self.__advance()
                token = self.__expect(TokenType.INTEGER)
                max_link_capacity = cast(int, token.value)
                if max_link_capacity == 0:
                    raise ParsingError(token.location, "Non Positive Integer")
            if self.__peek().type == TokenType.SPACE:
                self.__advance()
            self.__expect(TokenType.RBRACKET)
        if self.__peek().type == TokenType.SPACE:
            self.__advance()
        self.__expect(TokenType.NEWLINE)

        return UnvalidatedConnection(
            zone_a, zone_b, connection_location, max_link_capacity
        )

    def parse(self) -> Tuple[int, List[Zone], List[UnvalidatedConnection]]:

        nb_drones = self.__parse_nb_drones()
        self.__expect(TokenType.NEWLINE)
        while self.__peek().type != TokenType.EOF:
            token = self.__expect(TokenType.IDENTIFIER)
            match token.value:
                case "start_hub":
                    self.zones.append(
                        self.__parse_Zone(token.location, "start_hub")
                    )
                case "end_hub":
                    self.zones.append(
                        self.__parse_Zone(token.location, "end_hub")
                    )
                case "hub":
                    self.zones.append(self.__parse_Zone(token.location))
                case "connection":
                    self.connections.append(
                        self.__parse_connection(token.location)
                    )
                case _:
                    raise ParsingError(
                        token.location,
                        f"Unknown Identifier: '{token.value}'",
                    )
        return (nb_drones, self.zones, self.connections)
