from typing import Tuple, List

from ..map_parser import Map, Zone, Connection

Node = Tuple[str, int, int, str, str, int]
Edge = Tuple[int, int, int, int, int]
Graph = Tuple[List[Node], List[Edge], int]


class Converter:
    """
    Utility class to convert Fly-in related objects
    to objects used by Visualizer
    """

    @staticmethod
    def convert_map(map: Map) -> Graph:
        """
        Convert a Map object to a Graph.

        Args:
            map (Map): The Map object

        Returns:
            map (Graph): The map as a Graph
        """
        return (
            [Converter.convert_zone(z) for z in map.zones],
            [Converter.convert_connection(c) for c in map.connections],
            map.nb_drones,
        )

    @staticmethod
    def convert_zone(zone: Zone) -> Node:
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
    def convert_connection(connection: Connection) -> Edge:
        """
        Convert a Connection object to a Edge.

        Args:
            connection (Connection): The Connection object.

        Returns:
            connection (Edge): The connection as a Edge.
        """
        return (
            connection.zone_a.x,
            connection.zone_a.y,
            connection.zone_b.x,
            connection.zone_b.y,
            connection.max_link_capacity,
        )
