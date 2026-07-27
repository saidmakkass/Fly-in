import arcade

from .converter import Graph

WINDOW_TITLE = "Fly-in"

class Visualizer:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.window = VisualizerWindow()

    def run(self):
        self.window.run()

class VisualizerWindow(arcade.Window):
    def __init__(self):
        super().__init__(title=WINDOW_TITLE, resizable=True)
        self.center_window()