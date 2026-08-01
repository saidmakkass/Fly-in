import arcade
import math

from .map import Map
from .converter import Turn
from .constants import TURN_DURATION


class Drone(arcade.Sprite):
    def __init__(self, id: int, start):
        super().__init__(
            arcade.texture.make_circle_texture(20, (0, 255, 255)),
            center_x=start.center_x,
            center_y=start.center_y,
        )
        self.id = id
        self.set_target(start)

    @property
    def target_x(self):
        return self.spot.center_x
    @property
    def target_y(self):
        return self.spot.center_y

    def set_target(self, target):
        self.spot = target


    def update(self, delta_time, *args, **kwargs):
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
    def __init__(self, nb_drones: int, map: Map, turns):
        self.drones = arcade.SpriteList()
        self.map = map
        for id in range(1, nb_drones + 1):
            self.drones.append(Drone(id, map.spots[turns[0][id][0]]))

    def execute_turn(self, turn: Turn):
        for drone in self.drones:
            spot_name = turn[drone.id][0]
            drone.set_target(self.map.spots[spot_name])

    def update(self, delta_time):
        self.drones.update(delta_time)

    def draw(self):
        self.drones.draw()
