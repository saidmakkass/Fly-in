import arcade
import math

from .map import Map, Zone, Connection
from .converter import Turn, Turns
from .constants import TURN_DURATION, ZONE_RADIUS


class Drone(arcade.Sprite):
    """Visual representation of a single drone in the simulation."""
    def __init__(self, id: int, start: Zone) -> None:
        """Create a drone sprite and place it at `start` spot."""
        super().__init__(
            arcade.texture.make_circle_texture(20, (0, 255, 255)),
            center_x=start.center_x,
            center_y=start.center_y,
        )
        self.id = id
        self.center_x = 0.0
        self.center_y = 0.0
        self.spot = start
        self.spot.drones.append(self)
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.set_target(start)
        self.animation_timer = 0.0

    @property
    def target_x(self) -> float:
        """X coordinate the drone is moving toward."""
        return self.spot.center_x

    @property
    def target_y(self) -> float:
        """Y coordinate the drone is moving toward."""
        return self.spot.center_y

    def set_offset(self) -> None:
        """Compute a small offset to visually separate
        multiple drones on a spot."""
        count = len(self.spot.drones)
        index = self.spot.drones.index(self)
        if count <= 1:
            self.offset_x = 0.0
            self.offset_y = 0.0
            return

        angle = (2 * math.pi * index) / count
        radius = ZONE_RADIUS
        self.offset_x = radius * math.sin(angle)
        self.offset_y = radius * math.cos(angle)

    def set_target(self, target: Zone | Connection) -> None:
        """Move the drone to a new target spot (Zone or Connection)."""
        if self.spot:
            self.spot.drones.remove(self)
        self.spot = target
        self.spot.drones.append(self)

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        """Advance any animation frames (currently disabled)."""
        return
        self.animation_timer += delta_time

        if self.animation_timer >= 0.1:
            self.animation_timer = 0.0
            self.cur_texture_index: int = (self.cur_texture_index + 1) % len(
                self.textures
            )
            self.texture = self.textures[self.cur_texture_index]

    def update(self, delta_time: float) -> None:
        """Update the drone position toward its target using `delta_time`."""
        self.update_animation(delta_time)

        dx = self.target_x + self.offset_x - self.center_x
        dy = self.target_y + self.offset_y - self.center_y
        vx = dx / TURN_DURATION
        vy = dy / TURN_DURATION

        self.center_x += vx * delta_time
        self.center_y += vy * delta_time

        if dx * vx + dy * vy <= 0:
            self.center_x = self.target_x
            self.center_y = self.target_y


class Fleet:
    """Manage a collection of `Drone` sprites and apply turn updates."""
    def __init__(
        self,
        nb_drones: int,
        map: Map,
        turns: Turns,
    ):
        self.drones = arcade.SpriteList()
        self.map = map
        for id in range(1, nb_drones + 1):
            self.drones.append(Drone(id, map.spots[turns[0][id][0]]))

    def execute_turn(self, turn: Turn) -> None:
        """Apply the positions from `turn` to each drone in the fleet."""
        for drone in self.drones:
            spot_name = turn[drone.id][0]
            spot = self.map.spots[spot_name]
            drone.set_target(spot)
        for drone in self.drones:
            drone.set_offset()

    def update(self, delta_time: float) -> None:
        """Update all drones (movement) given elapsed `delta_time`."""
        self.drones.update(delta_time)

    def draw(self) -> None:
        """Draw all drone sprites to the screen."""
        self.drones.draw()
