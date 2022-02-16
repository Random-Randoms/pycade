import arcade
import copy

from core.Enemies import Asteroid, Missile
from core.Explosion import Explosion
from core.Ship import Bullet, ExplosiveBullet, ClusterBullet, ShootingWeapon, UpgradableValue, ConstantValue, Generator, EnergyStorage, \
    SpaceFoldStabilizer, SideEngines, ShieldCapacitor, Ship
from core.GameObjects import AnimatedSprite
from core.Utilities import cut


class Content:
    def __init__(self):
        self.objects = dict()
        self.ships = []
        self.timelines = []

    def add_object(self, _type, _object):
        self.objects[_type + "." + _object.name] = _object
        if _type == 'timeline':
            self.timelines.append(_object)
        if _type == 'controller':
            _object.set_content(self)

    def get_object(self, _id):
        return copy.deepcopy(self.objects[_id])

    def get_timelines(self):
        return self.timelines


content = Content()


buttons = [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4, arcade.key.KEY_5]
default_explosion = Explosion('explosion', 'sprites/explosion/explosion_1.png', 1.0, 'sounds/sfx_exp_medium7.wav',
                              ['sprites/explosion/explosion_1.png',
                               'sprites/explosion/explosion_2.png',
                               'sprites/explosion/explosion_3.png',
                               'sprites/explosion/explosion_4.png',
                               'sprites/explosion/explosion_5.png',
                               'sprites/explosion/explosion_6.png',
                               'sprites/explosion/explosion_7.png',
                               'sprites/explosion/explosion_8.png'])
asteroid = Asteroid('asteroid', 'sprites/asteroid/asteroid_1.png', 1.0, 0, 10,
                         'sounds/sfx_exp_shortest_soft7.wav', cut('sprites/asteroid/spritesheet (6).png', 1, 5, 5, 1.0))
missile = Missile('missile', 'sprites/missile/missile_1.png', 1.0, 750, 5, default_explosion,
                  ['sprites/missile/missile_1.png',
                           'sprites/missile/missile_2.png'])
pacific_ship = AnimatedSprite('sprites/ship.png', 1 / 2)
pacific_ship.add_state_textures('flying', cut('sprites/ship_2.png', 1, 5, 5, 0.5))
pacific_ship.set_state('flying')
bullet = Bullet("bullet", "sprites/bullet.png", 1.0, 750, 1)
default_gun = ShootingWeapon('Main cannon',
                             'sprites/icons/icon_cannon.png',
                             bullet,
                             UpgradableValue([1, 0.75, 0.5], [100, 150], 'reload',
                                             cut('sprites/icons/icon_reload.png', 2, 3, 6, 0.5)),
                             ConstantValue(0),
                             arcade.key.SPACE,
                             'sounds/sfx_wpn_cannon4.wav',
                             'sounds/sfx_wpn_noammo1.wav')
default_super_bullet = ExplosiveBullet("bomb", "sprites/super_bullet.png", 1.0, 500, 3, default_explosion)
cluster_bullet = ClusterBullet('cluster', "sprites/super_bullet.png", 1.0, 500, 1, bullet, "sounds/sfx_exp_medium6.wav")

default_super_gun = ShootingWeapon('Plasma gun', 'sprites/icons/icon_plasma_gun.png', cluster_bullet,
                                   ConstantValue(0),
                                   UpgradableValue([25, 20, 15
                                                    ], [100, 200], 'shoot energy',
                                                   cut('sprites/icons/icon_reload.png', 2, 3, 6, 0.5)),
                                   arcade.key.W, 'sounds/sfx_wpn_laser2.wav',
                                   'sounds/sfx_wpn_noammo1.wav')
default_generator = Generator('Nuclear reactor', 'sprites/icons/generator_icon.png',
                              UpgradableValue([5, 10], [100], 'production',
                                              cut('sprites/icons/icon_reload.png', 2, 3, 6, 0.5)))
default_energy_storage = EnergyStorage('Energy batteries', 'sprites/icons/icon_batteries.png',
                                       UpgradableValue([100, 250], [100], 'capacity',
                                                       cut('sprites/icons/icon_reload.png', 2, 3, 6, 0.5)))
default_stabilizer = SpaceFoldStabilizer(360, 1920 - 360, 1500, 300, 750)
default_side_engines = SideEngines(200)
default_shield_capacitor = ShieldCapacitor('Shield capacitor', 'sprites/icons/icon_shield.png',
                                           UpgradableValue([50, 75, 100, 150], [100, 150, 200], 'shield capacity',
                                                           cut('sprites/icons/icon_reload.png', 2, 3, 6, 0.5)))
default_player = Ship("pacific", pacific_ship, default_gun, default_energy_storage, default_shield_capacitor,
                      [default_generator,
                       default_super_gun,
                       default_stabilizer,
                       default_side_engines], 100,
                       'sounds/sfx_sounds_error8.wav')
asteroid.set_points(((-20, 44), (4, 44), (36, 28), (36, -20), (20, -36), (-20, -36), (-44, -20), (-44, 20)))
pacific_ship.set_points(((4, 60), (20, 36), (20, -52), (-20, -52), (-20, 36), (-4, 60)))
default_shield_capacitor.charge(25)

content.add_object("ship", default_player)
content.add_object("enemy", asteroid)
content.add_object("enemy", missile)
