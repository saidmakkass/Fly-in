import arcade
from webcolors import name_to_hex

from .converter import Graph, Node, Edge
from .viewport import Viewport

ZONE_SIZE = 80
BORDER_WIDTH = 100

ZONE_INNER_COLORS = {
    "normal": arcade.types.Color(128, 128, 128, 128),
    "restricted": arcade.types.Color(255, 255, 0, 128),
    "priority": arcade.types.Color(0, 255, 255, 128),
    "blocked": arcade.types.Color(255, 0, 0, 128),
}


class Zone:
    def __init__(self, node: Node):
        self.name = node[0]
        self.x = node[1]
        self.y = node[2]
        self.type = node[3]
        self.color = node[4]
        self.max_drones = node[5]

        self.scaled_x = 0.0
        self.scaled_y = 0.0

        self.screen_x = 0.0
        self.screen_y = 0.0

    def get_shapes(self):

        try:
            border_color = arcade.types.Color.from_hex_string(
                name_to_hex(self.color)
            )
        except ValueError:
            border_color = arcade.types.Color(0, 0, 0, 128)

        s1 = arcade.shape_list.create_ellipse_filled(
            self.screen_x,
            self.screen_y,
            ZONE_SIZE / 3,
            ZONE_SIZE / 3,
            arcade.color.WHITE,
        )
        s2 = arcade.shape_list.create_ellipse_filled(
            self.screen_x,
            self.screen_y,
            ZONE_SIZE,
            ZONE_SIZE,
            ZONE_INNER_COLORS[self.type],
        )
        s3 = arcade.shape_list.create_ellipse_outline(
            self.screen_x, self.screen_y, ZONE_SIZE, ZONE_SIZE, border_color
        )
        return (s1, s2, s3)


class Connection:
    def __init__(self, edge: Edge):
        self.start_x = edge[0]
        self.start_y = edge[1]
        self.end_x = edge[2]
        self.end_y = edge[3]
        self.max_drones = edge[4]

        self.scaled_start_x = 0.0
        self.scaled_start_y = 0.0
        self.scaled_end_x = 0.0
        self.scaled_end_y = 0.0


class Map:
    def __init__(
        self, graph: Graph, width: int, height: int, view_port: Viewport
    ):
        self.zones = [Zone(n) for n in graph[0]]
        self.connections = [Connection(c) for c in graph[1]]
        self.view_port = view_port

        self.scale(width, height, 40)

        self.shape_list = self.__build_shape_list()

    def __build_shape_list(self):
        shape_list = arcade.shape_list.ShapeElementList()
        # for con in self.connections:
        #     shape_list.append(con.shape)
        for zone in self.zones:
            for shape in zone.get_shapes():
                shape_list.append(shape)
        return shape_list

    def scale(self, width: int, height: int, pad: float):
        min_x = min(z.x for z in self.zones)
        max_x = max(z.x for z in self.zones)
        min_y = min(z.y for z in self.zones)
        max_y = max(z.y for z in self.zones)

        span_x = (max_x - min_x) or 1.0
        span_y = (max_y - min_y) or 1.0

        width = width - 2 * pad
        height = height - 2 * pad

        for zone in self.zones:
            frac_x = (zone.x - min_x) / span_x
            zone.scaled_x = pad + frac_x * width
            frac_y = (zone.y - min_y) / span_y
            zone.scaled_y = pad + frac_y * height
            zone.screen_x, zone.screen_y = self.view_port.world_to_screen(
                zone.scaled_x, zone.scaled_y
            )
        # for con in self.connections:
        #     frac_x = (con.start_x - min_x)

    def draw(self):
        self.shape_list.draw()

    def move(self, dx: float, dy: float):
        pass
