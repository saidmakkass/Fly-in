import arcade
from importlib.resources import files

from .converter import Graph, Turns
from .scaler import Scaler
from .map import Map
from .drone import Fleet
from .constants import WINDOW_TITLE


class Visualizer:
    def __init__(self, graph: Graph, nb_drones: int, turns: Turns):
        self.window = VisualizerWindow()
        self.graph_view = GraphView(self.window, graph, nb_drones, turns)

    def run(self):
        self.window.run(self.graph_view)


class GraphView(arcade.View):
    def __init__(
        self, window: arcade.Window, graph: Graph, nb_drones: int, turns: Turns
    ):
        super().__init__(window)
        arcade.enable_timings()
        self.fps = arcade.Text("", 0, self.height - 14, font_size=14)
        self.__load_assets()
        self.scaler = Scaler(
            [z[1] for z in graph[0]],
            [z[2] for z in graph[0]],
            window.width,
            window.height,
        )
        self.toggles = {
            "map": True,
            "drones": True,
            "popup": False,
        }
        self.map = Map(graph, self.scaler, self.toggles)
        self.mouse = arcade.Sprite()
        self.mouse.hit_box = arcade.hitbox.HitBox(((0, 0), (1, 1)))

        self.nb_drones = nb_drones
        self.turns = turns
        self.turn = 0
        self.max_turn = len(turns) - 1

        self.fleet = Fleet(self.drone_textures, nb_drones, self.map, turns)

    def __load_assets(self):
        assets_dir = files(__package__) / "assets"

        self.background_image = arcade.load_texture(
            assets_dir / "background.jpg"
        )
        self.drone_textures = arcade.load_spritesheet(assets_dir / "drone.png").get_texture_grid((48,48), 4, 4)


    def __draw_background(self):
        arcade.draw_texture_rect(
            self.background_image,
            arcade.rect.Viewport(0, 0, self.width, self.height),
        )

    def on_draw(self):
        self.__draw_background()
        if self.toggles["map"]:
            self.map.draw()
        if self.toggles["drones"]:
            self.fleet.draw()
        self.fps.draw()

    def on_resize(self, width, height):
        self.fps.position = 0, height - 14
        self.scaler.resize(width, height)
        self.scaler.reset()
        self.map.resize()

    def on_update(self, delta_time):
        self.fps.text = f"FPS: {round(arcade.get_fps())}"
        self.map.collision_check(self.mouse)

        self.fleet.update(delta_time)

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        self.on_mouse_motion(x, y, dx, dy)
        if self.toggles["map"]:
            self.scaler.ox += dx
            self.scaler.oy += dy

    def on_mouse_scroll(self, sx, sy, scroll_x, scroll_y):
        if scroll_y:
            prev_sx = (
                sx - self.scaler.ox - self.scaler.pad
            ) / self.scaler.zoom
            prev_sy = (
                sy - self.scaler.oy - self.scaler.pad
            ) / self.scaler.zoom
            self.scaler.zoom += scroll_y * 0.1
            self.scaler.zoom = max(self.scaler.zoom, 1.0)
            self.scaler.ox = sx - prev_sx * self.scaler.zoom - self.scaler.pad
            self.scaler.oy = sy - prev_sy * self.scaler.zoom - self.scaler.pad
        self.mouse.position = sx, sy

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse.position = (x, y)

    def on_key_press(self, symbol, modifiers):
        match modifiers, symbol:
            case (_, arcade.key.ESCAPE):
                self.window.close()
            case (_, arcade.key.R):
                self.scaler.reset()
                self.turn = 0
                self.fleet.execute_turn(self.turns[self.turn])
            case (_, arcade.key.P):
                self.toggles["popup"] = not self.toggles["popup"]
            case (_, arcade.key.M):
                self.toggles["map"] = not self.toggles["map"]
            case (_, arcade.key.D):
                self.toggles["drones"] = not self.toggles["drones"]
            case (_, arcade.key.RIGHT):
                self.turn += 1
                self.turn = min(self.turn, self.max_turn)
                self.fleet.execute_turn(self.turns[self.turn])
            case (_, arcade.key.LEFT):
                self.turn -= 1
                self.turn = max(self.turn, 0)
                self.fleet.execute_turn(self.turns[self.turn])
            case (_, arcade.key.F):
                self.window.set_fullscreen(not self.window.fullscreen)
            case _:
                print(f"{modifiers = }, {symbol = }")


class VisualizerWindow(arcade.Window):
    def __init__(self):
        super().__init__(title=WINDOW_TITLE, resizable=True)
        self.center_window()
