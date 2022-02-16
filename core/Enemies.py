import random

import pyglet.image
from pydub import AudioSegment
from pyglet.image import load
import arcade

from core.Collectables import SmallScrap
from core.GameObjects import GameObject, spawn, aim_at_player, random_rotation, random_speed, random_angle
from core.Utilities import Timer


scrap = SmallScrap('small scrap', 'sprites/scrap/scrap.png')


class Enemy(GameObject):
    def __init__(self, name, filename, scale, enemy_type):
        super(Enemy, self).__init__(name, filename, scale)
        self.type = enemy_type
        self.collidable = True


class RammingEnemy(Enemy):
    def __init__(self, name, filename, scale, speed, damage, enemy_type='', flying_textures=None, destruction_textures=None):
        super(RammingEnemy, self).__init__(name, filename, scale, enemy_type)
        self.speed = speed
        if flying_textures is not None:
            self.flying_textures = flying_textures
        else:
            self.flying_textures = [arcade.load_texture(filename)]
        self.add_state_textures('flying', self.flying_textures)
        if destruction_textures is not None:
            self.destruction_textures = destruction_textures
        else:
            self.destruction_textures = [arcade.load_texture(filename)]
        self.add_state_textures('destruction', self.destruction_textures)
        self.set_state('flying')
        self.angle_speed = 0
        self.damage = damage
        self.destruction_timer = Timer(1.0, self.complete_destroy)
        self.destruction_timer.stop()

    def on_destroy(self):
        self.collidable = False
        self.set_state('destruction')
        self.destruction_timer.trigger_time = self.frequency * (len(self.destruction_textures) - 1)
        self.destruction_timer.start()

    def is_collidable(self):
        return self.collidable

    def set_angle_speed(self, angle_speed):
        self.angle_speed = angle_speed

    def upd(self, delta_time):
        super().upd(delta_time)
        self.destruction_timer.update(delta_time)
        if self.center_y < -50:
            self.complete_destroy()

    def set_angle(self, angle):
        self.angle = angle


class Asteroid(RammingEnemy):
    def __init__(self, name, filename, scale, speed, damage, destruction_sound, destruction_textures=None):
        super().__init__(name, filename, scale, speed, damage, enemy_type='asteroid', destruction_textures=destruction_textures)
        self.move_by_flight = True
        self.destruction_sound = AudioSegment.from_wav('sounds/sfx_exp_shortest_soft7.wav')

    def on_spawn(self):
        random_rotation(self)
        random_angle(self)
        random_speed(self, 25)

    def player_collide(self):
        self.on_destroy()

    def on_destroy(self):
        super(Asteroid, self).on_destroy()
        spawn_scrap(self.flight, self.center_x, self.center_y)
        spawn_scrap(self.flight, self.center_x, self.center_y)
        spawn_scrap(self.flight, self.center_x, self.center_y)
        #play(self.destruction_sound)

    def collide(self, _object):
        if _object.type in ['missile', 'bullet', 'explosion']:
            self.on_destroy()


class Missile(RammingEnemy):
    def __init__(self, name, filename, scale, speed, damage, explosion, destruction_textures=None):
        super(Missile, self).__init__(name, filename, scale, speed, damage, 'missile')
        self.explosion = explosion

    def on_spawn(self):
        aim_at_player(self, self.flight)
        self.fly_by_angle(self.speed)

    def player_collide(self):
        self.on_destroy()

    def collide(self, _object):
        if _object.type in ['bullet']:
            self.on_destroy()

    def on_destroy(self):
        new_explosion = self.explosion.copy()
        spawn(new_explosion, self.flight, self.center_x, self.center_y)
        self.complete_destroy()


class TimeSpawner:
    def __init__(self, _object, frequency):
        self.object = _object
        self.frequency = frequency
        self.left = 0
        self.right = 1
        self.top = 0
        self.flight = None
        self.spawn_timer = Timer(frequency, self.spawn_enemy)

    def set_flight(self, flight):
        self.flight = flight
        self.top = flight.height
        self.left = flight.left_spawn
        self.right = flight.right_spawn

    def spawn_enemy(self):
        spawn(self.object, self.flight, random.randint(self.left, self.right), self.top + 50)

    def update(self, delta_time):
        self.spawn_timer.update(delta_time)


def spawn_scrap(flight, x, y):
    spawn(scrap, flight, x, y)
