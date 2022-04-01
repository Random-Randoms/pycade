import copy
import math
import random
import arcade

from core.Utilities import Timer


class AnimatedSprite(arcade.Sprite):
    def __init__(self, filename=None, scale=1.0, frequency=1 / 6):
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
    def __init__(self, name, filename, scale=1.0, frequency=1 / 6):
        super(GameObject, self).__init__(filename, scale, frequency)
        self.name = name
        self.fname = filename
        self.type = ''
        self._scale = scale
        self.speed_x = 0
        self.speed_y = 0
        self.force_x = 0
        self.force_y = 0
        self.angle_speed = 0
        self.flight = None
        self.collidable = True
        self.move_by_flight = False

    """ event methods """

    def on_destroy(self):
        pass

    def on_spawn(self):
        pass

    def collide(self, _object):
        pass

    def player_collide(self):
        pass

    """ *physical* methods """

    def set_speed(self, speed_x, speed_y):
        self.speed_x = speed_x
        self.speed_y = speed_y

    def add_force(self, force_x, force_y):
        self.force_x += force_x
        self.force_y += force_y

    def move(self, x, y):
        self.center_x += x
        self.center_y += y

    def set_angle(self, new_value: float):
        self.angle = new_value

    def set_angle_speed(self, speed):
        self.angle_speed = speed

    def rotate_by_speed(self):
        self.angle = math.atan(self.speed_y / self.speed_x) * 180 / math.pi
        if self.speed_y < 0:
            self.angle += 180

    def fly_by_angle(self, _speed):
        self.speed_x = _speed * math.cos((self.angle + 90) * math.pi / 180)
        self.speed_y = _speed * math.sin((self.angle + 90) * math.pi / 180)

    def complete_destroy(self):
        self.remove_from_sprite_lists()
        del self

    """ property methods """

    def set_flight(self, flight):
        self.flight = flight

    def is_collidable(self):
        return self.collidable

    """ misc """

    def upd(self, delta_time):
        super(GameObject, self).upd(delta_time)
        self.turn_left(self.angle_speed * delta_time)
        self.speed_x += self.force_x
        self.speed_y += self.force_y
        self.force_x = 0
        self.force_y = 0
        self.center_x += self.speed_x * delta_time
        self.center_y += self.speed_y * delta_time
        if self.center_y < 0:
            self.complete_destroy()

    def copy(self):
        return copy.deepcopy(self)


def aim_at_player(_object, flight):
    angle = 180 - math.atan((_object.center_x - flight.player.ship_sprite.center_x) /
                            (_object.center_y - flight.player.ship_sprite.center_y)) / math.pi * 180
    _object.turn_left(angle)


def random_angle(_object):
    _object.set_angle(random.randint(0, 360))


def random_rotation(_object):
    _object.set_angle_speed(random.randint(-100, 100))


def random_speed(_object, max_speed=100):
    _object.fly_by_angle(random.randint(0, max_speed))


def spawn(_object, flight, x, y):
    new_object = _object.copy()
    new_object.set_flight(flight)
    new_object.center_x = x
    new_object.center_y = y

    new_object.on_spawn()

    flight.add_object(new_object)
    return new_object


def spawn_speed(_object, flight, x, y, speed_x, speed_y):
    new_object = spawn(_object, flight, x, y)
    new_object.set_speed(speed_x, speed_y)
    new_object.rotate_by_speed()


def spawn_angle(_object, flight, x, y, angle):
    new_object = spawn(_object, flight, x, y)
    new_object.set_angle(angle)
    new_object.fly_by_angle(new_object.speed)
