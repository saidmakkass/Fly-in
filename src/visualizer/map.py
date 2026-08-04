import arcade
import math
from pyglet import shapes
from webcolors import name_to_rgb
from typing import Dict

from .converter import Graph
from .scaler import Scaler
from .constants import (
    WHITE_PIXEL,
    ZONE_RADIUS,
    ZONE_INNER_COLORS,
    LINE_WIDTH,
    RAINBOW,
)


class Zone(arcade.Sprite):
    back = shapes.Group(0)
    front = shapes.Group(1)

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        type: str,
        color: str,
        max_drones: int,
        scaler: Scaler,
        sprite_list: arcade.SpriteList,
        batch: shapes.Batch,
    ):
        self.name = name
        self.x = x
        self.y = y
        self.type = type
        self.max_drones = max_drones
        self.scaler = scaler
        self.sprite_list = sprite_list
        self.batch = batch
        self.shapes = self.get_shapes(color)
        self.count = 0
        super().__init__(scale=0)
        self.hit_box = arcade.hitbox.HitBox(
            [
                (
                    ZONE_RADIUS * math.cos(2 * math.pi * i / 12),
                    ZONE_RADIUS * math.sin(2 * math.pi * i / 12),
                )
                for i in range(12)
            ]
        )
        sprite_list.append(self)

    def __rainbow_shapes(self, *s):
        l3 = []
        arc_angle = 360 / len(RAINBOW)

        for i, color in enumerate(RAINBOW):
            l3.append(
                shapes.Arc(
                    0,
                    0,
                    ZONE_RADIUS,
                    angle=arc_angle,
                    start_angle=i * arc_angle,
                    thickness=LINE_WIDTH,
                    color=color,
                    group=self.front,
                    batch=self.batch,
                )
            )

        return s + tuple(l3)

    def get_shapes(self, color):
        try:
            border_color = name_to_rgb(color)
        except:
            border_color = (255, 255, 255)
        s1 = shapes.Circle(
            0,
            0,
            ZONE_RADIUS / 4,
            color=(255, 255, 255, 255),
            group=self.back,
            batch=self.batch,
        )
        s2 = shapes.Circle(
            0,
            0,
            ZONE_RADIUS,
            color=ZONE_INNER_COLORS[self.type],
            group=self.front,
            batch=self.batch,
        )

        if color and color.lower() == "rainbow":
            return self.__rainbow_shapes(s1, s2)

        s3 = shapes.Arc(
            0,
            0,
            ZONE_RADIUS,
            thickness=LINE_WIDTH,
            color=border_color,
            group=self.front,
            batch=self.batch,
        )
        return s1, s2, s3

    def resize(self):
        sx, sy = self.scaler.scale(self.x, self.y)
        self.center_x, self.center_y = sx, sy
        for shape in self.shapes:
            shape.x = sx
            shape.y = sy


class Connection(arcade.Sprite):
    type = "connection"

    def __init__(
        self,
        name: str,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        max_drones: int,
        scaler: Scaler,
        sprite_list: arcade.SpriteList,
        batch: shapes.Batch,
    ):
        super().__init__(WHITE_PIXEL)
        self.name = name
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.max_drones = max_drones
        self.scaler = scaler
        self.sprite_list = sprite_list
        self.batch = batch
        self.shape = self.get_shape()
        self.count = 0

        self.sprite_list.append(self)

    def get_shape(self):
        s1 = shapes.Line(
            self.start_x,
            self.start_y,
            self.end_x,
            self.end_y,
            LINE_WIDTH,
            self.color,
            batch=self.batch,
        )
        return s1

    def resize(self):
        x1, y1 = self.scaler.scale(self.start_x, self.start_y)
        x2, y2 = self.scaler.scale(self.end_x, self.end_y)
        dx = x2 - x1
        dy = y2 - y1

        self.center_x = (x1 + x2) / 2
        self.center_y = (y1 + y2) / 2
        self.scale = (math.hypot(dx, dy), 5)
        self.angle = -math.degrees(math.atan2(dy, dx))
        self.shape.x, self.shape.y = x1, y1
        self.shape.x2, self.shape.y2 = x2, y2


class Popup:
    def __init__(self, parent_group: shapes.Group):
        self.back = shapes.Group(0, parent_group)
        self.front = shapes.Group(1, parent_group)
        self.batch = shapes.Batch()
        self.background = shapes.Rectangle(
            0, 0, 0, 0, (45, 42, 64), group=self.back, batch=self.batch
        )
        self.active = False
        self.text = {
            "name": arcade.Text(
                "", 0, 0, font_size=14, group=self.front, batch=self.batch
            ),
            "type": arcade.Text(
                "", 0, 0, font_size=14, group=self.front, batch=self.batch
            ),
            "drones": arcade.Text(
                "", 0, 0, font_size=14, group=self.front, batch=self.batch
            ),
        }

    def update(self, x, y, spot: Zone | Connection):
        if not isinstance(spot, (Zone, Connection)):
            self.active = False
            return

        name = self.text["name"]
        type = self.text["type"]
        drones = self.text["drones"]

        name.text = f"Name: {spot.name}"
        type.text = f"Type: {spot.type}"
        drones.text = f"Drones: {spot.count}/{spot.max_drones}"

        max_width = max(t.content_width for t in self.text.values())

        name.x, name.y = x - max_width / 2, y + 14 * 6
        type.x, type.y = x - max_width / 2, y + 14 * 4
        drones.x, drones.y = x - max_width / 2, y + 14 * 2

        self.background.position = x - max_width / 2 - 14, y + 14
        self.background.width = max_width + 14 * 2
        self.background.height = 14 * 7

    def draw(self):
        if not self.active:
            return
        self.batch.draw()


class Map:
    back = shapes.Group(100)
    front = shapes.Group(101)

    def __init__(self, graph: Graph, scaler: Scaler, toggles: Dict[str, bool]):
        self.sprite_list = arcade.SpriteList(use_spatial_hash=True)
        self.batch = shapes.Batch()
        self.scaler = scaler
        self.toggles = toggles

        nodes, edges = graph
        self.spots = {}
        self.spots.update(
            {
                edge[0]: Connection(
                    *edge, scaler, self.sprite_list, self.batch
                )
                for edge in edges
            }
        )
        self.spots.update(
            {
                node[0]: Zone(*node, scaler, self.sprite_list, self.batch)
                for node in nodes
            }
        )
        self.popup = Popup(self.front)
        self.resize()

    def draw(self):
        self.resize()
        self.batch.draw()
        if self.toggles["popup"]:
            self.popup.draw()

    def resize(self):
        for spot in self.spots.values():
            spot.resize()

    def collision_check(self, mouse: arcade.Sprite):
        if not self.toggles["popup"]:
            return
        hit = arcade.check_for_collision_with_list(mouse, self.sprite_list)
        self.popup.active = bool(hit)
        if not hit:
            return
        hit.sort(key=lambda x: 0 if isinstance(x, Zone) else 1)
        self.popup.update(mouse.center_x, mouse.center_y, hit[0])
