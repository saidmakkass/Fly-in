from typing import Tuple, List

from ..map_parser import Map, Zone, Connection


class Converter:
    """Utility class to convert Fly-in related objects to tuples"""

    @staticmethod
    def convert_map(
        map: Map,
    ) -> Tuple[
        List[Tuple[str, int, int, str, str, int]],
        List[Tuple[int, int, int, int, int]],
        int,
    ]:
        """
        Convert a Map object to a tuple.

        Args:
            map (Map): The Map object

        Returns:
            map (tuple): The map as a tuple
        """
        return (
            [Converter.convert_zone(z) for z in map.zones],
            [Converter.convert_connection(c) for c in map.connections],
            map.nb_drones
        )

    @staticmethod
    def convert_zone(zone: Zone) -> Tuple[str, int, int, str, str, int]:
        """
        Convert a Zone object to a tuple.

        Args:
            zone (Zone): The Zone object.

        Returns:
            zone (tuple): The zone as a tuple.
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
    def convert_connection(
        connection: Connection,
    ) -> Tuple[int, int, int, int, int]:
        """
        Convert a Connection object to a tuple.

        Args:
            connection (Connection): The Connection object.

        Returns:
            connection (tuple): The connection as a tuple.
        """
        return (
            connection.zone_a.x,
            connection.zone_a.y,
            connection.zone_b.x,
            connection.zone_b.y,
            connection.max_link_capacity,
        )
