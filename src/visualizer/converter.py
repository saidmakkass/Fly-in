from typing import Tuple, List, Dict

from ..map_parser import Map, Zone, Connection

Node = Tuple[str, int, int, str, str, int]
Edge = Tuple[str, int, int, int, int, int]
Graph = Tuple[List[Node], List[Edge]]
Turn = Dict[int, Node | Edge]
Turns = Dict[int, Turn]


class Converter:
    """
    Utility class to convert Fly-in related objects
    to objects used by Visualizer

    This is an intermediary step done before starting the visualizer
    and should be reimplemented by anyone wishing to use this exact
    visualizer in their own project
    """

    @staticmethod
    def convert_graph(map: Map) -> Graph:
        """
        Convert a Map object to a Graph.

        Args:
            map (Map): The Map object

        Returns:
            map (Graph): The map as a Graph
        """
        return (
            [Converter.convert_node(z) for z in map.zones],
            [Converter.convert_edge(c) for c in map.connections],
        )

    @staticmethod
    def convert_node(zone: Zone) -> Node:
        """
        Convert a Zone object to a Node.

        Args:
            zone (Zone): The Zone object.

        Returns:
            zone (Node): The zone as a Node.
        """
        return (
            zone.name,
            zone.x,
            zone.y,
            zone.type,
            zone.color,
            zone.max_drones,
        )

    @staticmethod
    def convert_edge(connection: Connection) -> Edge:
        """
        Convert a Connection object to a Edge.

        Args:
            connection (Connection): The Connection object.

        Returns:
            connection (Edge): The connection as a Edge.
        """
        return (
            connection.name,
            connection.zone_a.x,
            connection.zone_a.y,
            connection.zone_b.x,
            connection.zone_b.y,
            connection.max_link_capacity,
        )

    @staticmethod
    def convert_turns(turns: Dict[int, Dict[int, Zone | Connection]]) -> Turns:
        """
        Convert simulation output to a standard format Turns.

        The output should include turn 0,
        And the Node/Edge a drone is at at any given turn (waiting or arriving)
        Args:
            turns (Dict): The simulation output.

        Returns:
            turns (Turns): The output in a standard format.
        """
        nb_drones = len(turns[0])
        output = {
            turn: {
                drone: (
                    Converter.convert_node(spot)
                    if isinstance(spot, Zone)
                    else Converter.convert_edge(spot)
                )
                for drone, spot in move.items()
            }
            for turn, move in turns.items()
        }
        for turn in output:
            for drone in range(1, nb_drones + 1):
                if drone not in output[turn]:
                    output[turn][drone] = output[turn - 1][drone]
        return output
