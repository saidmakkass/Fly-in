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
        self.spot = start

        self.target_x = start.center_x
        self.target_y = start.center_y

        self.move_time = 0.0
        self.vx = 0
        self.vy = 0

    def set_target(self, target):
        self.spot = target
        self.target_x = target.center_x
        self.target_y = target.center_y
        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y
        self.vx = dx / TURN_DURATION
        self.vy = dy / TURN_DURATION

    def update(self, delta_time, *args, **kwargs):

        self.center_x += self.vx * delta_time
        self.center_y += self.vy * delta_time

        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y

        if dx * self.vx + dy * self.vy <= 0:
            self.center_x = self.target_x
            self.center_y = self.target_y
            self.vx = 0
            self.vy = 0

class Fleet:
    def __init__(self, nb_drones: int, map: Map, turns):
        self.drones = arcade.SpriteList()
        self.map = map
        for id in range(1, nb_drones + 1):
            self.drones.append(Drone(id, map.spots[turns[0][id][0]]))
        self.turn_time = 0.0

    def execute_turn(self, turn: Turn):
        for drone in self.drones:
            spot_name = turn[drone.id][0]
            drone.set_target(self.map.spots[spot_name])

    def update(self, delta_time):
        self.drones.update(delta_time)

    def draw(self):
        self.drones.draw()
