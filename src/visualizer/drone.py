import arcade
import math
from typing import List

from .map import Map, Zone, Connection
from .converter import Turn, Turns
from .constants import TURN_DURATION, ZONE_RADIUS


class Drone(arcade.Sprite):
    def __init__(self, id: int, start: Zone) -> None:
        super().__init__(
            arcade.texture.make_circle_texture(20, (0, 255, 255)),
            center_x=start.center_x,
            center_y=start.center_y,
        )
        self.id = id
        self.center_x = 0.0
        self.center_y = 0.0
        self.spot = start
        self.spot.count += 1
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.set_target(start)
        self.animation_timer = 0.0

    @property
    def target_x(self) -> float:
        return self.spot.center_x

    @property
    def target_y(self) -> float:
        return self.spot.center_y

    def set_offset(self, count: int) -> None:
        if count <= 1:
            self.offset_x = 0.0
            self.offset_y = 0.0
            return

        angle = (2 * math.pi * self.id) / count
        radius = ZONE_RADIUS
        self.offset_x = radius * math.sin(angle)
        self.offset_y = radius * math.cos(angle)

    def set_target(self, target: Zone | Connection) -> None:
        if self.spot:
            self.spot.count -= 1
        self.spot = target
        self.spot.count += 1

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        return
        self.animation_timer += delta_time

        if self.animation_timer >= 0.1:
            self.animation_timer = 0.0
            self.cur_texture_index: int = (self.cur_texture_index + 1) % len(
                self.textures
            )
            self.texture = self.textures[self.cur_texture_index]

    def update(self, delta_time: float) -> None:
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
        for drone in self.drones:
            spot_name = turn[drone.id][0]
            spot = self.map.spots[spot_name]
            drone.set_target(spot)
        for drone in self.drones:
            drone.set_offset(drone.spot.count)

    def update(self, delta_time: float) -> None:
        self.drones.update(delta_time)

    def draw(self) -> None:
        self.drones.draw()
