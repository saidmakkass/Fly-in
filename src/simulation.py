from typing import Dict, Tuple
from heapq import heappop, heappush

from .map_parser import Map, Zone, Connection
from .classes import Graph, ReservationTable, Path


class Simulation:
    def __init__(self, map: Map):
        self.nb_drones = map.nb_drones
        self.start_hub = map.start_hub
        self.end_hub = map.end_hub
        self.graph = Graph(map.zones, map.connections, map.nb_drones)
        self.reservation_table = ReservationTable()

    def __get_path(self) -> Path:
        dist = {self.start_hub: 0}
        prev: Dict[Zone, Tuple[Zone, Connection]] = {}
        queue = [(0, 0, self.start_hub)]
        path = Path()

        while queue:
            turn, extra_cost, zone = heappop(queue)

            if zone is self.end_hub:
                path.reconstruct(
                    prev,
                    dist,
                    self.start_hub,
                    self.end_hub,
                    self.reservation_table,
                )
                break

            if len(self.graph.neighbors[zone]) == 1:
                break
            for neighbor, con in self.graph.neighbors[zone]:
                cost = 2 if neighbor.type == "restricted" else 1
                extra_cost = 0 if neighbor.type == "priority" else cost
                if (
                    not self.reservation_table.is_reserved(
                        turn + cost, neighbor
                    )
                ) and (not self.reservation_table.is_reserved(turn + 1, con)):
                    if turn + cost < dist.get(neighbor, float("inf")):
                        dist[neighbor] = turn + cost
                        prev[neighbor] = (zone, con)

                        heappush(queue, (turn + cost, extra_cost, neighbor))
                    elif con.zone_a is con.zone_b:
                        heappush(queue, (turn + 1, 3, neighbor))
        return path

    def run(self) -> Dict[int, Dict[int, Zone | Connection]]:
        output: Dict[int, Dict[int, Zone | Connection]] = {0: {}}
        for d in range(1, self.nb_drones + 1):
            output[0][d] = self.start_hub
            path = self.__get_path()
            if not path.path:
                raise ValueError("Error: No Path Found")
            for turn, spot in path.path.items():
                output.setdefault(turn, dict())[d] = spot
        return output
