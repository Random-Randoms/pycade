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

    # load methods

    def load_picture(self, filename):
        file = open(filename, "r")
        data = file.readlines()
        file.close()
        picture_name = data[0][:-1]
        picture_path = data[1][:-1]
        self.add_object('picture', picture_path, picture_name)

    def load_animation(self, filename):
        file = open(filename, "r")
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        spritesheet_id = data[1][:-1]
        rows = int(data[2][:-1])
        columns = int(data[3][:-1])
        amount = int(data[4][:-1])
        scale = float(data[5][:-1])
        spritesheet = self.get_object(spritesheet_id)
        animation = cut(spritesheet, rows, columns, amount, scale)
        self.add_object('animation', animation, name)

    def load_sound(self, filename):
        file = open(filename, "r")
        data = file.readlines()
        file.close()
        sound_name = data[0][:-1]
        sound_path = data[1][:-1]
        self.add_object('sound', sound_path, sound_name)

    def load_missile(self, filename):
        file = open(filename, "r")
        file.readline()
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        scale = float(data[2][:-1])
        speed = int(data[3][:-1])
        damage = int(data[4][:-1])
        explosion_id = data[5][:-1]
        picture = self.get_object(picture_id)
        explosion = self.get_object(explosion_id)
        self.add_object('enemy', Missile(name, picture, scale, speed, damage, explosion))

    def load_asteroid(self, filename):
        file = open(filename, "r")
        file.readline()
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        scale = float(data[2][:-1])
        speed = int(data[3][:-1])
        damage = int(data[4][:-1])
        sound_id = data[5][:-1]
        animation_id = data[6][:-1]
        picture = self.get_object(picture_id)
        sound = self.get_object(sound_id)
        animation = self.get_object(animation_id)
        self.add_object('enemy', Asteroid(name, picture, scale, speed, damage, sound, animation))

    def load_explosion(self, filename):
        file = open(filename, "r")
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        scale = float(data[2][:-1])
        sound_id = data[3][:-1]
        animation_id = data[4][:-1]
        picture = self.get_object(picture_id)
        sound = self.get_object(sound_id)
        animation = self.get_object(animation_id)
        self.add_object('explosion', Explosion(name, picture, scale, sound, animation))

    # add method

    def add_object(self, _type, _object, _name=''):
        if not _name:
            self.objects[_type + "." + _object.name] = _object
        else:
            self.objects[_type + "." + _name] = _object
            print(_type + "." + _name)
        if _type == 'timeline':
            self.timelines.append(_object)
        if _type == 'controller':
            _object.set_content(self)

    # get methods

    def get_object(self, _id):
        return copy.deepcopy(self.objects[_id])

    def get_timelines(self):
        return self.timelines


content = Content()

content.load_picture('content/pic_data/asteroid.txt')
content.load_picture('content/pic_data/sprite_data.txt')
content.load_picture('content/pic_data/explosion_spritesheet.txt')
content.load_picture('content/pic_data/explosion.txt')
content.load_picture('content/pic_data/missile.txt')
content.load_animation('content/animations/aster_dest.txt')
content.load_animation('content/animations/explosion.txt')
content.load_sound('content/sound_data/aster_dest.txt')
content.load_sound('content/sound_data/explosion.txt')
content.load_asteroid('content/enemies/asteroid.txt')
content.load_explosion('content/explosion/yellow.txt')
content.load_missile('content/enemies/missile.txt')

buttons = [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4, arcade.key.KEY_5]
default_explosion = content.get_object('explosion.explosion')
asteroid = content.get_object('enemy.asteroid')

missile = content.get_object('enemy.missile')
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
                             'sound_data/sfx_wpn_cannon4.wav',
                             'sound_data/sfx_wpn_noammo1.wav')
default_super_bullet = ExplosiveBullet("bomb", "sprites/super_bullet.png", 1.0, 500, 3, default_explosion)
cluster_bullet = ClusterBullet('cluster', "sprites/super_bullet.png", 1.0, 500, 1, bullet, "sound_data/sfx_exp_medium6.wav")

default_super_gun = ShootingWeapon('Plasma gun', 'sprites/icons/icon_plasma_gun.png', cluster_bullet,
                                   ConstantValue(0),
                                   UpgradableValue([25, 20, 15
                                                    ], [100, 200], 'shoot energy',
                                                   cut('sprites/icons/icon_reload.png', 2, 3, 6, 0.5)),
                                   arcade.key.W, 'sound_data/sfx_wpn_laser2.wav',
                                   'sound_data/sfx_wpn_noammo1.wav')
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
                       'sound_data/sfx_sounds_error8.wav')
asteroid.set_points(((-20, 44), (4, 44), (36, 28), (36, -20), (20, -36), (-20, -36), (-44, -20), (-44, 20)))
pacific_ship.set_points(((4, 60), (20, 36), (20, -52), (-20, -52), (-20, 36), (-4, 60)))
default_shield_capacitor.charge(25)

content.add_object("ship", default_player)
content.add_object("enemy", asteroid)
content.add_object("enemy", missile)
