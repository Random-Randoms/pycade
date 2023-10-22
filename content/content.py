import arcade
import copy
import os

from core.Enemies import Asteroid, Missile
from core.Explosion import Explosion
from core.Ship import Bullet, ClusterBullet, ShootingWeapon, UpgradableValue, ConstantValue, Generator, EnergyStorage, \
    SpaceFoldStabilizer, SideEngines, ShieldCapacitor, Ship
from core.GameObjects import AnimatedSprite
from core.Utilities import cut


class Content:
    def __init__(self):
        self.objects = dict()
        self.ships = []
        self.timelines = []

    # load methods

    def load_picture(self, file):
        data = file.readlines()
        file.close()
        picture_name = data[0][:-1]
        picture_path = data[1][:-1]
        self.add_object('picture', picture_path, picture_name)

    def load_pictures(self, root_dir):
        data_dir = '/pic_data'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            self.load_picture(file)

    def load_animation(self, file):
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

    def load_animations(self, root_dir):
        data_dir = '/animations'
        files = os.listdir(root_dir + data_dir)
        for filename in files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            self.load_animation(file)

    def load_sound(self, file):
        data = file.readlines()
        file.close()
        sound_name = data[0][:-1]
        sound_path = data[1][:-1]
        self.add_object('sound', sound_path, sound_name)

    def load_sounds(self, root_dir):
        data_dir = '/sound_data'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            self.load_sound(file)

    def load_missile(self, file):
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

    def load_asteroid(self, file):
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

    def load_enemies(self, root_dir):
        data_dir = '/enemies'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            enemy_type = file.readline()[:-1]
            if enemy_type == 'asteroid':
                self.load_asteroid(file)
            else:
                self.load_missile(file)

    def load_explosion(self, file):
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

    def load_explosions(self, root_dir):
        data_dir = '/explosions'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            self.load_explosion(file)

    def load_bullet(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        scale = float(data[2][:-1])
        speed = int(data[3][:-1])
        max_collisions = int(data[4][:-1])
        picture = self.get_object(picture_id)
        self.add_object('bullet', Bullet(name, picture, scale, speed, max_collisions))

    def load_cluster_bullet(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        scale = float(data[2][:-1])
        speed = int(data[3][:-1])
        max_collisions = int(data[4][:-1])
        shard_id = data[5][:-1]
        sound_id = data[6][:-1]
        picture = self.get_object(picture_id)
        shard = self.get_object(shard_id)
        sound = self.get_object(sound_id)
        self.add_object('bullet', ClusterBullet(name, picture, scale, speed, max_collisions, shard, sound))

    def load_bullets(self, root_dir):
        data_dir = '/bullets'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            enemy_type = file.readline()[:-1]
            if enemy_type == 'basic':
                self.load_bullet(file)
                print('loading asteroid')
            elif enemy_type == 'cluster':
                self.load_cluster_bullet(file)
                print('loading missile')

    def load_const_value(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        local_name = data[0][:-1]
        value = int(data[1][:-1])
        self.add_object('value', ConstantValue(value, local_name), name)

    def load_upgradable_value(self, file):
        name = file.readline()[:-1]
        local_name = file.readline()[:-1]
        variants = []
        prices = []
        icons = []
        file.readline()
        cur_line = file.readline()
        while cur_line[0] == ' ':
            variants.append(float(cur_line[4:-1]))
            cur_line = file.readline()
        cur_line = file.readline()
        while cur_line[0] == ' ':
            prices.append(int(cur_line[4:-1]))
            cur_line = file.readline()
        cur_line = file.readline()
        while cur_line[0] == ' ':
            icons.append(self.get_object(cur_line[4:-1]))
            cur_line = file.readline()
        self.add_object('value', UpgradableValue(variants, prices, local_name, icons), name)

    def load_values(self, root_dir):
        data_dir = '/values'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            facility_type = file.readline()[:-1]
            if facility_type == 'const':
                self.load_const_value(file)
            else:
                self.load_upgradable_value(file)
        print('values loaded')

    def load_key(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        key_id = data[1][:-1]
        print(name)
        self.add_object('key', eval(key_id), name)

    def load_keys(self, root_dir):
        data_dir = '/keys'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            self.load_key(file)

    def load_shooting_weapon(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        icon_id = data[1][:-1]
        bullet_id = data[2][:-1]
        reload_id = data[3][:-1]
        energy_cost_id = data[4][:-1]
        key_id = data[5][:-1]
        shoot_sound_id = data[6][:-1]
        error_sound_id = data[7][:-1]
        icon = self.get_object(icon_id)
        bullet = self.get_object(bullet_id)
        reload = self.get_object(reload_id)
        energy_cost = self.get_object(energy_cost_id)
        key = self.get_object(key_id)
        shoot_sound = self.get_object(shoot_sound_id)
        error_sound = self.get_object(error_sound_id)
        self.add_object('facility', ShootingWeapon(name, icon, bullet, reload, energy_cost, key, shoot_sound,
                                                   error_sound))

    def load_facilities(self, root_dir):
        data_dir = '/facilities'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            facility_type = file.readline()[:-1]
            if facility_type == 'shooting_weapon':
                self.load_shooting_weapon(file)
            elif facility_type == 'cluster':
                self.load_cluster_bullet(file)
            elif facility_type == 'generator':
                self.load_generator(file)
            elif facility_type == 'energy_storage':
                self.load_energy_storage(file)
            elif facility_type == 'side_engines':
                self.load_side_engines(file)
            elif facility_type == 'space_fold_stabiliser':
                self.load_space_fold_stabiliser(file)
            elif facility_type == 'shield_capacitor':
                self.load_shield_capacitor(file)

    def load_generator(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        energy_prod_id = data[2][:-1]
        picture = self.get_object(picture_id)
        energy_prod = self.get_object(energy_prod_id)
        self.add_object('facility', Generator(name, picture, energy_prod))

    def load_energy_storage(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        energy_capacity_id = data[2][:-1]
        picture = self.get_object(picture_id)
        energy_capacity = self.get_object(energy_capacity_id)
        self.add_object('facility', EnergyStorage(name, picture, energy_capacity))

    def load_shield_capacitor(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        shield_capacity_id = data[2][:-1]
        picture = self.get_object(picture_id)
        shield_capacity = self.get_object(shield_capacity_id)
        self.add_object('facility', ShieldCapacitor(name, picture, shield_capacity))

    def load_side_engines(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        force = int(data[1][:-1])
        self.add_object('facility', SideEngines(force), name)

    def load_space_fold_stabiliser(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        left = int(data[1][:-1])
        right = int(data[2][:-1])
        coef = int(data[3][:-1])
        length = int(data[4][:-1])
        max_speed = int(data[5][:-1])
        self.add_object('facility', SpaceFoldStabilizer(left, right, coef, length, max_speed), name)

    def load_ship_sprite(self, file):
        data = file.readlines()
        file.close()
        name = data[0][:-1]
        picture_id = data[1][:-1]
        scale = float(data[2][:-1])
        animation_id = data[3][:-1]
        picture = self.get_object(picture_id)
        animation = self.get_object(animation_id)
        ship_sprite = AnimatedSprite(picture, scale)
        ship_sprite.add_state_textures("flying", animation)
        ship_sprite.set_state("flying")
        self.add_object('ship_sprite', ship_sprite, name)

    def load_ship_sprites(self, root_dir):
        data_dir = '/ship_sprites'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            self.load_ship_sprite(file)

    def load_ship(self, file):
        name = file.readline()[:-1]
        ship_sprite_id = file.readline()[:-1]
        main_cannon_id = file.readline()[:-1]
        energy_storage_id = file.readline()[:-1]
        shields_id = file.readline()[:-1]
        damage_sound_id = file.readline()[:-1]
        max_hp = int(file.readline()[:-1])
        facilities = []
        file.readline()
        cur_line = file.readline()
        while cur_line[0] == ' ':
            facilities.append(self.get_object(cur_line[4:-1]))
            cur_line = file.readline()
        file.close()
        ship_sprite = self.get_object(ship_sprite_id)
        main_cannon = self.get_object(main_cannon_id)
        energy_storage = self.get_object(energy_storage_id)
        shields = self.get_object(shields_id)
        damage_sound = self.get_object(damage_sound_id)
        print(name)
        print(len(facilities))
        self.add_object("ship", Ship(name, ship_sprite, main_cannon, energy_storage, shields, facilities, max_hp, damage_sound))

    def load_ships(self, root_dir):
        data_dir = '/ships'
        pic_files = os.listdir(root_dir + data_dir)
        for filename in pic_files:
            file = open(root_dir + data_dir + '/' + filename, "r")
            self.load_ship(file)

    def load_all(self):
        root_dir = './content'
        self.load_pictures(root_dir)
        self.load_animations(root_dir)
        self.load_sounds(root_dir)
        self.load_explosions(root_dir)
        self.load_enemies(root_dir)
        self.load_bullets(root_dir)
        self.load_values(root_dir)
        self.load_keys(root_dir)
        self.load_facilities(root_dir)
        self.load_ship_sprites(root_dir)
        print('ggg')
        self.load_ships(root_dir)
        print('ggg')

    # add method

    def add_object(self, _type, _object, _name=None):
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

content.load_all()

buttons = [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4, arcade.key.KEY_5]
default_explosion = content.get_object('explosion.explosion')

pacific_ship = content.get_object('ship_sprite.pacific')
pacific_ship.set_points(((4, 60), (20, 36), (20, -52), (-20, -52), (-20, 36), (-4, 60)))

bullet = content.get_object('bullet.bullet')
default_gun = content.get_object('facility.main cannon')
cluster_bullet = content.get_object('bullet.cluster')
default_super_gun = content.get_object('facility.plasma cannon')
default_generator = content.get_object('facility.nuclear reactor')
default_energy_storage = content.get_object('facility.energy batteries')
default_stabilizer = content.get_object('facility.space_fold_stabiliser')
default_side_engines = content.get_object('facility.side_engines')
default_shield_capacitor = content.get_object('facility.shield capacitor')


#default_player = content.get_object("ship.pacific")#Ship("pacific", pacific_ship, default_gun, default_energy_storage, default_shield_capacitor,
                      #[default_generator,
                      # default_super_gun,
                      # default_stabilizer,
                      # default_side_engines], 100,
                      # 'sound_data/sfx_sounds_error8.wav')


#default_shield_capacitor.charge(25)
