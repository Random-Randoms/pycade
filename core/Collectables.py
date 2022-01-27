import random

import arcade

from core.GameObjects import GameObject, random_speed, random_rotation, random_angle


class Collectable(GameObject):
    def __init__(self, filename, amount, sound):
        super(Collectable, self).__init__(filename)
        self.amount = amount
        self.sound = sound
        self.move_by_flight = True
        self.type = 'collectable'

    def on_spawn(self):
        random_rotation(self)
        random_angle(self)
        random_speed(self, 50)

    def player_collide(self):
        self.flight.player.add_scraps(self.amount)
        arcade.play_sound(arcade.load_sound(self.sound))
        self.complete_destroy()


class SmallScrap(Collectable):
    def __init__(self, filename):
        super(SmallScrap, self).__init__(filename, random.randint(0, 10), 'sounds/scrap_collect.wav')
