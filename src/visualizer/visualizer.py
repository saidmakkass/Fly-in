import arcade
from importlib.resources import files

from .viewport import Viewport
from .converter import Graph
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
        self.__load_assets()
        self.view_port = Viewport()
        self.map = Map(graph, self.width, self.height, self.view_port)

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


    def on_update(self, delta_time):
        pass


class VisualizerWindow(arcade.Window):
    def __init__(self):
        super().__init__(title=WINDOW_TITLE, resizable=True)
        self.center_window()
