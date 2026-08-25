from typing import List, Any, Optional, Iterator
from enum import Enum, auto
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Location:
    file_path: str
    line: int
    column: int

    def __repr__(self) -> str:
        """Return a compact location string: file:line:column."""
        return f"{self.file_path}:{self.line}:{self.column}"


class TokenType(Enum):
    IDENTIFIER = auto()
    INTEGER = auto()
    NAME = auto()

    COLON = auto()
    EQUALS = auto()
    DASH = auto()
    PLUS = auto()
    SPACE = auto()

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
        """Return a short representation including location, type and value."""
        return f"{self.location} - {self.type.name}" + (
            f"({self.value})" if self.value is not None else ""
        )


@dataclass(slots=True, order=True)
class Zone:
    """Parsed zone metadata used for validation and simulation."""

    kind: str
    name: str
    x: int
    y: int

    location: Optional[Location] = None

    type: str = "normal"
    color: str = "white"
    max_drones: int = 1

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        """Return the zone name as its string representation."""
        return self.name

    def __repr__(self) -> str:
        return self.name


@dataclass(slots=True, frozen=True)
class Connection:
    """Validate Connection metadata"""

    zone_a: Zone
    zone_b: Zone

    location: Optional[Location] = None

    max_link_capacity: int = 1

    @property
    def name(self) -> str:
        """Return a human-readable name for the connection."""
        return f"{self.zone_a.name}-{self.zone_b.name}"

    @property
    def max_drones(self) -> int:
        """Return the maximum number of drones allowed on the connection."""
        return self.max_link_capacity

    @property
    def x(self) -> float:
        """Return the connection's midpoint X coordinate."""
        return (self.zone_a.x + self.zone_b.x) / 2

    @property
    def y(self) -> float:
        """Return the connection's midpoint Y coordinate."""
        return (self.zone_a.y + self.zone_b.y) / 2

    def get_other(self, zone: Zone) -> Zone:
        """Given one endpoint Zone, return the opposite Zone.

        Raises ValueError if the supplied zone is not part of the connection.
        """
        if zone not in self:
            raise ValueError(f"{zone.name} not in {self.name}")
        if zone is self.zone_a:
            return self.zone_b
        return self.zone_a

    def __contains__(self, item: Any) -> bool:
        """Return True if `item` is one of the connection endpoints."""
        if not isinstance(item, Zone):
            return False
        return item in (self.zone_a, self.zone_b)

    def __iter__(self) -> Iterator[Zone]:
        """Iterate over the two endpoint zones of the connection."""
        return iter((self.zone_a, self.zone_b))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


@dataclass(slots=True, frozen=True)
class UnvalidatedConnection:
    """Unvalidated Connection metadata"""

    zone_a: str
    zone_b: str

    location: Location

    max_link_capacity: int = 1

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, UnvalidatedConnection):
            connection_a = frozenset((self.zone_a, self.zone_b))
            connection_b = frozenset((other.zone_a, other.zone_b))
        elif isinstance(other, Connection):
            connection_a = frozenset((self.zone_a, self.zone_b))
            connection_b = frozenset((other.zone_a.name, other.zone_b.name))
        else:
            return NotImplemented
        return connection_a == connection_b


@dataclass(slots=True)
class Map:
    """Map object holding information for use in simulation"""

    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    zones: List[Zone]
    connections: List[Connection]

    def __repr__(self) -> str:
        zones = "\n".join([f"{z}" for z in self.zones])
        cons = "\n".join([f"{c}" for c in self.connections])
        return (
            f"nb_drones = {self.nb_drones}\n"
            "Zones:\n"
            f"{zones}\n"
            "Connections:\n"
            f"{cons}"
        )
