import arcade

from GameObjects import GameObject


class MagneticDisc(GameObject):
    def __init__(self, force, filename):
        super(MagneticDisc, self).__init__(filename, force / 100)
        self.force = force
        self.owner = None

    def set_owner(self, owner):
        self.owner = owner

    def set_force(self, force):
        self.force = force
        self.scale = self.force / 100

    def upd(self, delta_time):
        super().upd(delta_time)
        self.center_x = self.owner.center_x
        self.center_y = self.owner.center_y

