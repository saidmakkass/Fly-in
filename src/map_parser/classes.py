from typing import List, Any
from enum import Enum, auto
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Location:
    file_path: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"{self.file_path}:{self.line}:{self.column}"


class TokenType(Enum):
    IDENTIFIER = auto()
    INTEGER = auto()
    NAME = auto()

    COLON = auto()
    EQUALS = auto()
    DASH = auto()
    PLUS = auto()

    LBRACKET = auto()
    RBRACKET = auto()

    NEWLINE = auto()
    EOF = auto()


@dataclass(slots=True, frozen=True)
class Token:
    type: TokenType
    value: str | int | None

    location: Location

    def __repr__(self) -> str:
        return f"{self.location} - {self.type.name}" + (
            f"({self.value})" if self.value is not None else ""
        )


@dataclass(slots=True, frozen=True)
class Zone:
    kind: str
    name: str
    x: int
    y: int

    type: str = "normal"
    color: str | None = None
    max_drones: int = 1

    def __repr__(self) -> str:
        return (
            f"[{self.kind}] {self.name} ({self.x},{self.y}) [type={self.type} "
            + (f"color={self.color} " if self.color is not None else "")
            + f"max_drones={self.max_drones}]"
        )


@dataclass(slots=True, frozen=True)
class Connection:
    zone_a: str
    zone_b: str

    max_link_capacity: int = 1

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Connection):
            return NotImplemented
        connection_a = frozenset((self.zone_a, self.zone_b))
        connection_b = frozenset((other.zone_a, other.zone_b))
        return connection_a == connection_b

    def __hash__(self) -> int:
        return hash(frozenset((self.zone_a, self.zone_b)))

    def __repr__(self) -> str:
        return f"[{self.zone_a}]<-->[{self.zone_b}]"


@dataclass(slots=True)
class Map:
    nb_drones: int
    zones: List[Zone]
    connections: List[Connection]
