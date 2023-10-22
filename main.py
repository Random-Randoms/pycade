import arcade
from content.content import content
from core.Control import MenuController, NodeTimeLine


class App(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.WHITE)
        self.controller = content.get_object('controller.menu')
        self.controller.set_root(self)
        self.player = content.get_object('ship.pacific')
        self.set_update_rate(1 / 100)
        self.set_vsync(False)
        self.scene = None
        self.set_fullscreen(True)
        self.controller.start()

    def on_key_press(self, symbol: int, modifiers: int):
        self.scene.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        self.scene.on_key_release(symbol, modifiers)

    def on_draw(self):
        self.scene.on_draw()

    def set_scene(self, scene):
        self.scene = scene

    def set_player(self, player):
        self.player = player

    def on_update(self, delta_time: float):
        self.scene.on_update(delta_time)
        self.controller.update()



"""global variables"""
default_timeline = NodeTimeLine('test regime')
menu_controller = MenuController('menu')
content.add_object('timeline', default_timeline)
content.add_object('controller', menu_controller)
app = App(1920, 1080, 'Arcade')
arcade.run()
