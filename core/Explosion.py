import arcade

from core.GameObjects import GameObject
from core.Utilities import Timer


class Explosion(GameObject):
    def __init__(self, name, filename, scale, explosion_sound, explosion_textures):
        super(Explosion, self).__init__(name, filename, scale, 1 / 12)
        self.add_state_textures('explosion', explosion_textures)
        self.explosion_textures = explosion_textures
        self.set_state('explosion')
        self.type = 'explosion'
        self.move_by_flight = True
        self.explosion_sound = explosion_sound
        self.destruction_timer = Timer(self.frequency * len(explosion_textures), self.complete_destroy)
        self.first_upd = True

    def upd(self, delta_time):
        if self.first_upd:
            self.first_upd = False
            arcade.play_sound(arcade.load_sound(self.explosion_sound))
        super(Explosion, self).upd(delta_time)
        self.destruction_timer.update(delta_time)
