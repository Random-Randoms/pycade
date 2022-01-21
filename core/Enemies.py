import math
import random

import arcade

from core.Collectables import SmallScrap
from core.GameObjects import GameObject
from core.Utilities import Timer


class Enemy(GameObject):
    def __init__(self, filename, scale, enemy_type):
        super(Enemy, self).__init__(filename, scale)
        self._rotate_type = 0
        self.type = enemy_type
        self.collidable = True

    def rotate_type(self):
        return self._rotate_type


class RammingEnemy(Enemy):
    def __init__(self, filename, scale, speed, damage, rotate_type=0, enemy_type='', flying_fnames=None,
                 destruction_fnames=None):
        super(RammingEnemy, self).__init__(filename, scale, enemy_type)
        self._speed = speed
        self._rotate_type = rotate_type
        self.fly_by_angle()
        if flying_fnames is not None:
            self.flying_fnames = flying_fnames
        else:
            self.flying_fnames = [filename]
        self.add_state_fnames('flying', self.flying_fnames)
        if destruction_fnames is not None:
            self.destruction_fnames = destruction_fnames
        else:
            self.destruction_fnames = [filename]
        self.add_state_fnames('destruction', self.destruction_fnames)
        self.set_state('flying')
        self.angle_speed = 0
        self.damage = damage
        self.destruction_timer = Timer(1.0, self.complete_destroy)
        self.destruction_timer.stop()

    def destroy(self):
        self.collidable = False
        self.set_state('destruction')
        self.destruction_timer.trigger_time = self.frequency * (len(self.destruction_fnames) - 1)
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
    def __init__(self, filename, scale, speed, damage, destruction_sound, destruction_fnames=None):
        super().__init__(filename, scale, speed, damage, 1, enemy_type='asteroid',
                         destruction_fnames=destruction_fnames)
        self.move_by_flight = True
        self.destruction_sound = destruction_sound

    def player_collide(self):
        self.destroy()

    def destroy(self):
        super(Asteroid, self).destroy()
        spawn_scrap(self.flight, self.center_x, self.center_y)
        spawn_scrap(self.flight, self.center_x, self.center_y)
        spawn_scrap(self.flight, self.center_x, self.center_y)
        arcade.play_sound(arcade.load_sound(self.destruction_sound))

    def collide(self, _object):
        if _object.type in ['missile', 'bullet', 'explosion']:
            self.destroy()


class Missile(RammingEnemy):
    def __init__(self, filename, scale, speed, damage, explosion, destruction_fnames=None):
        super(Missile, self).__init__(filename, scale, speed, damage, 2, 'missile', destruction_fnames)
        self.explosion = explosion

    def player_collide(self):
        self.destroy()

    def collide(self, _object):
        if _object.type in ['bullet']:
            self.destroy()

    def destroy(self):
        new_explosion = self.explosion.copy()
        new_explosion.position = self.position
        self.flight.add_object(new_explosion)
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
        new_enemy = self.object.copy()
        new_enemy.set_flight(self.flight)
        new_enemy.center_x = random.randint(self.left, self.right)
        new_enemy.center_y = self.top + 50
        if new_enemy.rotate_type() == 1:
            new_enemy.turn_left(180)
            new_enemy.set_angle_speed(random.randint(-100, 100))
        if new_enemy.rotate_type() == 2:
            angle = 180 - math.atan((new_enemy.center_x - self.flight.player.ship_sprite.center_x) /
                                    (new_enemy.center_y - self.flight.player.ship_sprite.center_y)) / math.pi * 180
            new_enemy.turn_left(angle)
        new_enemy.fly_by_angle()
        self.flight.add_object(new_enemy)

    def update(self, delta_time):
        self.spawn_timer.update(delta_time)


def spawn_scrap(flight, x, y):
    new_scrap = SmallScrap('sprites/scrap/scrap.png')
    new_scrap.set_flight(flight)
    new_scrap.set_position(x, y)
    new_scrap.set_angle_speed(random.randint(-10000, 10000) / 10)
    new_scrap.set_angle(random.randint(0, 360))
    new_scrap._speed = random.randint(-50, 50)
    new_scrap.fly_by_angle()
    flight.add_object(new_scrap)