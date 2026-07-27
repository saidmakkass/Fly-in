import arcade

from .converter import Graph

WINDOW_TITLE = "Fly-in"

class Visualizer:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.window = VisualizerWindow()
        self.graph_view = GraphView(self.window)

    def run(self):
        self.window.run(self.graph_view)

class GraphView(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window)

    def on_draw(self):
        pass

    def on_update(self, delta_time):
        pass

class VisualizerWindow(arcade.Window):
    def __init__(self):
        super().__init__(title=WINDOW_TITLE, resizable=True)
        self.center_window()