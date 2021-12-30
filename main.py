import arcade
import random


class Scene:
    def __init__(self):
        pass

    def on_draw(self):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        pass


class Flight(Scene):
    def __init__(self, base_speed, acceleration):
        super().__init__()
        self.delta_time = 1
        self.width = 600
        self.height = 600
        self.player = None
        self.controls = None
        self.enemy_template = None
        self.spawn_timer = Timer(0.5, self.spawn_enemy)
        self.all_sprites = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.sprite_setup()
        self.controls_setup()
        self.enemy_setup()
        self.speed = base_speed
        self.base_speed = base_speed
        self.acceleration = acceleration
        self.acc_timer = Timer(1, self.accelerate)

    def accelerate(self):
        self.speed += self.acceleration

    def enemy_setup(self):
        self.enemy_template = Enemy("sprites/asteroid.gif", 2.0, 5, 1, 10)
        self.enemy_template.center_x = -50
        self.enemy_template.center_y = -50

    def controls_setup(self):
        self.controls = Controls(arcade.key.A, arcade.key.D, arcade.key.SPACE)

    def sprite_setup(self):
        self.player_setup()

    def player_setup(self):
        self.player = default_player
        self.player.set_flight(self)
        self.player.center_x = self.width / 2
        self.player.center_y = 20
        self.player.spawn(self.width / 2, 20)

    """ overridden methods of Scene class """

    def on_key_press(self, symbol: int, modifiers: int):
        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.player.on_key_release(symbol, modifiers)

    def on_draw(self):
        arcade.start_render()
        self.all_sprites.draw()
        self.player.draw()
        self.bullets.draw()
        arcade.draw_text(str(1 / self.delta_time), 500, 500, (0, 0, 0))
        arcade.draw_text(str(self.player.hp), 500, 520, (0, 0, 0))
        arcade.draw_text(str(self.player.right_pressed), 500, 540, (0, 0, 0))
        arcade.draw_text(str(self.player.left_pressed), 500, 560, (0, 0, 0))
        arcade.draw_text(str(self.player.main_weapon.reload_time_left()), 500, 580, (0, 0, 0))
        arcade.draw_text(str(self.player.energy), 500, 408, (0, 0, 0))

    def on_update(self, delta_time: float):
        self.all_sprites.update()
        self.spawn_timer.update(delta_time)
        self.check_collision_bullet_enemy()
        self.check_collision_enemy_player()
        self.acc_timer.update(delta_time)
        self.update_enemies_speed(delta_time)
        self.player.update(delta_time)
        self.move_bullets(delta_time)
        self.delta_time = delta_time

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
        new_enemy.center_x = random.randint(0, self.width)
        new_enemy.center_y = self.height - 50
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
            if arcade.check_for_collision(enemy, self.player.player_sprite):
                enemy.destroy()
                self.player.damage(enemy.damage)


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


class Bullet(arcade.Sprite):
    def __init__(self, fname, scale, speed, on_collision=0):
        self.scale_ = scale
        self.fname = fname
        self.speed = speed
        self.on_collision = on_collision
        self.collisions = 0
        super().__init__(fname, scale)

    def copy(self):
        return Bullet(self.fname, self.scale_, self.speed, self.on_collision)

    def move(self, delta_time):
        self.center_y += self.speed * delta_time

    def collide(self, enemy):
        if self.on_collision == 0:
            self.destroy()
            enemy.destroy()
            print('bullet destroyed')
        elif self.on_collision == 1:
            enemy.destroy()
            self.collisions += 1

    def destroy(self):
        self.remove_from_sprite_lists()
        del self


class Weapon:
    def __init__(self, bullet_sprite, reload_time, energy_cost):
        # flight
        self.flight = None

        # ship
        self.ship = None

        # sprites
        self.bullet_sprite = bullet_sprite

        # shoot info
        self.reload_time = reload_time
        self.energy_cost = energy_cost

        # time
        self.time_since_last_shoot = 0

    def set_flight(self, flight: Flight):
        self.flight = flight

    def set_ship(self, ship):
        self.ship = ship

    def update(self, delta_time):
        self.time_since_last_shoot += delta_time

    def reload_time_left(self):
        if self.time_since_last_shoot >= self.reload_time:
            return 0
        else:
            return self.reload_time - self.time_since_last_shoot

    def shoot(self):
        if self.reload_time_left() <= 0 and self.ship.energy >= self.energy_cost:
            self.ship.energy -= self.energy_cost
            self.time_since_last_shoot = 0
            new_bullet = self.bullet_sprite.copy()
            new_bullet.center_x = self.ship.player_sprite.center_x
            new_bullet.center_y = self.ship.player_sprite.center_y
            self.flight.bullets.append(new_bullet)


class Player:
    def __init__(self, player_sprite, main_weapon, super_weapon, max_hp, base_side_speed, energy_flow):
        # sprites
        self.player_sprite = player_sprite
        self.sprites = arcade.SpriteList()
        self.sprites.append(player_sprite)

        # health
        self.max_hp = max_hp
        self.hp = self.max_hp

        # movement
        self.base_side_speed = base_side_speed
        self.cur_side_speed = base_side_speed
        self.left_pressed = False
        self.right_pressed = False

        # flight_info
        self.flight = None

        # weapon
        self.main_weapon = main_weapon
        self.main_weapon.set_ship(self)
        self.super_weapon = super_weapon
        self.super_weapon.set_ship(self)

        # energy
        self.energy_flow = energy_flow
        self.energy = 0

    def damage(self, damage):
        self.hp -= damage

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.left_pressed = True

        if symbol == arcade.key.D:
            self.right_pressed = True

        if symbol == arcade.key.SPACE:
            self.main_weapon.shoot()

        if symbol == arcade.key.W:
            self.super_weapon.shoot()

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.left_pressed = False

        if symbol == arcade.key.D:
            self.right_pressed = False

    def move(self, delta_time):
        self.cur_side_speed = self.base_side_speed * delta_time
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.center_x -= self.cur_side_speed

        if self.right_pressed and not self.left_pressed:
            self.player_sprite.center_x += self.cur_side_speed

    def draw(self):
        self.sprites.draw()

    def update(self, delta_time):
        self.main_weapon.update(delta_time)
        self.energy += delta_time * self.energy_flow
        self.move(delta_time)

    def set_flight(self, flight):
        self.flight = flight
        self.main_weapon.set_flight(self.flight)
        self.super_weapon.set_flight(self.flight)

    def spawn(self, x, y):
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y


class App(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.WHITE)
        self.set_update_rate(1/40)
        self.set_vsync(True)
        self.scene = Flight(100, 5)

    def on_key_press(self, symbol: int, modifiers: int):
        self.scene.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.scene.on_key_release(symbol, modifiers)

    def on_draw(self):
        self.scene.on_draw()

    def on_update(self, delta_time: float):
        self.scene.on_update(delta_time)


"""global variables"""
default_player_sprite = arcade.Sprite("sprites/ship.gif")
default_bullet = Bullet("sprites/bullet.gif", 1.0, 250, 0)
default_gun = Weapon(default_bullet, 0.5, 0)
default_super_bullet = Bullet("sprites/super_bullet.gif", 1.0, 200, 1)
default_super_gun = Weapon(default_super_bullet, 0, 25)
default_player = Player(default_player_sprite, default_gun, default_super_gun, 100, 250, 5)

app = App(600, 600, 'Arcade')
arcade.run()
