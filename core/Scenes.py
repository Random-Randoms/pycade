import arcade

from core.GUI import GUIIdle, GUIText, GUIBar, GUIMovable, GUIFacilityInfo, GUITextUpgrade
from core.Ship import Ship
from core.Utilities import Timer, Controls, clamp, choose_random_subset, ParamTimer
from content.content import buttons, content


class Scene:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.delta_time = 1
        self.fps_counter = 0
        self.state = ''

    def clear_state(self):
        self.state = ''

    def draw_fps(self):
        arcade.draw_text('FPS: ' + str(round(1 / self.delta_time)), 20, self.height - 30, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')

    def on_draw(self):
        pass

    def on_update(self, delta_time: float):
        self.fps_counter += 1
        if self.fps_counter >= 25:
            self.delta_time = delta_time
            self.fps_counter = 0

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.Q:
            self.state = 'close'

    def on_key_release(self, symbol: int, modifiers: int):
        pass


class GameScene(Scene):
    def __init__(self, player, width, height):
        super(GameScene, self).__init__(width, height)
        self.player = player

    def on_key_press(self, symbol: int, modifiers: int):
        super(GameScene, self).on_key_press(symbol, modifiers)
        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.player.on_key_release(symbol, modifiers)


class MainMenu(Scene):
    def __init__(self, width, height):
        super(MainMenu, self).__init__(width, height)
        self.logo = GUIIdle('sprites/Logo.png')
        self.menu_sound = arcade.load_sound('sound_data/sfx_menu_move4.wav')
        self.start_game = GUIText('sprites/gui/text_window_dark.png', 'Enter: new game', (255, 255, 255),
                                  'fonts/editundo.ttf', 50)
        self.set_gui()

    def set_gui(self):
        self.logo.set_position(8 * 120, 7 * 120)
        self.start_game.set_position(8 * 120, 4.5 * 120)

    def draw_gui(self):
        self.logo.draw()
        self.start_game.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        super(MainMenu, self).on_key_press(symbol, modifiers)
        if symbol == arcade.key.ENTER:
            arcade.play_sound(self.menu_sound)
            self.state = 'new game'

    def on_draw(self):
        arcade.start_render()
        self.draw_gui()


class ChooseNewGame(Scene):
    def __init__(self, width, height):
        super(ChooseNewGame, self).__init__(width, height)
        self.test_regime = GUIText('sprites/gui/text_window_dark.png', '1: test regime', (255, 255, 255),
                                   'fonts/editundo.ttf', 50)
        self.set_gui()
        self.player = content.get_object("ship.pacific")
        self.player.shield_capacitor.charge(25)
        self.player.add_credits(100)

    def set_gui(self):
        self.test_regime.set_position(8 * 120, 4.5 * 120)

    def draw_gui(self):
        self.test_regime.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        super(ChooseNewGame, self).on_key_press(symbol, modifiers)
        if symbol == arcade.key.KEY_1:
            self.state = 'choose ship'

    def on_draw(self):
        self.draw_gui()


class Loss(GameScene):
    def __init__(self, width, health, player):
        super(Loss, self).__init__(width, health, player)
        for facility in self.player.facilities:
            facility.status = 'malfunctioning'
            facility.status_positiveness = -2

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ENTER:
            self.state = 'game ended'

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text('You lost. Tap enter to return to menu', 500, 500, (0, 0, 0), 50)
        self.draw_fps()


class Flight(GameScene):
    def __init__(self, player, width, height, enemy_spawners, left_spawn_zone, right_spawn_zone, base_speed,
                 acceleration, length):
        super().__init__(player, width, height)

        # GUI
        self.health_bar = GUIBar('sprites/gui/health_bar/spritesheet (5).png', 14, 1, 14)
        self.energy_bar = GUIBar("sprites/gui/energy_bar/spritesheet (4).png", 1, 14, 14)
        self.progress_bar = GUIBar('sprites/gui/flight_progress/spritesheet (3).png', 2, 11, 16)
        self.left_gui = GUIIdle("sprites/gui/left_gui.png")
        self.right_gui = GUIIdle("sprites/gui/right_gui.png")
        self.mid_gui = GUIBar('sprites/gui/mid_gui.png', 3, 4, 12)
        self.left_border = GUIMovable("sprites/gui/stab_border_left.png", 50, self.height, self.height)
        self.right_border = GUIMovable("sprites/gui/stab_border_right.png", 50, self.height, self.height)
        self.background = GUIMovable('sprites/background.jpg', 0, 0, self.height, True)
        self.showable_facilities = []
        for facility in self.player.facilities:
            if facility.is_showable():
                self.showable_facilities.append(facility)
        self.facility_info = []
        for facility in self.showable_facilities:
            self.facility_info.append(GUIFacilityInfo("sprites/gui/facility_info.png",
                                                      facility.icon))

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
        self.background.set_position(8 * 120,  9 * 120)
        for i in range(len(self.showable_facilities)):
            self.facility_info[i].set_position(1.5 * 120, 7 * 120 - i * 120)

    def sprite_setup(self):
        self.player_setup()

    def player_setup(self):
        self.player.set_flight(self)
        self.player.spawn(8 * 120, 3.5 * 120)

    """ draw methods """

    def gui_draw_bg(self):
        self.background.draw()

    def gui_draw(self):
        self.left_border.draw()
        self.right_border.draw()
        self.health_bar.draw()
        self.energy_bar.draw()
        self.left_gui.draw()
        self.right_gui.draw()
        self.mid_gui.draw()
        self.progress_bar.draw()
        for gui in self.facility_info:
            # gui.draw()
            pass
        arcade.draw_text('credits: ' + str(self.player.credits), 13.5 * 120, 8.5 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')
        arcade.draw_text('scraps: ' + str(self.player.scraps), 13.5 * 120, 8 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')

    """ overridden methods of Scene class """

    def on_draw(self):
        arcade.start_render()
        self.gui_draw_bg()
        self.objects.draw()
        self.explosions.draw()

        self.player.draw()

        self.gui_draw()
        self.draw_fps()

    def on_update(self, delta_time: float):
        super(Flight, self).on_update(delta_time)
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

        _object.set_flight(self)

    def gui_update(self, delta_time):
        self.health_bar.upd(self.player.hp / self.player.max_hp)
        self.energy_bar.upd(self.player.energy_storage.energy / self.player.energy_storage.max_energy.value())
        self.progress_bar.upd(self.cur_len / self.length)
        self.mid_gui.upd(self.player.shield_capacitor.cur_shield / self.player.shield_capacitor.max_shield.value())
        self.left_border.move(delta_time)
        self.right_border.move(delta_time)
        self.background.speed = -self.speed // 2
        self.background.move(delta_time)
        for i in range(len(self.showable_facilities)):
            self.facility_info[i].set_content(self.showable_facilities[i].info())
            self.facility_info[i].update()

    def update_spawn_timers(self, delta_time):
        for spawner in self.enemy_spawners:
            spawner.update(delta_time)
            spawner.spawn_timer.trigger_time = spawner.frequency / self.speed * self.base_speed

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
                if object_1.is_collidable() and object_2.is_collidable() \
                        and not (object_1.type == 'asteroid' and
                                 object_2.type == 'asteroid'):
                    if arcade.check_for_collision(object_1, object_2):
                        object_1.collide(object_2)
                        object_2.collide(object_1)

    def check_collision_player(self):
        for _object in self.objects:
            if _object.is_collidable():
                if arcade.check_for_collision(_object, self.player.ship_sprite):
                    _object.player_collide()
                    self.player.collide(_object)


class Station(GameScene):
    def __init__(self, player, width, height, facilities):
        super(Station, self).__init__(player, width, height)
        # sound_data
        self.menu_sound = arcade.load_sound('sound_data/sfx_menu_move4.wav')

        # facilities
        self.facilities = facilities

        # gui
        self.gui_left_1 = GUIBar('sprites/gui/station_gui/left_1/st_gui_left_1.png', 6, 3, 18)
        self.gui_left_2 = GUIBar('sprites/gui/station_gui/left_2/st_gui_left_2.png', 6, 3, 18)
        self.gui_left_3 = GUIBar('sprites/gui/station_gui/left_3/st_gui_left_3.png', 6, 3, 18)
        self.gui_left_4 = GUIIdle('sprites/gui/station_gui/st_gui_left_4.png')
        self.gui_welcome = GUIText('sprites/gui/text_window.png', 'Welcome to station!', (0, 0, 0),
                                   'fonts/editundo.ttf', 25)
        self.gui_facility = []
        for i in range(len(self.facilities)):
            self.gui_facility.append(GUIText('sprites/gui/text_window_2.png',
                                             str(i + 1) + ': ' + self.facilities[i].name, (0, 0, 0),
                                             'fonts/editundo.ttf', 20))
        self.set_gui()

        # player
        self.set_up_player()

    def set_gui(self):
        self.gui_left_1.set_position(2 * 120, 7.5 * 120)
        self.gui_left_2.set_position(2 * 120, 6.5 * 120)
        self.gui_left_3.set_position(2 * 120, 5.5 * 120)
        self.gui_left_4.set_position(2 * 120, 3 * 120)
        self.gui_welcome.set_position(7.5 * 120, 7 * 120)
        for i in range(len(self.facilities)):
            self.gui_facility[i].set_position(8 * 120, 6 * 120 - 90 * i)

    def set_up_player(self):
        self.player.spawn(self.width / 2, -50)

    def draw_gui(self):
        self.gui_left_1.draw()
        self.gui_left_2.draw()
        self.gui_left_3.draw()
        self.gui_left_4.draw()
        for gui in self.gui_facility:
            gui.draw()
        self.gui_welcome.draw()

    def update_gui(self):
        self.gui_left_1.upd(self.player.hp / self.player.max_hp)
        self.gui_left_2.upd(self.player.energy() / self.player.max_energy())
        self.gui_left_3.upd(self.player.shield_capacitor.cur_shield / self.player.shield_capacitor.max_shield.value())

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)
        for i in range(len(self.facilities)):
            if symbol == buttons[i]:
                self.state = 'to facility' + str(i)
                arcade.play_sound(self.menu_sound)

        if symbol == arcade.key.ESCAPE:
            arcade.play_sound(self.menu_sound)
            self.state = 'ended'

    def on_update(self, delta_time: float):
        super(Station, self).on_update(delta_time)
        self.delta_time = delta_time
        self.update_gui()

    def on_draw(self):
        arcade.start_render()
        self.player.draw()
        self.draw_gui()
        self.draw_fps()
        arcade.draw_text('credits: ' + str(self.player.credits), 13.5 * 120, 8.5 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')
        arcade.draw_text('scraps: ' + str(self.player.scraps), 13.5 * 120, 8 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')


class StationFacility(GameScene):
    def __init__(self, width, height, player, name, level):
        super(StationFacility, self).__init__(width, height, player)
        self.name = name
        self.level = level
        self.menu_sound = arcade.load_sound('content/sounds/sfx_menu_move4.wav')
        self.buy_sound = arcade.load_sound('content/sounds/sfx_sounds_powerup16.wav')
        self.error_sound = arcade.load_sound('content/sounds/sfx_sounds_error8.wav')
        self.gui_left_1 = GUIBar('sprites/gui/station_gui/left_1/st_gui_left_1.png', 6, 3, 18)
        self.gui_left_2 = GUIBar('sprites/gui/station_gui/left_2/st_gui_left_2.png', 6, 3, 18)
        self.gui_left_3 = GUIBar('sprites/gui/station_gui/left_3/st_gui_left_3.png', 6, 3, 18)
        self.gui_left_4 = GUIIdle('sprites/gui/station_gui/st_gui_left_4.png')

    def set_gui(self):
        self.gui_left_1.set_position(2 * 120, 7.5 * 120)
        self.gui_left_2.set_position(2 * 120, 6.5 * 120)
        self.gui_left_3.set_position(2 * 120, 5.5 * 120)
        self.gui_left_4.set_position(2 * 120, 3 * 120)

    def draw_gui(self):
        self.gui_left_1.draw()
        self.gui_left_2.draw()
        self.gui_left_3.draw()
        self.gui_left_4.draw()

    def update_gui(self):
        self.gui_left_1.upd(self.player.hp / self.player.max_hp)
        self.gui_left_2.upd(self.player.energy() / self.player.max_energy())
        self.gui_left_3.upd(self.player.shield_capacitor.cur_shield / self.player.shield_capacitor.max_shield.value())

    def on_key_press(self, symbol: int, modifiers: int):
        super(StationFacility, self).on_key_press(symbol, modifiers)

        if symbol == arcade.key.ESCAPE:
            self.state = 'back'
            arcade.play_sound(self.menu_sound)

    def on_draw(self):
        self.draw_gui()

    def on_update(self, delta_time: float):
        super(StationFacility, self).on_update(delta_time)
        self.update_gui()


class UpgradeHangar(StationFacility):
    def __init__(self, width, height, player, level):
        super(UpgradeHangar, self).__init__(width, height, player, 'Upgrade hangar', level)
        self.upgradables = []
        self.set_upgradables()
        upgrades_number = clamp(self.level, len(self.upgradables), 0)
        self.upgrades = choose_random_subset(self.upgradables, upgrades_number)
        self.gui_welcome = GUIText('sprites/gui/text_window.png', 'Welcome to \n lvl ' + str(self.level) +
                                   ' Upgrade Hangar!', (36, 59, 97), 'fonts/editundo.ttf', 20)
        self.gui_options = []
        self.gui_options_text = []
        for i in range(len(self.upgrades)):
            self.gui_options.append(
                GUITextUpgrade('sprites/gui/upgrade_text.png', str(i + 1) + ': ' + self.upgrades[i][0].upgrade_info(),
                               (36, 59, 97), 'fonts/editundo.ttf', 20,
                               arcade.load_texture(self.upgrades[i][0].get_facility().icon, scale=0.5),
                               self.upgrades[i][0].get_icon()))
            self.gui_options_text.append(str(i + 1) + ': ' + self.upgrades[i][0].upgrade_info())
        self.text_timers = []
        for i in range(len(self.upgrades)):
            self.text_timers.append(ParamTimer(1, self.text_reset, i, 1))
            self.text_timers[i].stop()
        self.set_gui()

    def set_gui(self):
        super(UpgradeHangar, self).set_gui()
        self.gui_welcome.set_position(7.5 * 120, 7 * 120)
        for i in range(len(self.upgrades)):
            self.gui_options[i].set_position(8 * 120, 6 * 120 - 90 * i)

    def text_reset(self, index):
        self.gui_options[index].text = self.gui_options_text[index]

    def draw_gui(self):
        super(UpgradeHangar, self).draw_gui()
        self.gui_welcome.draw()
        for gui in self.gui_options:
            gui.draw()

    def update_gui(self):
        super(UpgradeHangar, self).update_gui()
        self.gui_welcome.update()

    def set_upgradables(self):
        self.upgradables = []
        for facility in self.player.facilities:
            for upgradable in facility.upgradables:
                if upgradable.is_upgradable():
                    self.upgradables.append([upgradable, True, upgradable.upgrade_cost()])

    def on_key_press(self, symbol: int, modifiers: int):
        super(UpgradeHangar, self).on_key_press(symbol, modifiers)
        self.set_upgradables()
        for i in range(len(self.upgrades)):
            if symbol == buttons[i] and self.upgrades[i][1]:
                if self.player.credits >= self.upgrades[i][2]:
                    self.upgrades[i][0].upgrade()
                    self.upgrades[i][1] = False
                    self.player.add_credits(-self.upgrades[i][2])
                    arcade.play_sound(self.buy_sound)
                    self.gui_options[i].text = str(i + 1) + ': ' + '*bought*'
                else:
                    arcade.play_sound(self.error_sound)
                    self.gui_options[i].text = str(i + 1) + ': ' + '*not enough credits*'
                    self.text_timers[i].start()

    def on_update(self, delta_time: float):
        super(UpgradeHangar, self).on_update(delta_time)
        self.update_gui()
        for timer in self.text_timers:
            timer.update(delta_time)

    def on_draw(self):
        arcade.start_render()
        super(UpgradeHangar, self).on_draw()
        self.draw_fps()
        self.draw_gui()
        arcade.draw_text('credits: ' + str(self.player.credits), 13.5 * 120, 8.5 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')
        arcade.draw_text('scraps: ' + str(self.player.scraps), 13.5 * 120, 8 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')


class MaintenanceHangar(StationFacility):
    def __init__(self, player, width, height, level):
        super(MaintenanceHangar, self).__init__(player, width, height, 'Maintenance Hangar', level)
        self.gui_welcome = GUIText('sprites/gui/text_window.png', 'Welcome to \nlvl ' + str(self.level) +
                                   ' Maintenance Hangar!', (0, 0, 0), 'fonts/editundo.ttf', 20)
        self.gui_hp = GUIText('sprites/gui/text_window_2.png', '1: Repair hull', (36, 59, 97), 'fonts/editundo.ttf', 20)
        self.gui_energy = GUIText('sprites/gui/text_window_2.png', '2: Restore energy', (36, 59, 97),
                                  'fonts/editundo.ttf', 20)
        self.gui_shields = GUIText('sprites/gui/text_window_2.png', '3: Recharge shields', (36, 59, 97),
                                   'fonts/editundo.ttf', 20)
        self.set_gui()

    def draw_gui(self):
        super(MaintenanceHangar, self).draw_gui()
        self.gui_welcome.draw()
        self.gui_hp.draw()
        self.gui_energy.draw()
        self.gui_shields.draw()

    def set_gui(self):
        super(MaintenanceHangar, self).set_gui()
        self.gui_welcome.set_position(7.5 * 120, 7 * 120)
        self.gui_hp.set_position(8 * 120, 6 * 120)
        self.gui_energy.set_position(8 * 120, 5.25 * 120)
        self.gui_shields.set_position(8 * 120, 4.5 * 120)

    def on_key_press(self, symbol: int, modifiers: int):
        super(MaintenanceHangar, self).on_key_press(symbol, modifiers)
        if symbol == arcade.key.KEY_1:
            self.player.repair()
            arcade.play_sound(self.buy_sound)
        if symbol == arcade.key.KEY_2:
            self.player.recharge()
            arcade.play_sound(self.buy_sound)
        if symbol == arcade.key.KEY_3:
            self.player.recharge_shields()
            arcade.play_sound(self.buy_sound)

    def on_draw(self):
        arcade.start_render()
        self.draw_gui()
        arcade.draw_text('credits: ' + str(self.player.credits), 13.5 * 120, 8.5 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')
        arcade.draw_text('scraps: ' + str(self.player.scraps), 13.5 * 120, 8 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')


class Exchanger(StationFacility):
    def __init__(self, width, height, player, level):
        super(Exchanger, self).__init__(width, height, player, 'Exchanger', level)
        self.gui_welcome = GUIText('sprites/gui/text_window.png', 'Welcome to \nlvl ' + str(self.level) +
                                   ' Exchanger!', (0, 0, 0), 'fonts/editundo.ttf', 20)
        self.gui_1 = GUIText('sprites/gui/text_window_2.png', '1: 1 credit for 5 scraps', (36, 59, 97),
                             'fonts/editundo.ttf', 20)
        self.gui_2 = GUIText('sprites/gui/text_window_2.png', '2: 10 credits for 45 scraps', (36, 59, 97),
                             'fonts/editundo.ttf', 20)
        self.gui_3 = GUIText('sprites/gui/text_window_2.png', '3: 100 credits for 400 scraps', (36, 59, 97),
                             'fonts/editundo.ttf', 20)
        self.set_gui()

    def set_gui(self):
        super(Exchanger, self).set_gui()
        self.gui_welcome.set_position(7.5 * 120, 7 * 120)
        self.gui_1.set_position(8 * 120, 6 * 120)
        self.gui_2.set_position(8 * 120, 5.25 * 120)
        self.gui_3.set_position(8 * 120, 4.5 * 120)

    def draw_gui(self):
        super(Exchanger, self).draw_gui()
        self.gui_welcome.draw()
        self.gui_1.draw()
        self.gui_2.draw()
        self.gui_3.draw()

    def on_draw(self):
        arcade.start_render()
        self.draw_gui()
        arcade.draw_text('credits: ' + str(self.player.credits), 13.5 * 120, 8.5 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')
        arcade.draw_text('scraps: ' + str(self.player.scraps), 13.5 * 120, 8 * 120, (0, 0, 0), font_size=20,
                         font_name='fonts/editundo.ttf')

    def on_key_press(self, symbol: int, modifiers: int):
        super(Exchanger, self).on_key_press(symbol, modifiers)
        if symbol == arcade.key.KEY_1:
            if self.player.scraps >= 5:
                self.player.add_scraps(-5)
                self.player.add_credits(1)
                arcade.play_sound(self.buy_sound)
            else:
                arcade.play_sound(self.error_sound)

        if symbol == arcade.key.KEY_2:
            if self.player.scraps >= 45:
                self.player.add_scraps(-45)
                self.player.add_credits(10)
                arcade.play_sound(self.buy_sound)
            else:
                arcade.play_sound(self.error_sound)

        if symbol == arcade.key.KEY_3:
            if self.player.scraps >= 400:
                self.player.add_scraps(-400)
                self.player.add_credits(100)
                arcade.play_sound(self.buy_sound)
            else:
                arcade.play_sound(self.error_sound)


def create_station(player, width, height):
    upg_hangar = UpgradeHangar(player, width, height, 3)
    main_hangar = MaintenanceHangar(player, width, height, 1)
    exc = Exchanger(player, width, height, 1)
    station = Station(player, width, height, [upg_hangar, main_hangar, exc])
    return station
