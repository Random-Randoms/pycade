import arcade

from core.Enemies import Asteroid, Missile
from core.Explosion import Explosion
from core.Ship import Bullet, ShootingWeapon, UpgradableValue, ConstantValue, Generator, EnergyStorage, \
    SpaceFoldStabilizer, SideEngines, ShieldCapacitor, Ship

buttons = [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4, arcade.key.KEY_5]
default_explosion = Explosion('sprites/explosion/explosion_1.png', 1.0, 'sounds/sfx_exp_medium7.wav',
                              ['sprites/explosion/explosion_1.png',
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
default_enemy_2 = Missile('sprites/missile/missile_1.png', 1.0, 750, 5, default_explosion,
                          ['sprites/missile/missile_1.png',
                           'sprites/missile/missile_2.png'])
default_player_sprite = arcade.Sprite("sprites/ship.png")
default_bullet = Bullet("sprites/bullet.png", 1.0, 750, 1, 0)
default_gun = ShootingWeapon('Main cannon', 'sprites/icons/icon_cannon.png', default_bullet, UpgradableValue([1, 0.75, 0.5], [100, 150], 'reload'), ConstantValue(0),
                             arcade.key.SPACE, arcade.load_sound('sounds/sfx_wpn_cannon4.wav'), arcade.load_sound('sounds/sfx_wpn_noammo1.wav'))
default_super_bullet = Bullet("sprites/super_bullet.png", 1.0, 500, -1, 0)
default_super_gun = ShootingWeapon('Plasma gun', 'sprites/icons/icon_plasma_gun.png', default_super_bullet, ConstantValue(0),
                                   UpgradableValue([25, 20, 15
                                                    ], [100, 200], 'shoot energy'),
                                   arcade.key.W, arcade.load_sound('sounds/sfx_wpn_laser2.wav'), arcade.load_sound('sounds/sfx_wpn_noammo1.wav'))
default_generator = Generator('Nuclear reactor', 'sprites/icons/generator_icon.png',
                              UpgradableValue([5, 10], [100], 'production'))
default_energy_storage = EnergyStorage('Energy batteries', 'sprites/icons/icon_batteries.png', UpgradableValue([100, 250], [100], 'capacity'))
default_stabilizer = SpaceFoldStabilizer(360, 1920 - 360, 1500, 300, 750)
default_side_engines = SideEngines(250)
default_shield_capacitor = ShieldCapacitor('Shield capacitor', 'sprites/icons/icon_shield.png', UpgradableValue([50, 75, 100, 150], [100, 150, 200], 'shield capacity'))
default_player = Ship(default_player_sprite, default_gun, default_energy_storage, default_shield_capacitor,
                      [default_generator,
                       default_super_gun,
                       default_stabilizer,
                       default_side_engines], 100,
                      arcade.load_sound('sounds/sfx_sounds_error8.wav'))
default_enemy.set_points(((-20, 44), (4, 44), (36, 28), (36, -20), (20, -36), (-20, -36), (-44, -20), (-44, 20)))
default_player_sprite.set_points(((4, 60), (20, 36), (20, -52), (-20, -52), (-20, 36), (-4, 60)))
default_shield_capacitor.charge(25)