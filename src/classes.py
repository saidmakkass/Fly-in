from typing import List, Dict, Tuple

from .map_parser import Zone, Connection


class Graph:
    def __init__(
        self, zones: List[Zone], cons: List[Connection], nb_drones: int
    ) -> None:
        self.zones = zones
        self.connections = cons
        self.nb_drones = nb_drones
        self.neighbors = self.__build_neighbors()

    def __build_neighbors(self) -> Dict[Zone, List[Tuple[Zone, Connection]]]:
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
    def __init__(self) -> None:
        self.__table: Dict[int, Dict[Zone | Connection, int]] = dict()

    def reserve(self, turn: int, spot: Zone | Connection) -> bool:
        if self.is_reserved(turn, spot):
            return False
        self.__table[turn][spot] += 1
        return True

    def is_reserved(self, turn: int, spot: Zone | Connection) -> bool:
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

    def __init__(self) -> None:
        self.path: Dict[int, Zone | Connection] = dict()

    def reconstruct(
        self,
        prev: Dict[Zone, Tuple[Zone, Connection]],
        dist: Dict[Zone, int],
        start: Zone,
        end: Zone,
        reservation_table: ReservationTable,
    ) -> None:
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
