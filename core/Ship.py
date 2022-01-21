import math

import arcade

from core.GameObjects import GameObject
from core.Utilities import status_color, clamp


class Value:
    def __init__(self, name=''):
        self._value = None
        self.name = name
        self._upgradable = False
        self.facility = None

    def is_upgradable(self):
        return self._upgradable

    def value(self):
        return self._value

    def set_facility(self, facility):
        self.facility = facility


class ConstantValue(Value):
    def __init__(self, _value, name=''):
        super(ConstantValue, self).__init__(name)
        self._value = _value


class UpgradableValue(Value):
    def __init__(self, variants, prices, name=''):
        super(UpgradableValue, self).__init__(name)
        self._upgradable = True
        self.variants = variants
        self.prices = prices
        self.level = 0
        self._value = variants[self.level]

    def upgrade_cost(self):
        return self.prices[self.level]

    def next_value(self):
        if self._upgradable:
            return self.variants[self.level + 1]
        else:
            return None

    def upgrade(self):
        if len(self.variants) - 1 > self.level:
            self.level += 1
            self._value = self.variants[self.level]
        if len(self.variants) - 1 == self.level:
            self._upgradable = False

    def upgrade_info(self):
        if self._upgradable:
            return 'Upgrade ' + self.name + ' of ' + str(self.facility.name) + ' \n ' + 'from ' + str(self.value()) +\
                   ' to ' + str(self.next_value()) + ' for ' + str(self.upgrade_cost())

        else:
            return ''


class ShipFacility:
    def __init__(self, name: str, icon: str):
        self.upgradables = []
        self.name = name
        self.status = ' '
        self.showable = True
        self.status_positiveness = 0
        self.flight = None
        self.ship = None
        self.icon = icon

    def is_showable(self):
        return self.showable

    def info(self):
        return [0, 0, 0, self.name, self.status, status_color(self.status_positiveness)]

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        pass

    def set_flight(self, flight):
        self.flight = flight

    def set_ship(self, ship):
        self.ship = ship

    def update(self, delta_time):
        pass


class Bullet(GameObject):
    def __init__(self, fname, scale, speed, max_collisions=1, on_collision=0):
        self.speed = speed
        self.on_collision = on_collision
        self.collisions = 0
        self.max_collisions = max_collisions
        super().__init__(fname, scale)
        self.type = 'bullet'
        self.change_x = 0
        self.change_y = self.speed

    def add_speed(self, spd):
        self.change_x += spd

    def set_velocity(self):
        self.change_x = -self.speed * math.sin(math.radians(self.angle))
        self.change_y = self.speed * math.cos(math.radians(self.angle))

    def upd(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * math.cos(math.radians(self.angle)) * delta_time

    def collide(self, _object):
        if _object.type in ['asteroid', 'missile']:
            self.collisions += 1
            if self.collisions == self.max_collisions:
                self.last_collision()

    def copy(self):
        new_bullet = super().copy()
        new_bullet.collisions = 0
        return new_bullet

    def last_collision(self):
        if self.on_collision <= 0:
            self.complete_destroy()

    def complete_destroy(self):
        self.remove_from_sprite_lists()
        del self


class Weapon(ShipFacility):
    def __init__(self, name, icon, reload_time, energy_cost):
        super(Weapon, self).__init__(name, icon)
        self.reload_time = reload_time
        self.energy_cost = energy_cost
        self.upgradables.append(self.reload_time)
        self.upgradables.append(self.energy_cost)
        self.reload_time.set_facility(self)
        self.energy_cost.set_facility(self)


class ShootingWeapon(Weapon):
    def __init__(self, name, icon, bullet_sprite, reload_time, energy_cost, key, shoot_sound, error_sound):
        # parent class init
        super().__init__(name, icon, reload_time, energy_cost)

        # keys
        self.key = key

        # sprites
        self.bullet_sprite = bullet_sprite

        # time
        self.time_since_last_shoot = 0

        # sounds
        self.shoot_sound = shoot_sound
        self.error_sound = error_sound

    def info(self):
        if self.reload_time.value() > 0:
            rel_1 = self.reload_time_left() / self.reload_time.value()
        else:
            rel_1 = 1
        if self.energy_cost.value() > 0:
            rel_2 = clamp(self.ship.energy() / self.energy_cost.value(), 1, 0)
        else:
            rel_2 = 1
        rel_3 = 0
        return [rel_1, rel_2, rel_3, self.name, self.status, status_color(self.status_positiveness)]

    def update(self, delta_time):
        self.time_since_last_shoot += delta_time

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == self.key:
            self.shoot()

    def reload_time_left(self):
        if self.time_since_last_shoot >= self.reload_time.value():
            return 0
        else:
            return self.reload_time.value() - self.time_since_last_shoot

    def shoot(self):
        if self.reload_time_left() <= 0 and self.ship.energy_storage.energy >= self.energy_cost.value():
            arcade.play_sound(self.shoot_sound)
            self.ship.energy_storage.add(-self.energy_cost.value())
            self.time_since_last_shoot = 0
            new_bullet = self.bullet_sprite.copy()
            new_bullet.center_x = self.ship.ship_sprite.center_x
            new_bullet.center_y = self.ship.ship_sprite.center_y
            new_bullet.angle = self.ship.ship_sprite.angle
            new_bullet.add_speed(self.ship.current_speed)
            self.flight.add_object(new_bullet)
        else:
            arcade.play_sound(self.error_sound)


class ShieldCapacitor(ShipFacility):
    def __init__(self, name, icon, max_shield):
        super(ShieldCapacitor, self).__init__(name, icon)
        self.max_shield = max_shield
        self.max_shield.set_facility(self)
        self.cur_shield = 0
        self.status = 'functioning'
        self.status_positiveness = 2
        self.upgradables.append(self.max_shield)

    def set_info(self):
        if self.cur_shield > self.max_shield.value() * 3 / 4:
            self.status = 'functioning'
            self.status_positiveness = 2
        elif self.cur_shield > self.max_shield.value() * 2 / 4:
            self.status = 'slightly damaged'
            self.status_positiveness = 1
        elif self.cur_shield > self.max_shield.value() * 1 / 4:
            self.status = 'damaged'
            self.status_positiveness = 0
        elif self.cur_shield > 0:
            self.status = 'severely damaged'
            self.status_positiveness = -1
        else:
            self.status = 'offline'
            self.status_positiveness = -2

    def info(self):
        return [0, self.cur_shield / self.max_shield.value(), 0, self.name, self.status,
                status_color(self.status_positiveness)]

    def charge(self, shield):
        self.cur_shield = clamp(self.cur_shield + shield, self.max_shield.value(), 0)
        self.set_info()

    def damage(self, damage):
        if damage > self.cur_shield:
            remnant = damage - self.cur_shield
            self.cur_shield = 0
            self.set_info()
            return remnant
        else:
            self.cur_shield -= damage
            self.set_info()
            return 0


class Generator(ShipFacility):
    def __init__(self, name, icon, energy_prod):
        super(Generator, self).__init__(name, icon)
        self.energy_prod = energy_prod
        self.energy_prod.set_facility(self)
        self.upgradables = [self.energy_prod]
        self.status = 'functioning'
        self.status_positiveness = 2

    def update(self, delta_time):
        self.ship.give_energy(self.energy_prod.value() * delta_time)


class EnergyStorage(ShipFacility):
    def __init__(self, name, icon, max_energy):
        super().__init__(name, icon)
        self.max_energy = max_energy
        self.max_energy.set_facility(self)
        self.upgradables = [self.max_energy]
        self.energy = 0

    def add(self, amount):
        self.energy += amount
        if self.energy > self.max_energy.value():
            self.energy = self.max_energy.value()


class SpaceFoldStabilizer(ShipFacility):
    def __init__(self, left_border, right_border, coef, length, max_speed):
        super().__init__(' ', '')
        self.left_sprite = None
        self.right_sprite = None
        self.showable = False
        self.length = length
        self.left = left_border
        self.right = right_border
        self.width = self.right - self.left
        self.coef = coef
        self.max_speed = max_speed

    def set_flight(self, flight):
        super(SpaceFoldStabilizer, self).set_flight(flight)
        self.left_sprite = self.flight.left_border
        self.right_sprite = self.flight.right_border

    def reflect(self):
        self.ship.current_speed *= -1 / 3

    def update(self, delta_time):
        x = self.ship.ship_sprite.center_x - self.left
        antix = self.right - self.ship.ship_sprite.center_x
        left_force = 0
        right_force = 0
        if x < self.length:
            self.left_sprite.alpha = (1 - x / self.length) * 225
            left_force = 1 / (x * x / 1250 + x / 25 + 1) * self.coef
        else:
            self.left_sprite.alpha = 0
        if antix < self.length:
            self.right_sprite.alpha = (1 - antix / self.length) * 225
            right_force = - 1 / (antix ** 2 / 1250 + antix / 25 + 1) * self.coef
        else:
            self.right_sprite.alpha = 0
        total_force = left_force + right_force
        self.ship.add_force(clamp(total_force, 2000, -2000))
        self.ship.add_force(total_force)
        self.ship.current_speed *= 0.99
        if x > self.width:
            self.ship.ship_sprite.center_x = self.right - 1
            self.reflect()

        if x < 0:
            self.ship.ship_sprite.center_x = self.left + 1

            self.reflect()
        self.ship.current_speed = clamp(self.ship.current_speed, self.max_speed, -self.max_speed)


class SideEngines(ShipFacility):
    def __init__(self, force):
        super(SideEngines, self).__init__(' ', '')
        self.left_pressed = False
        self.right_pressed = False
        self.showable = False
        self.force = force

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.left_pressed = True

        if symbol == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.left_pressed = False

        if symbol == arcade.key.D:
            self.right_pressed = False

    def update(self, delta_time):
        if self.left_pressed:
            self.ship.add_force(-self.force)
        if self.right_pressed:
            self.ship.add_force(self.force)


class Ship:
    def __init__(self, ship_sprite, main_weapon, energy_storage, shield_capacitor, facilities, max_hp, damage_sound):
        # sprites
        self.ship_sprite = ship_sprite
        self.sprites = arcade.SpriteList()
        self.sprites.append(ship_sprite)

        # health
        self.max_hp = max_hp
        self.hp = self.max_hp

        # movement
        self.total_force = 0
        self.current_speed = 0

        # flight_info
        self.flight = None

        # weapon
        self.main_weapon = main_weapon
        self.main_weapon.set_ship(self)

        # energy
        self.energy_storage = energy_storage
        self.energy_storage.add(500)
        self.energy_storage.set_ship(self)

        # shield
        self.shield_capacitor = shield_capacitor
        self.shield_capacitor.set_ship(self)

        # facilities
        self.facilities = facilities
        self.facilities.append(self.main_weapon)
        self.facilities.append(self.energy_storage)
        self.facilities.append(self.shield_capacitor)

        # setup
        self.set_ship()

        # sounds
        self.damage_sound = damage_sound

        # inventory
        self.credits = 0
        self.scraps = 0

    def add_scraps(self, scraps):
        self.scraps += scraps
        if self.scraps < 0:
            self.scraps = 0

    def  add_credits(self, credits):
        self.credits += credits
        if self.credits < 0:
            self.credits = 0

    def collide(self, _object):
        if _object.type in ['asteroid', 'missile']:
            self.damage(_object.damage)

    def damage(self, damage):
        remnant = self.shield_capacitor.damage(damage)
        self.hp -= remnant
        arcade.play_sound(self.damage_sound)

    def repair(self):
        self.hp = self.max_hp

    def recharge(self):
        self.energy_storage.energy = self.max_energy()

    def recharge_shields(self):
        self.shield_capacitor.cur_shield = self.shield_capacitor.max_shield.value()

    def give_energy(self, energy):
        self.energy_storage.add(energy)

    def energy(self):
        return self.energy_storage.energy

    def max_energy(self):
        return self.energy_storage.max_energy.value()

    def on_key_press(self, symbol: int, modifiers: int):
        for facility in self.facilities:
            facility.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        for facility in self.facilities:
            facility.on_key_release(symbol, modifiers)

    def move(self, delta_time):
        self.ship_sprite.center_x += self.current_speed * delta_time
        self.ship_sprite.angle = 180 / math.pi * math.atan(-self.current_speed / 750)

    def draw(self):
        self.sprites.draw()

    def update(self, delta_time):
        self.result_force(delta_time)
        for facility in self.facilities:
            facility.update(delta_time)
        self.move(delta_time)

    def set_ship(self):
        for facility in self.facilities:
            facility.set_ship(self)

    def set_flight(self, flight):
        self.flight = flight
        for facility in self.facilities:
            facility.set_flight(self.flight)

    def spawn(self, x, y):
        self.ship_sprite.center_x = x
        self.ship_sprite.center_y = y

    def add_force(self, force):
        self.total_force += force

    def result_force(self, delta_time):
        self.current_speed += self.total_force * delta_time
        self.total_force = 0