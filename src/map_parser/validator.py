from typing import List

from .classes import Map, Zone, Connection
from .errors import ValidationError

VALID_ZONE_TYPES = ["normal", "blocked", "restricted", "priority"]

VALID_COLORS = [
    None,
    "brown",
    "gold",
    "orange",
    "blue",
    "crimson",
    "lime",
    "black",
    "rainbow",
    "green",
    "yellow",
    "maroon",
    "darkred",
    "red",
    "purple",
    "violet",
    "cyan",
    "magenta",
]


class Validator:
    def __init__(
        self, nb_drones: int, zones: List[Zone], connections: List[Connection]
    ):
        self.nb_drones = nb_drones
        self.zones = zones
        self.connections = connections
        self.zones_by_name: dict[str, Zone] = {}

    def __validate_zones(self) -> None:
        start_zone = 0
        end_zone = 0
        for zone in self.zones:
            if zone.kind == "start_hub":
                start_zone += 1
            if zone.kind == "end_hub":
                end_zone += 1
            if start_zone > 1:
                raise ValidationError(zone.location, "Extra start_hub")
            if end_zone > 1:
                raise ValidationError(zone.location, "Extra end_hub")
            if zone.name in self.zones_by_name:
                raise ValidationError(
                    zone.location, "Zone With Duplicated Name"
                )
            if any(
                (zone.x, zone.y) == (z.x, z.y)
                for z in self.zones_by_name.values()
            ):
                raise ValidationError(
                    zone.location, "Zone Overlaps A Previous One"
                )
            if zone.color not in VALID_COLORS:
                raise ValidationError(zone.location, "Zone With Invalid Color")
            if zone.type not in VALID_ZONE_TYPES:
                raise ValidationError(zone.location, "Zone With Invalid Type")
            self.zones_by_name[zone.name] = zone
        if start_zone < 1:
            raise ValidationError(None, "Missing start_hub")
        if end_zone < 1:
            raise ValidationError(None, "Missing end_hub")

    def __validate_connections(self) -> None:
        validated_connections = set()
        for connection in self.connections:
            if connection in validated_connections:
                raise ValidationError(
                    connection.location, "Duplicated Connection"
                )
            if connection.zone_a == connection.zone_b:
                raise ValidationError(connection.location, "Self Connection")
            if connection.zone_a not in self.zones_by_name:
                raise ValidationError(
                    connection.location,
                    f"Connection With Unknown Zone '{connection.zone_a}'",
                )
            if connection.zone_b not in self.zones_by_name:
                raise ValidationError(
                    connection.location,
                    f"Connection With Unknown Zone '{connection.zone_b}'",
                )
            validated_connections.add(connection)

    def validate(self) -> Map:
        self.__validate_zones()
        self.__validate_connections()

        return Map(self.nb_drones, self.zones, self.connections)
