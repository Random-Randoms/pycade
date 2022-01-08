import arcade
import random
import math
import copy

""" timelines """


class TimeLine:
    def __init__(self):
        self.root = None

    def set_root(self, root):
        self.root = root

    def start(self):
        pass

    def update(self):
        pass


class NodeTimeLine(TimeLine):
    def __init__(self):
        super(NodeTimeLine, self).__init__()
        self.cur_station = None

    def start(self):
        self.root.set_scene(Flight(self.root.player, self.root.width, self.root.height,
                                   [TimeSpawner(default_enemy, 0.15),
                                    TimeSpawner(default_enemy_2, 1.0)], 360, 1920 - 360, 200, 1, 250))

    def update(self):
        state = self.root.scene.state
        if state == 'flight_ended_victory':
            self.cur_station = Station(self.root.player, self.root.width, self.root.height)
            self.root.set_scene(self.cur_station)
            self.root.scene.clear_state()

        if state == 'flight_ended_loss':
            self.root.set_scene(Loss(self.root.player, self.root.width, self.root.height))
            self.root.scene.clear_state()

        if state == 'ended':
            self.root.set_scene(Flight(self.root.player, self.root.width, self.root.height,
                                       [TimeSpawner(default_enemy, 0.25)], 360, 1920 - 360, 360, 5, 500))
            self.root.scene.clear_state()

        if state == 'back':
            self.root.set_scene(self.cur_station)
            self.root.scene.clear_state()

        if state == 'upgrade':
            self.root.set_scene(UpgradeHangar(self.root.player, self.root.width, self.root.height))
            self.root.scene.clear_state()


""" scenes """


class Scene:
    def __init__(self, player, width, height):
        self.state = ''
        self.player = player
        self.width = width
        self.height = height
        self.delta_time = 1

    def clear_state(self):
        self.state = ''

    def draw_fps(self):
        arcade.draw_text('FPS: ' + str(round(1 / self.delta_time)), 20, self.height - 30, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')

    def on_draw(self):
        pass

    def on_update(self, delta_time: float):
        self.delta_time = delta_time

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.Q:
            app.close()
        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.player.on_key_release(symbol, modifiers)


class Flight(Scene):
    def __init__(self, player, width, height, enemy_spawners, left_spawn_zone, right_spawn_zone, base_speed,
                 acceleration, length):
        super().__init__(player, width, height)

        # GUI
        self.health_bar = GUIBar("sprites/gui/health_bar/health_bar_", 13)
        self.energy_bar = GUIBar("sprites/gui/energy_bar/energy_bar_", 13)
        self.progress_bar = GUIBar('sprites/gui/flight_progress/flight_progress_', 16)
        self.left_gui = GUIIdle("sprites/gui/left_gui.png")
        self.right_gui = GUIIdle("sprites/gui/right_gui.png")
        self.mid_gui = GUIIdle('sprites/gui/mid_gui.png')
        self.left_border = GUIMovable("sprites/gui/stab_border_left.png", 50, self.height)
        self.right_border = GUIMovable("sprites/gui/stab_border_right.png", 50, self.height)

        # spawn borders
        self.left_spawn = left_spawn_zone
        self.right_spawn = right_spawn_zone

        # enemy spawners
        self.enemy_spawners = enemy_spawners
        self.spawners_setup()

        # sprite lists setup
        self.explosions = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.missiles = arcade.SpriteList()
        self.objects = arcade.SpriteList()
        self.move = arcade.SpriteList()

        # objects setup
        self.sprite_setup()
        self.controls_setup()
        self.gui_setup()

        # speed info
        self.speed = base_speed
        self.base_speed = base_speed
        self.acceleration = acceleration
        self.acc_timer = Timer(1, self.accelerate)

        # length info
        self.length = length
        self.cur_len = 0

        # state
        self.state = 'flying'

        # controls
        self.controls = None

    def accelerate(self):
        self.speed += self.acceleration

    """ setup methods"""

    def spawners_setup(self):
        for spawner in self.enemy_spawners:
            spawner.set_flight(self)

    def controls_setup(self):
        self.controls = Controls(arcade.key.A, arcade.key.D, arcade.key.SPACE)

    def gui_setup(self):
        self.health_bar.set_position(5.5 * 120, 1.0 * 120)
        self.energy_bar.set_position(10.5 * 120, 1.0 * 120)
        self.progress_bar.set_position(14.5 * 120, 4.5 * 120)
        self.left_gui.set_position(2 * 120, 4.5 * 120)
        self.right_gui.set_position(14 * 120, 4.5 * 120)
        self.mid_gui.set_position(8 * 120, 1 * 120)
        self.left_border.set_position(4 * 120, 4.5 * 120)
        self.right_border.set_position(12 * 120, 4.5 * 120)

    def sprite_setup(self):
        self.player_setup()

    def player_setup(self):
        self.player.set_flight(self)
        self.player.spawn(8 * 120, 3.5 * 120)

    """ draw methods """

    def gui_draw(self):
        self.left_border.draw()
        self.right_border.draw()
        self.health_bar.draw()
        self.energy_bar.draw()
        self.left_gui.draw()
        self.right_gui.draw()
        self.mid_gui.draw()
        self.progress_bar.draw()

    """ overridden methods of Scene class """

    def on_draw(self):
        arcade.start_render()
        self.enemies.draw()
        self.bullets.draw()
        self.missiles.draw()
        self.explosions.draw()

        self.player.draw()

        self.gui_draw()
        self.draw_fps()

    def on_update(self, delta_time: float):
        # updating gui
        self.gui_update(delta_time)

        # updating timers
        self.update_spawn_timers(delta_time)
        self.acc_timer.update(delta_time)

        # checking collisions
        self.check_collision_objects()
        self.check_collision_player()

        # updating objects
        self.player.update(delta_time)
        self.update_objects(delta_time)

        # moving objects
        self.move_objects(delta_time)

        # updating delta_time
        self.delta_time = delta_time

        # updating current length
        self.cur_len = clamp(self.cur_len + self.speed * delta_time / 100, self.length, 0)

        # updating state
        if self.cur_len == self.length:
            self.state = 'flight_ended_victory'
        if self.player.hp <= 0:
            self.state = 'flight_ended_loss'

    """ update methods """

    def add_object(self, _object):
        self.objects.append(_object)
        if _object.type == 'bullet':
            self.bullets.append(_object)
        elif _object.type == 'missile':
            self.missiles.append(_object)
        elif _object.type == 'asteroid':
            self.enemies.append(_object)
        elif _object.type == 'explosion':
            self.explosions.append(_object)

        if _object.move_by_flight:
            self.move.append(_object)

    def gui_update(self, delta_time):
        self.health_bar.upd(self.player.hp / self.player.max_hp)
        self.energy_bar.upd(self.player.energy_storage.energy / self.player.energy_storage.max_energy.value())
        self.progress_bar.upd(self.cur_len / self.length)
        self.left_border.move(delta_time)
        self.right_border.move(delta_time)

    def update_spawn_timers(self, delta_time):
        for spawner in self.enemy_spawners:
            spawner.update(delta_time)
            spawner.spawn_timer.trigger_time = spawner.frequency * self.speed / self.base_speed

    def update_objects(self, delta_time):
        for _object in self.objects:
            _object.upd(delta_time)

    def move_objects(self, delta_time):
        for _object in self.move:
            _object.move(0, -self.speed * delta_time)

    """ collision check methods """

    def check_collision_objects(self):
        for object_1 in self.objects:
            for object_2 in self.objects:
                if object_1.is_collidable() and object_2.is_collidable():
                    if arcade.check_for_collision(object_1, object_2):
                        object_1.collide(object_2)
                        object_2.collide(object_1)

    def check_collision_player(self):
        for _object in self.objects:
            if _object.is_collidable():
                if arcade.check_for_collision(_object, self.player.ship_sprite):
                    _object.player_collide()
                    self.player.collide(_object)

    def check_collision_missile_asteroid(self):
        for missile in self.missiles:
            for asteroid in self.enemies:
                if asteroid.is_collidable():
                    if arcade.check_for_collision(missile, asteroid):
                        asteroid.destroy()

    def check_collision_bullet_enemy(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                if enemy.is_collidable():
                    if arcade.check_for_collision(bullet, enemy):
                        bullet.collide(enemy)

    def check_collision_enemy_player(self):
        for enemy in self.enemies:
            if enemy.is_collidable():
                if arcade.check_for_collision(enemy, self.player.ship_sprite):
                    enemy.destroy()
                    self.player.damage(enemy.damage)


class Station(Scene):
    def __init__(self, player, width, height):
        super(Station, self).__init__(player, width, height)
        self.delta_time = 1
        self.set_up_player()

    def set_up_player(self):
        self.player.spawn(self.width / 2, 10)

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.KEY_1:
            self.player.hp = self.player.max_hp

        if symbol == arcade.key.KEY_2:
            self.state = 'upgrade'

        if symbol == arcade.key.KEY_3:
            self.state = 'ended'

    def on_update(self, delta_time: float):
        self.delta_time = delta_time

    def on_draw(self):
        arcade.start_render()
        self.player.draw()
        self.draw_fps()


class Loss(Scene):
    def __init__(self, width, health, player):
        super(Loss, self).__init__(width, health, player)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text('you lost lost lmao', 500, 500, (0, 0, 0))
        self.draw_fps()


class UpgradeHangar(Station):
    def __init__(self, width, health, player):
        super(UpgradeHangar, self).__init__(width, health, player)
        self.upgradables = []
        self.set_upgradables()
        print(len(self.upgradables))

    def set_upgradables(self):
        self.upgradables = []
        for facility in self.player.facilities:
            for upgradable in facility.upgradables:
                if upgradable.is_upgradable():
                    self.upgradables.append(upgradable)

    def on_key_press(self, symbol: int, modifiers: int):
        self.set_upgradables()

        if symbol == arcade.key.ESCAPE:
            self.state = 'back'

        if symbol == arcade.key.Q:
            self.player.main_weapon.reload_time.upgrade()

        if symbol == arcade.key.E:
            self.player.energy_storage.max_energy.upgrade()

    def on_draw(self):
        arcade.start_render()
        self.draw_fps()
        for i in range(len(self.upgradables)):
            upgradable = self.upgradables[i]
            arcade.draw_text(upgradable.upgrade_info(), 500, 480 - 20 * i, (0, 0, 0), font_size=20,
                             font_name='fonts/editundo.ttf')


""" utilities """


class Timer:
    def __init__(self, time, func):
        self.trigger_time = time
        self.current_time = 0
        self.func = func
        self.is_running = True

    def update(self, delta_time):
        if self.is_running:
            self.current_time += delta_time
        if self.current_time >= self.trigger_time:
            self.current_time = 0
            self.func()

    def stop(self):
        self.is_running = False
        self.current_time = 0

    def start(self):
        self.is_running = True

    def refresh(self):
        self.current_time = 0


class Controls:
    def __init__(self, right, left, shoot):
        self.right = right
        self.left = left
        self.shoot = shoot


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


""" gui """


class GUIBar(arcade.Sprite):
    def __init__(self, directory: str, amount=13):
        self.amount = amount
        super(GUIBar, self).__init__(directory + str(amount) + '.png')
        for i in range(self.amount):
            new_texture = arcade.load_texture(directory + str(self.amount - 1 - i) + '.png')
            self.textures.append(new_texture)

    def upd(self, rel_value):
        index = self.amount - round(rel_value * self.amount)
        self.set_texture(index)


class GUIIdle(arcade.Sprite):
    def __init__(self, filename):
        super().__init__(filename)


class GUIMovable(arcade.Sprite):
    def __init__(self, filename, speed, __height):
        super().__init__(filename)
        self.speed = speed
        self.__height = __height

    def move(self, delta_time):
        self.center_y += self.speed * delta_time
        if self.center_y >= self.__height:
            self.center_y -= self.__height


""" game objects"""


class GameObject(AnimatedSprite):
    def __init__(self, filename, scale, frequency=1 / 6):
        super(GameObject, self).__init__(filename, scale, frequency)
        self.fname = filename
        self.type = ''
        self._scale = scale
        self.speed_x = 0
        self.speed_y = 0
        self.flight = None
        self.collidable = True
        self.move_by_flight = False

    def move(self, x, y):
        self.center_x += x
        self.center_y += y

    def is_collidable(self):
        return self.collidable

    def collide(self, _object):
        pass

    def player_collide(self):
        pass

    def set_flight(self, flight):
        self.flight = flight

    def complete_destroy(self):
        self.remove_from_sprite_lists()
        del self

    def copy(self):
        return copy.deepcopy(self)


""" explosion """


class Explosion(GameObject):
    def __init__(self, filename, scale, explosion_fnames):
        super(Explosion, self).__init__(filename, scale, 1 / 12)
        self.add_state_fnames('explosion', explosion_fnames)
        self.explosion_fnames = explosion_fnames
        self.set_state('explosion')
        self.type = 'explosion'
        self.destruction_timer = Timer(self.frequency * len(explosion_fnames), self.complete_destroy)

    def upd(self, delta_time):
        super(Explosion, self).upd(delta_time)
        self.destruction_timer.update(delta_time)

    def copy(self):
        return Explosion(self.fname, self.scale, self.explosion_fnames)


""" enemies """


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
        self.speed = speed
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

    def fly_by_angle(self):
        self.speed_x = self.speed * math.cos((self.angle + 90) * math.pi / 180)
        self.speed_y = self.speed * math.sin((self.angle + 90) * math.pi / 180)

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
        self.turn_left(self.angle_speed * delta_time)
        self.center_y += self.speed_y * delta_time
        self.center_x += self.speed_x * delta_time
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

    def set_flight(self, flight: Flight):
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


""" values """


class Value:
    def __init__(self, name=''):
        self._value = None
        self.name = name
        self._upgradable = False

    def is_upgradable(self):
        return self._upgradable

    def value(self):
        return self._value


class ConstantValue(Value):
    def __init__(self, _value, name=''):
        super(ConstantValue, self).__init__(name)
        self._value = _value


class UpgradableValue(Value):
    def __init__(self, variants, name=''):
        super(UpgradableValue, self).__init__(name)
        self._upgradable = True
        self.variants = variants
        self.level = 0
        self._value = variants[self.level]

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
            return 'Upgrade ' + self.name + ' from ' + str(self.value()) + ' to ' + str(self.next_value())


""" facilities"""


class ShipFacility:
    def __init__(self):
        self.upgradables = []
        self.flight = None
        self.ship = None

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


""" weaponry facilities """


class Bullet(GameObject):
    def __init__(self, fname, scale, speed, max_collisions=1, on_collision=0):
        self.speed = speed
        self.on_collision = on_collision
        self.collisions = 0
        self.max_collisions = max_collisions
        super().__init__(fname, scale)
        self.type = 'bullet'

    def upd(self, delta_time):
        self.center_x += -self.speed * math.sin(math.radians(self.angle)) * delta_time
        self.center_y += self.speed * math.cos(math.radians(self.angle)) * delta_time

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
    def __init__(self, reload_time, energy_cost):
        super(Weapon, self).__init__()
        self.reload_time = reload_time
        self.energy_cost = energy_cost
        self.upgradables.append([self.reload_time, self.energy_cost])


class ShootingWeapon(Weapon):
    def __init__(self, bullet_sprite, reload_time, energy_cost, key, sound):
        # parent class init
        super().__init__(reload_time, energy_cost)

        # keys
        self.key = key

        # sprites
        self.bullet_sprite = bullet_sprite

        # time
        self.time_since_last_shoot = 0

        # sounds
        self.shoot_sound = sound

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
            alpha = math.radians(self.ship.ship_sprite.angle)
            spd = self.ship.current_speed
            spd2 = new_bullet.speed
            new_bullet.angle = -math.atan((math.sin(alpha) * spd2 + spd) / (math.cos(alpha) * spd2)) * 180 / math.pi
            new_bullet.speed = math.sqrt((math.sin(alpha) * spd2 + spd) ** 2 + (math.cos(alpha) * spd2) ** 2)
            self.flight.add_object(new_bullet)


""" utility facilities """


class Generator(ShipFacility):
    def __init__(self, energy_prod):
        super(Generator, self).__init__()
        self.energy_prod = energy_prod
        self.upgradables = [self.energy_prod]

    def update(self, delta_time):
        self.ship.give_energy(self.energy_prod.value() * delta_time)


class EnergyStorage(ShipFacility):
    def __init__(self, max_energy):
        super().__init__()
        self.max_energy = max_energy
        self.upgradables = [self.max_energy]
        self.energy = 0

    def add(self, amount):
        self.energy += amount
        if self.energy > self.max_energy.value():
            self.energy = self.max_energy.value()


def clamp(value, _max, _min):
    if value > _max:
        return _max
    elif value < _min:
        return _min
    else:
        return value


class SpaceFoldStabilizer(ShipFacility):
    def __init__(self, left_border, right_border, coef, length, max_speed):
        super().__init__()
        self.left_sprite = None
        self.right_sprite = None
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
        super(SideEngines, self).__init__()
        self.left_pressed = False
        self.right_pressed = False
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


""" ship """


class Ship:
    def __init__(self, ship_sprite, main_weapon, energy_storage, facilities, max_hp):
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
        self.energy = 0

        # facilities
        self.facilities = facilities
        self.facilities.append(self.main_weapon)
        self.facilities.append(self.energy_storage)

        # setup
        self.set_ship()

    def collide(self, _object):
        if _object.type in ['asteroid', 'missile']:
            self.damage(_object.damage)

    def damage(self, damage):
        self.hp -= damage

    def give_energy(self, energy):
        self.energy_storage.add(energy)

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


""" app """


class App(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.WHITE)
        self.timeline = default_timeline
        self.timeline.set_root(self)
        self.player = default_player
        self.set_update_rate(1 / 60)
        self.set_vsync(True)
        self.scene = None
        self.set_fullscreen(True)
        self.timeline.start()

    def on_key_press(self, symbol: int, modifiers: int):
        self.scene.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.scene.on_key_release(symbol, modifiers)

    def on_draw(self):
        self.scene.on_draw()

    def set_scene(self, scene):
        self.scene = scene

    def on_update(self, delta_time: float):
        self.scene.on_update(delta_time)
        self.timeline.update()


"""global variables"""

default_explosion = Explosion('sprites/explosion/explosion_1.png', 1.0, ['sprites/explosion/explosion_1.png',
                                                                         'sprites/explosion/explosion_2.png',
                                                                         'sprites/explosion/explosion_3.png',
                                                                         'sprites/explosion/explosion_4.png',
                                                                         'sprites/explosion/explosion_5.png',
                                                                         'sprites/explosion/explosion_6.png',
                                                                         'sprites/explosion/explosion_7.png',
                                                                         'sprites/explosion/explosion_8.png'])
default_enemy = Asteroid('sprites/asteroid/asteroid_1.png', 1.0, 0, 10,
                         'sounds/sfx_exp_shortest_soft7.wav', ['sprites/asteroid/asteroid_1.png',
                                                                                  'sprites/asteroid/asteroid_2.png',
                                                                                  'sprites/asteroid/asteroid_3.png',
                                                                                  'sprites/asteroid/asteroid_4.png',
                                                                                  'sprites/asteroid/asteroid_5.png'])
default_enemy.set_points(((-20, 44), (4, 44), (36, 28), (36, -20), (20, -36), (-20, -36), (-44, -20), (-44, 20)))
default_enemy_2 = Missile('sprites/missile/missile_1.png', 1.0, 750, 5, default_explosion,
                          ['sprites/missile/missile_1.png',
                           'sprites/missile/missile_2.png'])
default_player_sprite = arcade.Sprite("sprites/ship.png")
default_player_sprite.set_points(((4, 60), (20, 36), (20, -52), (-20, -52), (-20, 36), (-4, 60)))
default_bullet = Bullet("sprites/bullet.png", 1.0, 250, 1, 0)
default_gun = ShootingWeapon(default_bullet, UpgradableValue([2, 0.5], 'reload'), ConstantValue(0), arcade.key.SPACE,
                             arcade.load_sound('sounds/sfx_wpn_cannon4.wav'))
default_super_bullet = Bullet("sprites/super_bullet.png", 1.0, 200, -1, 0)
default_super_gun = ShootingWeapon(default_super_bullet, ConstantValue(0), ConstantValue(25), arcade.key.W,
                                   arcade.load_sound('sounds/sfx_wpn_laser2.wav'))
default_generator = Generator(UpgradableValue([5, 10], 'energy prod'))
default_energy_storage = EnergyStorage(UpgradableValue([100, 250], 'energy capacity'))
default_stabilizer = SpaceFoldStabilizer(360, 1920 - 360, 1500, 300, 750)
default_side_engines = SideEngines(250)
default_player = Ship(default_player_sprite, default_gun, default_energy_storage,
                      [default_generator, default_super_gun, default_stabilizer, default_side_engines], 100)
default_timeline = NodeTimeLine()

app = App(1920, 1080, 'Arcade')
arcade.run()
