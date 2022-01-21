import copy
import math

import arcade

from core.Utilities import Timer


class AnimatedSprite(arcade.Sprite):
    def __init__(self, filename, scale=1.0, frequency=1 / 6):
        super(AnimatedSprite, self).__init__(filename, scale)
        self.states = {'Idle': [arcade.load_texture(filename)]}
        self.frequency = frequency
        self.cur_state = self.states['Idle']
        self.cur_index = 0
        self.animation_timer = Timer(self.frequency, self.update_texture)

    def update_texture(self):
        self.cur_index = (self.cur_index + 1) % len(self.cur_state)
        self._set_texture2(self.cur_state[self.cur_index])

    def add_state_fnames(self, name, filenames):
        textures = []
        for filename in filenames:
            textures.append(arcade.load_texture(filename))
        self.states[name] = textures

    def add_state_textures(self, name, textures):
        self.states[name] = textures

    def upd(self, delta_time):
        self.animation_timer.update(delta_time)

    def set_state(self, name):
        self.cur_state = self.states[name]
        self.cur_index = 0


class GameObject(AnimatedSprite):
    def __init__(self, filename, scale=1.0, frequency=1 / 6):
        super(GameObject, self).__init__(filename, scale, frequency)
        self.fname = filename
        self.type = ''
        self._scale = scale
        self.speed_x = 0
        self.speed_y = 0
        self._speed = 0
        self.angle_speed = 0
        self.flight = None
        self.collidable = True
        self.move_by_flight = False

    def upd(self, delta_time):
        super(GameObject, self).upd(delta_time)
        self.turn_left(self.angle_speed * delta_time)
        self.center_x += self.speed_x * delta_time
        self.center_y += self.speed_y * delta_time
        if self.center_y < 0:
            self.complete_destroy()

    def move(self, x, y):
        self.center_x += x
        self.center_y += y

    def is_collidable(self):
        return self.collidable

    def collide(self, _object):
        pass

    def player_collide(self):
        pass

    def set_angle(self, new_value: float):
        self.angle = new_value

    def fly_by_angle(self):
        self.speed_x = self._speed * math.cos((self.angle + 90) * math.pi / 180)
        self.speed_y = self._speed * math.sin((self.angle + 90) * math.pi / 180)

    def set_flight(self, flight):
        self.flight = flight

    def complete_destroy(self):
        self.remove_from_sprite_lists()
        del self

    def set_angle_speed(self, speed):
        self.angle_speed = speed

    def copy(self):
        return copy.deepcopy(self)