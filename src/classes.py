from typing import List, Dict, Tuple

from .map_parser import Zone, Connection


class Graph:
    """Graph of zones and connections with neighbor lookup.

    Attributes:
        zones: List of zones in the graph.
        connections: List of connections between zones.
        nb_drones: Number of drones in the simulation.
        neighbors: Mapping from a zone to its neighbor zones and connection.
    """
    def __init__(
        self, zones: List[Zone], cons: List[Connection], nb_drones: int
    ) -> None:
        self.zones = zones
        self.connections = cons
        self.nb_drones = nb_drones
        self.neighbors = self.__build_neighbors()

    def __build_neighbors(self) -> Dict[Zone, List[Tuple[Zone, Connection]]]:
        """Build neighbor mapping for each zone."""
        output: Dict[Zone, List[Tuple[Zone, Connection]]] = dict()
        for zone in self.zones:
            neighbors = output.setdefault(zone, list())
            for con in self.connections:
                if zone in con:
                    neighbor = con.get_other(zone)
                    if neighbor.type != "blocked":
                        neighbors.append((neighbor, con))
        for zone, neighbors in output.items():
            wait_con = Connection(zone, zone, max_link_capacity=self.nb_drones)
            neighbors.append((zone, wait_con))
        return output


class ReservationTable:
    """Simple reservation table to track occupancy per turn and spot.

    The table maps turns to counts of reservations for each zone/connection.
    """
    def __init__(self) -> None:
        """Initialize an empty reservation table."""
        self.__table: Dict[int, Dict[Zone | Connection, int]] = dict()

    def reserve(self, turn: int, spot: Zone | Connection) -> bool:
        """Reserve `spot` at `turn` if capacity allows.

        Returns True on success, False if already fully reserved.
        """
        if self.is_reserved(turn, spot):
            return False
        self.__table[turn][spot] += 1
        return True

    def is_reserved(self, turn: int, spot: Zone | Connection) -> bool:
        """Return True if `spot` is at or above its max capacity on `turn`."""
        res = self.__table.setdefault(turn, dict()).setdefault(spot, 0)
        if res >= spot.max_drones:
            return True
        return False

    def __repr__(self) -> str:
        lines = [f"{self.__class__.__name__}("]
        for turn in sorted(self.__table):
            lines.append(f"  {turn}:")
            for obj, reservations in self.__table[turn].items():
                lines.append(f"    {obj.name}: {reservations}")
        lines.append(")")
        return "\n".join(lines)


class Path:
    """The generated Path of a Drone"""
    def __init__(self) -> None:
        """Create an empty path mapping."""
        self.path: Dict[int, Zone | Connection] = dict()

    def reconstruct(
        self,
        prev: Dict[Zone, Tuple[Zone, Connection]],
        dist: Dict[Zone, int],
        start: Zone,
        end: Zone,
        reservation_table: ReservationTable,
    ) -> None:
        """Reconstruct the path from `prev`/`dist` and reserve spots.

        Updates `self.path` with a mapping turn -> Zone|Connection and
        populates the `reservation_table` accordingly.
        """
        path: Dict[int, Zone | Connection] = dict()
        cur = end
        while cur is not start:
            turn = dist[cur]
            path[turn] = cur
            reservation_table.reserve(turn, cur)
            zone, con = prev[cur]
            waits = (
                dist[cur] - dist[zone] - (1 if cur.type == "restricted" else 0)
            )
            for w in range(1, waits):
                reservation_table.reserve(dist[zone] + w, zone)
            if cur.type == "restricted":
                reservation_table.reserve(turn - 1, con)
                path[turn - 1] = con
            reservation_table.reserve(turn, con)
            cur = zone
        self.path = dict(sorted(path.items()))
