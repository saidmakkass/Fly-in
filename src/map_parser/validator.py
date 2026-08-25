from typing import List, Set
from webcolors import name_to_rgb

from .classes import Map, Zone, UnvalidatedConnection, Connection, Location
from .errors import ValidationError

VALID_ZONE_TYPES = ["normal", "blocked", "restricted", "priority"]


class Validator:
    def __init__(
        self,
        nb_drones: int,
        zones: List[Zone],
        connections: List[UnvalidatedConnection],
    ):
        self.nb_drones = nb_drones
        self.zones = zones
        self.connections = connections
        self.zones_by_name: dict[str, Zone] = {}
        self.start_hub: Zone | None = None
        self.end_hub: Zone | None = None

    def __validate_zones(self) -> None:
        for zone in self.zones:
            if zone.kind == "start_hub":
                if self.start_hub is not None:
                    raise ValidationError(zone.location, "Extra start_hub")
                zone.max_drones = self.nb_drones
                self.start_hub = zone
            if zone.kind == "end_hub":
                if self.end_hub is not None:
                    raise ValidationError(zone.location, "Extra end_hub")
                zone.max_drones = self.nb_drones
                self.end_hub = zone
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
            try:
                if zone.color.lower() != "rainbow":
                    name_to_rgb(zone.color)
            except ValueError:
                raise ValidationError(zone.location, "Zone With Invalid Color")
            if zone.type not in VALID_ZONE_TYPES:
                raise ValidationError(zone.location, "Zone With Invalid Type")
            self.zones_by_name[zone.name] = zone
        if self.start_hub is None:
            raise ValidationError(None, "Missing start_hub")
        if self.end_hub is None:
            raise ValidationError(None, "Missing end_hub")

    def __validate_connections(self) -> List[Connection]:
        validated_connections = list()
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
            zone_a = self.zones_by_name[connection.zone_a]
            zone_b = self.zones_by_name[connection.zone_b]
            assert isinstance(zone_a.location, Location)
            assert isinstance(zone_b.location, Location)
            if connection.location.line < zone_a.location.line:
                raise ValidationError(
                    connection.location,
                    f"Connection Declared Before Hub '{zone_a.name}'",
                )
            elif connection.location.line < zone_b.location.line:
                raise ValidationError(
                    connection.location,
                    f"Connection Declared Before Hub '{zone_b.name}'",
                )
            validated_connections.append(
                Connection(
                    zone_a,
                    zone_b,
                    connection.location,
                    connection.max_link_capacity,
                )
            )
        return validated_connections

    def __validate_no_path(self, cons: List[Connection]) -> None:
        assert isinstance(self.start_hub, Zone)
        assert isinstance(self.end_hub, Zone)
        stack: List[Zone] = [self.start_hub]
        visited: Set[Zone] = {
            self.start_hub,
        }

        while stack:
            neighbors = []
            for con in cons:
                if stack[-1] in con:
                    neighbor = con.get_other(stack[-1])
                    if neighbor in visited or neighbor.type == "blocked":
                        continue
                    neighbors.append(neighbor)
            if not neighbors:
                stack.pop()
                continue
            for neighbor in neighbors:
                stack.append(neighbor)
                visited.add(neighbor)
        if self.end_hub not in visited:
            print(visited)
            raise ValidationError(self.end_hub.location, "No Path")

    def __validate_disconnected_graph(self, cons: List[Connection]) -> None:
        assert isinstance(self.start_hub, Zone)
        assert isinstance(self.end_hub, Zone)
        stack: List[Zone] = [self.start_hub]
        visited: Set[Zone] = {
            self.start_hub,
        }

        while stack:
            neighbors = []
            for con in cons:
                if stack[-1] in con:
                    neighbor = con.get_other(stack[-1])
                    if neighbor in visited:
                        continue
                    neighbors.append(neighbor)
            if not neighbors:
                stack.pop()
                continue
            for neighbor in neighbors:
                stack.append(neighbor)
                visited.add(neighbor)
        for zone in self.zones:
            if zone not in visited:
                raise ValidationError(zone.location, "Disconnected Graph")

    def __validate_graph(self, cons: List[Connection]) -> None:
        self.__validate_no_path(cons)
        self.__validate_disconnected_graph(cons)

    def validate(self) -> Map:
        self.__validate_zones()
        validated_connections = self.__validate_connections()
        self.__validate_graph(validated_connections)
        assert isinstance(self.start_hub, Zone)
        assert isinstance(self.end_hub, Zone)
        return Map(
            self.nb_drones,
            self.start_hub,
            self.end_hub,
            self.zones,
            validated_connections,
        )
