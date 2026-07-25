from arcade import (
    Window,
    draw_lines,
    draw_circle_filled,
    key,
    load_texture,
    draw_texture_rect,
)
from arcade.types import Color
import arcade.color

from importlib.resources import files

from ..map_parser import Map

WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280
WINDOW_TITLE = "Fly-in"


LINE_WIDTH = 5
MARGIN = 0.8
ZOOM_SPEED = 1.2


class SimulationWindow(Window):
    def __init__(self, map: Map):
        super().__init__(
            WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True
        )
        self.center_window()

        self.hold = {
            "right": False,
            "left": False,
            "up": False,
            "down": False,
        }

        self.map = map

        self.min_x = min(z.x for z in map.zones)
        self.max_x = max(z.x for z in map.zones)
        self.min_y = min(z.y for z in map.zones)
        self.max_y = max(z.y for z in map.zones)

        self.__calculate_viewport()
        self.__load__assets()

    def __load__assets(self):
        assets_dir = files(__package__) / "assets"

        self.background = load_texture(assets_dir / "background.jpg")

    def __calculate_viewport(self):
        graph_width = self.max_x - self.min_x
        graph_height = self.max_y - self.min_y

        zoom_x = self.width / graph_width
        zoom_y = self.height / graph_height

        self.zoom = min(zoom_x, zoom_y) * MARGIN
        self.min_zoom = self.zoom
        self.max_zoom = self.zoom * 5
        self.zoom_step = self.zoom / 5

        self.max_cell_size = self.zoom / 2 * MARGIN

        graph_cx = (self.min_x + self.max_x) / 2
        graph_cy = (self.min_y + self.max_y) / 2

        screen_cx = self.width / 2
        screen_cy = self.height / 2

        self.ox = screen_cx - graph_cx * self.zoom
        self.oy = screen_cy - graph_cy * self.zoom

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.__calculate_viewport()

    def world_to_screen(self, x, y):
        return (
            x * self.zoom + self.ox,
            y * self.zoom + self.oy,
        )

    def screen_to_world(self, x, y):
        return (
            (x - self.ox) / self.zoom,
            (y - self.oy) / self.zoom,
        )

    def move_viewport(self):
        if self.hold["zoom_in"]:
            self.zoom += ZOOM_SPEED
            self.zoom = min(self.zoom, self.max_zoom)
            print(self.zoom)
        if self.hold["zoom_out"]:
            self.zoom -= ZOOM_SPEED
            self.zoom = max(self.zoom, self.min_zoom)
            print(self.zoom)

    def __draw_cons(self):
        point_list = list()
        for con in self.map.connections:
            point_list.append(self.world_to_screen(con.zone_a.x, con.zone_a.y))
            point_list.append(self.world_to_screen(con.zone_b.x, con.zone_b.y))
        draw_lines(point_list, arcade.color.WHITE, LINE_WIDTH)

    def __draw_zones(self):
        cell_size = min(self.zoom, self.max_cell_size)
        for zone in self.map.zones:
            sx, sy = self.world_to_screen(zone.x, zone.y)
            draw_circle_filled(sx, sy, cell_size, arcade.color.RED)

    def draw_map(self):
        self.__draw_cons()
        self.__draw_zones()

    def on_draw(self):
        self.clear()
        draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, self.width, self.height),
        )
        self.draw_map()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.RIGHT or symbol == key.D:
            self.hold["right"] = True
        elif symbol == key.LEFT or symbol == key.A:
            self.hold["left"] = True
        elif symbol == key.UP or symbol == key.W:
            self.hold["up"] = True
        elif symbol == key.DOWN or symbol == key.S:
            self.hold["down"] = True
        elif symbol == key.EQUAL:
            self.zoom += self.zoom_step
            self.zoom = min(self.zoom, self.max_zoom)
            print(self.zoom)
        elif symbol == key.MINUS:
            self.zoom -= self.zoom_step
            self.zoom = max(self.zoom, self.min_zoom)
            print(self.zoom)
        elif symbol == key.R:
            self.__calculate_viewport()
        elif symbol == key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.RIGHT or symbol == key.D:
            self.hold["right"] = False
        elif symbol == key.LEFT or symbol == key.A:
            self.hold["left"] = False
        elif symbol == key.UP or symbol == key.W:
            self.hold["up"] = False
        elif symbol == key.DOWN or symbol == key.S:
            self.hold["down"] = False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y:
            wx, wy = self.screen_to_world(x, y)
            self.zoom += scroll_y * self.zoom_step
            self.zoom = max(self.zoom, self.min_zoom)
            self.zoom = min(self.zoom, self.max_zoom)
            self.ox = x - wx * self.zoom
            self.oy = y - wy * self.zoom


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.ox += dx
        self.oy += dy
