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

from webcolors import name_to_hex
from importlib.resources import files
from typing import Dict

from ..map_parser import Map, Zone, Connection

WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280
WINDOW_TITLE = "Fly-in"


LINE_WIDTH = 5
MARGIN = 0.8
ZOOM_SPEED = 1.2

RAINBOW_COLORS = (
    arcade.color.ELECTRIC_CRIMSON,
    arcade.color.FLUORESCENT_ORANGE,
    arcade.color.ELECTRIC_YELLOW,
    arcade.color.ELECTRIC_GREEN,
    arcade.color.ELECTRIC_CYAN,
    arcade.color.MEDIUM_ELECTRIC_BLUE,
    arcade.color.ELECTRIC_INDIGO,
    arcade.color.ELECTRIC_PURPLE,
)


class SimulationWindow(Window):
    def __init__(self, map: Map, turns: Dict[int, Dict[int, Zone | Connection]]):
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
        self.flags = {
            "hud": False,
            "can_drag": False,
            "can_resize_hud": False,
            "pause_button": False
        }

        self.map = map
        self.turns = turns

        self.min_x = min(z.x for z in map.zones)
        self.max_x = max(z.x for z in map.zones)
        self.min_y = min(z.y for z in map.zones)
        self.max_y = max(z.y for z in map.zones)

        self.zone_background_colors = {
            "normal": Color(128,128,128,128),
            "restricted": Color(255,255,0,128),
            "priority": Color(0,255,255,128),
            "blocked": Color(255,0,0,128),
        }

        self.hud_background_color = Color(45, 42, 64, 225)
        self.hud_height = 0
        self.target_hud_height = 0
        self.hud_bar_size = 5
        self.button_size = 50
        self.controls_offset = 50

        self.turn = 0
        self.max_turn = len(self.turns) - 1
        self.turn_text = arcade.Text(f"Turn: {self.turn}", 0, 0, arcade.color.WHITE, 22)
        self.drone_size = 20

        self.__calculate_viewport()
        self.__load__assets()

    def __load__assets(self):
        assets_dir = files(__package__) / "assets"

        self.background = load_texture(assets_dir / "background.jpg")
        controls_sheet = arcade.SpriteSheet(assets_dir / "controls.png")
        # from left of texture to left of next texture = 795
        # from top of texture to top of next one = 709
        # width of texture = 446
        # margin left/right 349
        # margin up/down 263
        textures = controls_sheet.get_texture_grid(
            (446, 446),
            7,
            35,
            (349/2, 349/2, 263/2, 263/2)
        )
        self.play_button = textures[1]
        self.pause_button = textures[2]
        self.prev_button = textures[3]
        self.next_button = textures[4]
        self.reset_button = textures[22]


    def __calculate_viewport(self):
        self.max_zone_size = 40
        self.zoom = 100

        self.min_zoom = self.zoom
        self.max_zoom = self.zoom * 5
        self.zoom_step = self.zoom / 5

        self.ox = self.max_zone_size * 2 - self.map.start_hub.x * self.zoom
        self.oy = self.height - self.max_y * self.zoom - self.max_zone_size

    def on_resize(self, width: int, height: int):
        self.__calculate_viewport()
        if self.target_hud_height:
            self.target_hud_height = height / 4

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
            # print(self.zoom)
        if self.hold["zoom_out"]:
            self.zoom -= ZOOM_SPEED
            self.zoom = max(self.zoom, self.min_zoom)
            # print(self.zoom)

    def __draw_cons(self):
        point_list = list()
        for con in self.map.connections:
            con_color = arcade.color.WHITE
            if any(True if spot is con else False for spot in self.turns[self.turn].values()):
                con_color = arcade.color.ORANGE_PEEL
            asx, asy = self.world_to_screen(con.zone_a.x, con.zone_a.y)
            bsx, bsy = self.world_to_screen(con.zone_b.x, con.zone_b.y)
            arcade.draw_line(asx, asy, bsx, bsy, con_color, LINE_WIDTH)
        #     point_list.append(self.world_to_screen(con.zone_a.x, con.zone_a.y))
        #     point_list.append(self.world_to_screen(con.zone_b.x, con.zone_b.y))
        # draw_lines(point_list, arcade.color.WHITE, LINE_WIDTH)

    def __draw_zones(self):
        zone_size = min(self.zoom, self.max_zone_size)
        for zone in self.map.zones:
            try:
                border_color = Color.from_hex_string(name_to_hex(zone.color))
            except ValueError:
                border_color = Color(0,0,0, 0)
            background_color =  self.zone_background_colors[zone.type]
            sx, sy = self.world_to_screen(zone.x, zone.y)
            draw_circle_filled(sx, sy, zone_size / 3, arcade.color.WHITE)
            draw_circle_filled(sx, sy, zone_size, background_color)
            arcade.draw_circle_outline(sx, sy, zone_size, border_color, LINE_WIDTH)

    def __draw_hud(self):
        arcade.draw_rect_filled(
            arcade.rect.Viewport(0, 0, self.width, self.hud_height),
            self.hud_background_color
        )
        arcade.draw_line(0, self.hud_height, self.width, self.hud_height, arcade.color.BLACK, self.hud_bar_size * 2)
        self.turn_text.text = f"Turn: {self.turn}"
        self.turn_text.x, self.turn_text.y = 40, self.hud_height - 40
        self.turn_text.draw()

        if not self.flags["hud"]:
            return

        i = 0
        arcade.draw_texture_rect(self.reset_button, arcade.rect.Viewport(self.controls_offset + self.button_size + (i := i + self.button_size), 10, self.button_size, self.button_size))
        arcade.draw_texture_rect(self.prev_button, arcade.rect.Viewport(self.controls_offset + self.button_size + (i := i + self.button_size), 10, self.button_size, self.button_size))
        play_pause_rect = arcade.rect.Viewport(self.controls_offset + self.button_size + (i := i + self.button_size), 10, self.button_size, self.button_size)
        if self.flags["pause_button"]:
            arcade.draw_texture_rect(self.pause_button, play_pause_rect)
        else:
            arcade.draw_texture_rect(self.play_button, play_pause_rect)
        arcade.draw_texture_rect(self.next_button, arcade.rect.Viewport(self.controls_offset + self.button_size + (i := i + self.button_size), 10, self.button_size, self.button_size))

    def draw_map(self):
        self.__draw_cons()
        self.__draw_zones()

    def __draw_drone(self, id: int, spot: Zone|Connection):
        drone_color = arcade.color.CYAN
        if isinstance(spot, Connection):
            drone_color = arcade.color.ORANGE
        drone_texture = arcade.make_circle_texture(self.drone_size, drone_color, f"D{id}")
        sx, sy = self.world_to_screen(spot.x, spot.y)
        arcade.draw_texture_rect(drone_texture, arcade.rect.Viewport(sx - self.drone_size/2, sy - self.drone_size/2, self.drone_size, self.drone_size))

    def draw_drones(self):
        turn = self.turns[self.turn]
        for drone, spot in turn.items():
            self.__draw_drone(drone, spot)


    def on_update(self, delta_time):
        speed = 12.0

        self.hud_height += (
            self.target_hud_height - self.hud_height
        ) * speed * delta_time

    def on_draw(self):
        self.clear()
        draw_texture_rect(
            self.background,
            arcade.rect.Viewport(0, 0, self.width, self.height),
        )
        self.draw_map()
        self.draw_drones()
        self.__draw_hud()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.RIGHT or symbol == key.D:
            self.hold["right"] = True
            self.turn += 1
            self.turn = min(self.turn, self.max_turn)
        elif symbol == key.LEFT or symbol == key.A:
            self.hold["left"] = True
            self.turn -= 1
            self.turn = max(self.turn, 0)
        elif symbol == key.UP or symbol == key.W:
            self.hold["up"] = True
        elif symbol == key.DOWN or symbol == key.S:
            self.hold["down"] = True
        elif symbol == key.EQUAL:
            self.zoom += self.zoom_step
            self.zoom = min(self.zoom, self.max_zoom)
            # print(self.zoom)
        elif symbol == key.MINUS:
            self.zoom -= self.zoom_step
            self.zoom = max(self.zoom, self.min_zoom)
            # print(self.zoom)
        elif symbol == key.R:
            self.__calculate_viewport()
        elif symbol == key.ESCAPE:
            self.close()
        elif symbol == key.H:
            if self.flags["hud"]:
                self.target_hud_height = 0
            else:
                self.target_hud_height = self.height / 4
            self.flags["hud"] = not self.flags["hud"]

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

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            if self.flags["hud"]:
                if self.hud_height - self.hud_bar_size * 2 < y < self.hud_height + self.hud_bar_size:
                    self.flags["can_resize_hud"] = True
                else:
                    self.flags["can_resize_hud"] = False
                if self.hud_height + self.hud_bar_size < y < self.height:
                    self.flags["can_drag"] = True
                else:
                    self.flags["can_drag"] = False
            else:
                self.flags["can_resize_hud"] = False
                self.flags["can_drag"] = True



    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.flags["can_drag"]:
            self.ox += dx
            self.oy += dy
        if self.flags["can_resize_hud"]:
            self.hud_height += dy
        # print(f"{self.ox, self.oy = }")

    def on_mouse_motion(self, x, y, dx, dy):
        pass


