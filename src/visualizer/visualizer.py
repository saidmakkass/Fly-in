import arcade
from importlib.resources import files

from .converter import Graph
from .scaler import Scaler
from .map import Map

WINDOW_TITLE = "Fly-in"


class Visualizer:
    def __init__(self, graph: Graph, nb_drones: int):
        self.nb_drones = nb_drones
        self.window = VisualizerWindow()
        self.graph_view = GraphView(self.window, graph)

    def run(self):
        self.window.run(self.graph_view)


class GraphView(arcade.View):
    def __init__(self, window: arcade.Window, graph: Graph):
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
        self.map = Map(graph, self.scaler)
        self.mouse = arcade.Sprite()
        self.mouse.hit_box = arcade.hitbox.HitBox(((0, 0), (1, 1)))

    def __load_assets(self):
        assets_dir = files(__package__) / "assets"

        self.background_image = arcade.load_texture(
            assets_dir / "background.jpg"
        )

    def __draw_background(self):
        arcade.draw_texture_rect(
            self.background_image,
            arcade.rect.Viewport(0, 0, self.width, self.height),
        )

    def on_draw(self):
        self.__draw_background()
        self.map.draw()
        self.fps.draw()

    def on_resize(self, width, height):
        self.fps.position = 0, height - 14
        self.scaler.resize(width, height)
        self.map.resize()

    def on_update(self, delta_time):
        self.fps.text = f"FPS: {arcade.get_fps():.0f}"

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        self.on_mouse_motion(x, y, dx, dy)
        self.scaler.ox += dx
        self.scaler.oy += dy

    def on_mouse_scroll(self, sx, sy, scroll_x, scroll_y):
        if scroll_y:
            prev_sx = (sx - self.scaler.ox) / self.scaler.zoom
            prev_sy = (sy - self.scaler.oy) / self.scaler.zoom
            self.scaler.zoom += scroll_y * 0.1
            self.scaler.zoom = max(self.scaler.zoom, 1.0)
            self.scaler.zoom = min(self.scaler.zoom, 10.0)
            self.scaler.ox = sx - prev_sx * self.scaler.zoom
            self.scaler.oy = sy - prev_sy * self.scaler.zoom
        self.on_mouse_motion(sx, sy, 0, 0)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse.position = (x, y)
        self.map.collision_check(self.mouse)


class VisualizerWindow(arcade.Window):
    def __init__(self):
        super().__init__(title=WINDOW_TITLE, resizable=True)
        self.center_window()
