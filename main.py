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
        arcade.draw_text(str(1 / self.delta_time), 500, 500, (0, 0, 0))
        arcade.draw_text(str(self.player.hp), 500, 520, (0, 0, 0))
        arcade.draw_text(str(self.player.right_pressed), 500, 540, (0, 0, 0))
        arcade.draw_text(str(self.player.left_pressed), 500, 560, (0, 0, 0))
        arcade.draw_text(str(self.player.reload_time_left), 500, 580, (0, 0, 0))
        arcade.draw_text(str(self.player.energy), 500, 408, (0, 0, 0))

    def on_update(self, delta_time: float):
        self.all_sprites.update()
        self.spawn_timer.update(delta_time)
        self.check_collision_bullet_enemy()
        self.check_collision_enemy_player()
        self.acc_timer.update(delta_time)
        self.update_enemies_speed(delta_time)
        self.player.update(delta_time)
        self.delta_time = delta_time

    """ methods for in-game actions """

    """ update functions """

    def update_enemies_speed(self, delta_time):
        for enemy in self.enemies:
            enemy.update_speed(self.speed * delta_time)

    """ spawn methods """

    def spawn_enemy(self):
        new_enemy = self.enemy_template.copy()
        new_enemy.center_x = random.randint(0, self.width)
        new_enemy.center_y = self.height - 50
        new_enemy.angle_speed = random.randint(-100, 100) / 10
        self.all_sprites.append(new_enemy)
        self.enemies.append(new_enemy)
        del new_enemy

    def shoot(self):
        new_bullet = self.player.spawn_bullet()
        new_bullet.center_x = self.player.player_sprite.center_x
        new_bullet.center_y = self.player.player_sprite.center_y
        self.all_sprites.append(new_bullet)
        self.bullets.append(new_bullet)
        del new_bullet

    def super_shoot(self):
        new_bullet = self.player.spawn_super_bullet()
        new_bullet.center_x = self.player.player_sprite.center_x
        new_bullet.center_y = self.player.player_sprite.center_y
        self.all_sprites.append(new_bullet)
        self.bullets.append(new_bullet)
        del new_bullet

    """ collision check methods """

    def check_collision_bullet_enemy(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                if arcade.check_for_collision(bullet, enemy):
                    bullet.destroy()
                    enemy.destroy()

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
    def __init__(self, fname, scale, speed):
        super().__init__(fname, scale)
        self.fname = fname
        self.scale = scale
        self.speed = speed
        self.change_y = speed

    def update(self):
        super().update()
        if self.center_x > 600:
            self.remove_from_sprite_lists()
            del self

    def copy(self):
        new_bullet = Bullet(self.fname, self.scale, self.speed)
        return new_bullet

    def destroy(self):
        self.remove_from_sprite_lists()
        del self


class Player:
    def __init__(self, player_sprite, bullet_sprite, super_bullet_sprite, max_hp, base_side_speed, gun_reload, energy_flow):
        # sprites
        self.super_bullet_sprite = super_bullet_sprite
        self.player_sprite = player_sprite
        self.bullet_sprite = bullet_sprite
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
        self.cur_time = 0
        self.last_shoot_time = 0
        self.reload_time_left = 0
        self.gun_reload_time = gun_reload
        self.gun_reloaded = True
        self.reload_timer = Timer(self.gun_reload_time, self.reload_gun)
        self.super_bullet_cost = 50

        # energy
        self.energy_flow = energy_flow
        self.energy = 0

    def reload_gun(self):
        self.gun_reloaded = True

    def spawn_bullet(self):
        return self.bullet_sprite.copy()

    def spawn_super_bullet(self):
        return self.super_bullet_sprite.copy()

    def damage(self, damage):
        self.hp -= damage

    def shoot(self):
        if self.gun_reloaded:
            self.flight.shoot()
            self.reload_timer.refresh()
            self.gun_reloaded = False
            self.last_shoot_time = self.cur_time

    def super_shoot(self):
        if self.energy >= self.super_bullet_cost:
            self.energy -= self.super_bullet_cost
            self.flight.super_shoot()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.left_pressed = True

        if symbol == arcade.key.D:
            self.right_pressed = True

        if symbol == arcade.key.SPACE:
            self.shoot()

        if symbol == arcade.key.W:
            self.super_shoot()

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
        self.energy += delta_time * self.energy_flow
        self.cur_time += delta_time
        self.reload_time_left = self.gun_reload_time - (self.cur_time - self.last_shoot_time)
        self.move(delta_time)
        self.reload_timer.update(delta_time)

    def set_flight(self, flight):
        self.flight = flight

    def spawn(self, x, y):
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y


class App(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.WHITE)
        self.set_update_rate(1/60)
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
default_bullet = Bullet("sprites/bullet.gif", 1.0, 25)
default_super_bullet = Bullet("sprites/super_bullet.gif", 1.0, 15)
default_player = Player(default_player_sprite, default_bullet, default_super_bullet, 100, 250, 1, 5)


app = App(600, 600, 'Arcade')
arcade.run()
