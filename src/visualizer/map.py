import arcade
from pyglet import shapes
from webcolors import name_to_rgb

from .converter import Graph, Node, Edge
from .viewport import Viewport
from .constants import ZONE_SIZE, LINE_WIDTH, ZONE_INNER_COLORS, RAINBOW


class Zone:

    back = shapes.Group(0)
    front = shapes.Group(1)

    def __init__(self, node: Node, batch: shapes.Batch, view_port: Viewport):
        self.name = node[0]
        self.x = node[1]
        self.y = node[2]
        self.type = node[3]
        self.color = node[4]
        self.max_drones = node[5]

        self.screen_x = 0
        self.screen_y = 0

        self.batch = batch
        self.view_port = view_port
        self.shapes = self.get_shapes()

    def scale(self, min_x, min_y, span_x, span_y, width, height, pad):
        frac_x = (self.x - min_x) / span_x
        frac_y = (self.y - min_y) / span_y
        self.screen_x, self.screen_y = (
            pad + frac_x * width,
            pad + frac_y * height,
        )

    def __rainbow_shapes(self, *s):
        l3 = []
        arc_angle = 360 / len(RAINBOW)

        for i, color in enumerate(RAINBOW):
            l3.append(
                shapes.Arc(
                    self.screen_x,
                    self.screen_y,
                    ZONE_SIZE,
                    angle=arc_angle,
                    start_angle=i * arc_angle,
                    thickness=LINE_WIDTH,
                    color=color,
                    group=self.front,
                    batch=self.batch,
                )
            )

        return s + tuple(l3)

    def get_shapes(self):
        try:
            border_color = name_to_rgb(self.color)
        except:
            border_color = (255, 255, 255)
        s1 = shapes.Circle(
            self.screen_x,
            self.screen_y,
            ZONE_SIZE / 4,
            color=(255, 255, 255, 255),
            group=self.back,
            batch=self.batch,
        )
        s2 = shapes.Circle(
            self.screen_x,
            self.screen_y,
            ZONE_SIZE,
            color=ZONE_INNER_COLORS[self.type],
            group=self.front,
            batch=self.batch,
        )

        if self.color.lower() == "rainbow":
            return self.__rainbow_shapes(s1, s2)

        s3 = shapes.Arc(
            self.screen_x,
            self.screen_y,
            ZONE_SIZE,
            thickness=LINE_WIDTH,
            color=border_color,
            group=self.front,
            batch=self.batch,
        )
        return s1, s2, s3

    def update(self):
        for shape in self.shapes:
            shape.x, shape.y = (
                self.screen_x * self.view_port.zoom + self.view_port.ox,
                self.screen_y * self.view_port.zoom + self.view_port.oy,
            )


class Connection:
    def __init__(self, edge: Edge, batch: shapes.Batch, view_port: Viewport):
        self.start_x = edge[0]
        self.start_y = edge[1]
        self.end_x = edge[2]
        self.end_y = edge[3]
        self.max_drones = edge[4]

        self.color = arcade.color.WHITE.rgb

        self.screen_start_x = 0
        self.screen_start_y = 0
        self.screen_end_x = 0
        self.screen_end_y = 0

        self.batch = batch
        self.view_port = view_port
        self.shapes = self.get_shapes()

    def scale(self, min_x, min_y, span_x, span_y, width, height, pad):
        frac_start_x = (self.start_x - min_x) / span_x
        frac_start_y = (self.start_y - min_y) / span_y
        frac_end_x = (self.end_x - min_x) / span_x
        frac_end_y = (self.end_y - min_y) / span_y
        self.screen_start_x, self.screen_start_y = (
            pad + frac_start_x * width,
            pad + frac_start_y * height,
        )
        self.screen_end_x, self.screen_end_y = (
            pad + frac_end_x * width,
            pad + frac_end_y * height,
        )

    def get_shapes(self):
        s1 = shapes.Line(
            self.screen_start_x,
            self.screen_start_y,
            self.screen_end_x,
            self.screen_end_y,
            LINE_WIDTH,
            self.color,
            batch=self.batch,
        )
        return (s1,)

    def update(self):
        for shape in self.shapes:
            shape.x, shape.y = (
                self.screen_start_x * self.view_port.zoom + self.view_port.ox,
                self.screen_start_y * self.view_port.zoom + self.view_port.oy,
            )
            shape.x2, shape.y2 = (
                self.screen_end_x * self.view_port.zoom + self.view_port.ox,
                self.screen_end_y * self.view_port.zoom + self.view_port.oy,
            )


class Map:
    def __init__(
        self, graph: Graph, width: int, height: int, view_port: Viewport
    ):
        self.batch = shapes.Batch()
        self.view_port = view_port

        self.zones = [Zone(n, self.batch, self.view_port) for n in graph[0]]
        self.connections = [
            Connection(c, self.batch, self.view_port) for c in graph[1]
        ]

        self.scale(width, height)

    def scale(self, width: int, height: int):
        min_x = min(z.x for z in self.zones)
        max_x = max(z.x for z in self.zones)
        min_y = min(z.y for z in self.zones)
        max_y = max(z.y for z in self.zones)

        span_x = (max_x - min_x) or 1.0
        span_y = (max_y - min_y) or 1.0

        pad = ZONE_SIZE * 2

        width = width - 2 * pad
        height = height - 2 * pad

        for zone in self.zones:
            zone.scale(min_x, min_y, span_x, span_y, width, height, pad)

        for con in self.connections:
            con.scale(min_x, min_y, span_x, span_y, width, height, pad)

    def draw(self):
        for zone in self.zones:
            zone.update()
        for con in self.connections:
            con.update()
        self.batch.draw()
