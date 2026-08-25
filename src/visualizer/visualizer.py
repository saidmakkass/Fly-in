import arcade
from importlib.resources import files

from .converter import Graph, Turns
from .scaler import Scaler
from .map import Map
from .drone import Fleet
from .constants import WINDOW_TITLE


class Visualizer:
    """High-level entrypoint to run the graphical visualizer."""

    def __init__(self, graph: Graph, nb_drones: int, turns: Turns):
        """Create a visualizer for `graph` and simulation `turns`."""
        self.window = VisualizerWindow()
        self.graph_view = GraphView(self.window, graph, nb_drones, turns)

    def run(self) -> None:
        """Start the arcade event loop showing the graph view."""
        self.window.run(self.graph_view)


class GraphView(arcade.View):
    """Arcade view displaying the map and drone fleet with controls."""

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

        self.fleet = Fleet(nb_drones, self.map, turns)
        self.fleet.execute_turn(self.turns[self.turn])

    def __load_assets(self) -> None:
        """Load image assets required by the view."""
        assets_dir = files(__package__) / "assets"

        self.background_image = arcade.load_texture(
            assets_dir / "background.jpg"
        )

    def __draw_background(self) -> None:
        """Draw the background texture stretched to the view size."""
        arcade.draw_texture_rect(
            self.background_image,
            arcade.rect.Viewport(0, 0, self.width, self.height),
        )

    def on_draw(self) -> None:
        """Arcade callback to render the view each frame."""
        self.__draw_background()
        if self.toggles["map"]:
            self.map.draw()
        if self.toggles["drones"]:
            self.fleet.draw()
        self.fps.draw()

    def on_resize(self, width: int, height: int) -> None:
        """Handle window resize: adjust scaler and map layout."""
        self.fps.position = 0, height - 14
        self.scaler.resize(width, height)
        self.scaler.reset()
        self.map.resize()

    def on_update(self, delta_time: float) -> None:
        """Update view state each frame given elapsed `delta_time`."""
        self.fps.text = (
            f"FPS: {round(arcade.get_fps())}  Turn {self.turn}/{self.max_turn}"
        )
        self.map.collision_check(self.mouse)

        self.fleet.update(delta_time)

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int
    ) -> None:
        """Handle drag events: pan map when dragging."""
        self.on_mouse_motion(x, y, dx, dy)
        if self.toggles["map"]:
            self.scaler.ox += dx
            self.scaler.oy += dy

    def on_mouse_scroll(
        self, sx: int, sy: int, scroll_x: int, scroll_y: int
    ) -> None:
        """Zoom and pan centered on the mouse scroll position."""
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

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """Update internal mouse sprite position for collision checks."""
        self.mouse.position = (x, y)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Handle keyboard shortcuts controlling playback and view toggles."""
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


class VisualizerWindow(arcade.Window):
    """Arcade window wrapper used by the Visualizer."""

    def __init__(self) -> None:
        super().__init__(title=WINDOW_TITLE, resizable=True)
        self.center_window()
