import arcade
import random
import math

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
        self.root.set_scene(Flight(self.root.player, self.root.width, self.root.height, 360, 1920 - 360, 200, 1, 500))

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
            self.root.set_scene(Flight(self.root.player, self.root.width, self.root.height, 360, 1920 - 360, 500, 1,
                                       200))
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
        self.health_bar = GUIBar("sprites/health_bar/health_bar_")
        self.energy_bar = GUIBar("sprites/energy_bar/energy_bar_")
        self.left_gui = GUIIdle("sprites/left_gui.png")
        self.right_gui = GUIIdle("sprites/right_gui.png")
        self.left_border = GUIMovable("sprites/stab_border_left.png", 50, self.height)
        self.right_border = GUIMovable("sprites/stab_border_right.png", 50, self.height)

    def clear_state(self):
        self.state = ''

    def gui_setup(self):
        self.health_bar.set_position(5.5 * 120, 1.0 * 120)
        self.energy_bar.set_position(10.5 * 120, 1.0 * 120)
        self.left_gui.set_position(2 * 120, 4.5 * 120)
        self.right_gui.set_position(14 * 120, 4.5 * 120)
        self.left_border.set_position(4 * 120, 4.5 * 120)
        self.right_border.set_position(12 * 120, 4.5 * 120)

    def gui_update(self):
        self.left_border.draw()
        self.right_border.draw()
        self.health_bar.draw()
        self.energy_bar.draw()
        self.left_gui.draw()
        self.right_gui.draw()

    def gui_draw(self):
        self.left_border.draw()
        self.right_border.draw()
        self.health_bar.draw()
        self.energy_bar.draw()
        self.left_gui.draw()
        self.right_gui.draw()

    def on_draw(self):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.Q:
            app.close()
        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.player.on_key_release(symbol, modifiers)


class Flight(Scene):
    def __init__(self, player, width, height, left_spawn_zone, right_spawn_zone, base_speed, acceleration, length):
        super().__init__(player, width, height)
        self.left_spawn = left_spawn_zone
        self.right_spawn = right_spawn_zone
        self.health_bar = GUIBar("sprites/health_bar/health_bar_")
        self.energy_bar = GUIBar("sprites/energy_bar/energy_bar_")
        self.left_gui = GUIIdle("sprites/left_gui.png")
        self.right_gui = GUIIdle("sprites/right_gui.png")
        self.left_border = GUIMovable("sprites/stab_border_left.png", 50, self.height)
        self.right_border = GUIMovable("sprites/stab_border_right.png", 50, self.height)
        self.state = 'flying'
        self.delta_time = 1
        self.length = length
        self.cur_len = 0
        self.controls = None
        self.enemy_template = None
        self.spawn_timer = Timer(0.5, self.spawn_enemy)
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.sprite_setup()
        self.controls_setup()
        self.enemy_setup()
        self.gui_setup()
        self.speed = base_speed
        self.base_speed = base_speed
        self.acceleration = acceleration
        self.acc_timer = Timer(1, self.accelerate)

    def accelerate(self):
        self.speed += self.acceleration

    def enemy_setup(self):
        self.enemy_template = Enemy("sprites/asteroid.png", 1.0, 5, 1, 10)
        self.enemy_template.set_position(-50, -50)

    def controls_setup(self):
        self.controls = Controls(arcade.key.A, arcade.key.D, arcade.key.SPACE)

    def sprite_setup(self):
        self.player_setup()

    def player_setup(self):
        self.player.set_flight(self)
        self.player.spawn(8 * 120, 3.5 * 120)

    """ overridden methods of Scene class """

    def on_draw(self):
        arcade.start_render()
        self.all_sprites.draw()
        self.player.draw()
        self.bullets.draw()
        arcade.draw_text(str(1 / self.delta_time), 400, 500, (0, 0, 0))
        self.gui_draw()

    def on_update(self, delta_time: float):
        self.all_sprites.update()
        self.gui_update()
        self.spawn_timer.update(delta_time)
        self.check_collision_bullet_enemy()
        self.check_collision_enemy_player()
        self.acc_timer.update(delta_time)
        self.update_enemies_speed(delta_time)
        self.player.update(delta_time)
        self.move_bullets(delta_time)
        self.delta_time = delta_time
        self.spawn_timer.trigger_time = 50 / self.speed
        self.cur_len = clamp(self.cur_len + self.speed * delta_time / 25, self.length, 0)
        self.health_bar.upd(self.player.hp / self.player.max_hp)
        self.energy_bar.upd(self.player.energy_storage.energy / self.player.energy_storage.max_energy.value())
        self.left_border.move(delta_time)
        self.right_border.move(delta_time)
        if self.cur_len == self.length:
            self.state = 'flight_ended_victory'
        if self.player.hp <= 0:
            self.state = 'flight_ended_loss'

    """ methods for in-game actions """

    """ update methods """

    def update_enemies_speed(self, delta_time):
        for enemy in self.enemies:
            enemy.update_speed(self.speed * delta_time)

    def move_bullets(self, delta_time):
        for bullet in self.bullets:
            bullet.move(delta_time)

    """ spawn methods """

    def spawn_enemy(self):
        new_enemy = self.enemy_template.copy()
        new_enemy.center_x = random.randint(self.left_spawn, self.right_spawn)
        new_enemy.center_y = self.height + 50
        new_enemy.angle_speed = random.randint(-100, 100) / 10
        self.all_sprites.append(new_enemy)
        self.enemies.append(new_enemy)
        del new_enemy

    """ collision check methods """

    def check_collision_bullet_enemy(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                if arcade.check_for_collision(bullet, enemy):
                    bullet.collide(enemy)

    def check_collision_enemy_player(self):
        for enemy in self.enemies:
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
        arcade.draw_text(str(1 / self.delta_time), 400, 500, (0, 0, 0))


class Loss(Scene):
    def __init__(self, width, health, player):
        super(Loss, self).__init__(width, health, player)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text('you lost lost lmao', 500, 500, (0, 0, 0))


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
        arcade.draw_text('Welcome to upgrade hangar!', 500, 500, (0, 0, 0))
        for i in range(len(self.upgradables)):
            upgradable = self.upgradables[i]
            arcade.draw_text(upgradable.upgrade_info(), 500, 480 - 20 * i, (0, 0, 0))


""" utilities """


class Timer:
    def __init__(self, time, func):
        self.trigger_time = time
        self.current_time = 0
        self.func = func

    def update(self, delta_time):
        self.current_time += delta_time
        if self.current_time >= self.trigger_time:
            self.current_time = 0
            self.func()

    def refresh(self):
        self.current_time = 0


class Controls:
    def __init__(self, right, left, shoot):
        self.right = right
        self.left = left
        self.shoot = shoot


""" gui """


class GUIBar(arcade.Sprite):
    def __init__(self, directory: str):
        super(GUIBar, self).__init__(directory + '13' + '.png')
        for i in range(13):
            new_texture = arcade.load_texture(directory + str(12 - i) + '.png')
            self.textures.append(new_texture)

    def upd(self, rel_value):
        index = 13 - round(rel_value * 13)
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


""" enemies """


class Enemy(arcade.Sprite):
    def __init__(self, fname, scale, speed, angle_speed, damage):
        super().__init__(fname, scale)
        self.fname = fname
        self.scale = scale
        self.speed = speed
        self.angle_speed = angle_speed
        self.damage = damage

    def update_speed(self, new_speed):
        self.speed = new_speed
        self.change_y = -new_speed

    def update(self):
        super().update()
        self.angle += self.angle_speed
        if self.center_x < -10:
            self.destroy()

    def copy(self):
        new_enemy = Enemy(self.fname, self.scale, self.speed, self.angle_speed, self.damage)
        return new_enemy

    def destroy(self):
        self.remove_from_sprite_lists()
        del self


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


class Bullet(arcade.Sprite):
    def __init__(self, fname, scale, speed, max_collisions=1, on_collision=0):
        self.scale_ = scale
        self.fname = fname
        self.speed = speed
        self.on_collision = on_collision
        self.collisions = 0
        self.max_collisions = max_collisions
        super().__init__(fname, scale)

    def copy(self):
        return Bullet(self.fname, self.scale_, self.speed, self.on_collision)

    def move(self, delta_time):
        self.center_x += -self.speed * math.sin(math.radians(self.angle)) * delta_time
        self.center_y += self.speed * math.cos(math.radians(self.angle)) * delta_time

    def collide(self, enemy):
        if self.on_collision == 0:
            enemy.destroy()
            self.collisions += 1
            if self.collisions == self.max_collisions:
                self.last_collision()

    def last_collision(self):
        if self.on_collision <= 0:
            self.destroy()

    def destroy(self):
        self.remove_from_sprite_lists()
        del self


class Weapon(ShipFacility):
    def __init__(self):
        super(Weapon, self).__init__()


class ShootingWeapon(Weapon):
    def __init__(self, bullet_sprite, reload_time, energy_cost, key):
        # parent class init
        super().__init__()

        # keys
        self.key = key

        # sprites
        self.bullet_sprite = bullet_sprite

        # shoot info
        self.reload_time = reload_time
        self.energy_cost = energy_cost

        # upgrade info
        self.upgradables = [self.reload_time, self.energy_cost]

        # time
        self.time_since_last_shoot = 0

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
            self.flight.bullets.append(new_bullet)


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
        self.energy_storage.set_ship(self)
        self.energy = 0

        # facilities
        self.facilities = facilities
        self.facilities.append(self.main_weapon)
        self.facilities.append(self.energy_storage)

        # setup
        self.set_ship()

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

default_player_sprite = arcade.Sprite("sprites/ship.png")
default_bullet = Bullet("sprites/bullet.png", 1.0, 250, 1, 1)
default_gun = ShootingWeapon(default_bullet, UpgradableValue([2, 0.5], 'reload'), ConstantValue(0), arcade.key.SPACE)
default_super_bullet = Bullet("sprites/super_bullet.png", 1.0, 200, 1, 0)
default_super_gun = ShootingWeapon(default_super_bullet, ConstantValue(0), ConstantValue(25), arcade.key.W)
default_generator = Generator(UpgradableValue([5, 10], 'energy prod'))
default_energy_storage = EnergyStorage(UpgradableValue([50, 500], 'energy capacity'))
default_stabilizer = SpaceFoldStabilizer(360, 1920 - 360, 1500, 300, 750)
default_side_engines = SideEngines(250)
default_player = Ship(default_player_sprite, default_gun, default_energy_storage,
                      [default_generator, default_super_gun, default_stabilizer, default_side_engines], 500)
default_timeline = NodeTimeLine()

app = App(1920, 1080, 'Arcade')

arcade.run()
