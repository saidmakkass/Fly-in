import arcade
from typing import List

from .map import Map
from .converter import Turn
from .constants import TURN_DURATION


class Drone(arcade.Sprite):
    def __init__(self, textures: arcade.Texture, id: int, start):
        super().__init__(
            textures[0],
            center_x=start.center_x,
            center_y=start.center_y,
            scale=1,
        )
        self.textures = textures
        self.id = id
        self.set_target(start)
        self.animation_timer = 0

    @property
    def target_x(self):
        return self.spot.center_x
    @property
    def target_y(self):
        return self.spot.center_y

    def set_target(self, target):
        self.spot = target

    def update_animation(self, delta_time: float = 1 / 60):
        self.animation_timer += delta_time

        if self.animation_timer >= 0.1:  # 10 FPS animation
            self.animation_timer = 0
            self.cur_texture_index = (self.cur_texture_index + 1) % len(self.textures)
            self.texture = self.textures[self.cur_texture_index]

    def update(self, delta_time, *args, **kwargs):
        self.update_animation(delta_time)

        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y

        vx = dx / TURN_DURATION
        vy = dy / TURN_DURATION

        self.center_x += vx * delta_time
        self.center_y += vy * delta_time

        if dx * vx + dy * vy <= 0:
            self.center_x = self.target_x
            self.center_y = self.target_y

class Fleet:
    def __init__(self, textures: List[arcade.Texture], nb_drones: int, map: Map, turns):
        self.drones = arcade.SpriteList()
        self.map = map
        for id in range(1, nb_drones + 1):
            self.drones.append(Drone(textures, id, map.spots[turns[0][id][0]]))

    def execute_turn(self, turn: Turn):
        for drone in self.drones:
            spot_name = turn[drone.id][0]
            drone.set_target(self.map.spots[spot_name])

    def update(self, delta_time):
        self.drones.update(delta_time)

    def draw(self):
        self.drones.draw()
