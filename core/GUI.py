import arcade

from core.Utilities import cut


class GUIBar(arcade.Sprite):
    def __init__(self, filename: str, rows, columns, amount):
        super(GUIBar, self).__init__()
        self.amount = amount
        self.textures = cut(filename, rows, columns, amount)
        self.set_texture(0)

    def upd(self, rel_value):
        index = round(rel_value * (self.amount - 1))
        self.set_texture(index)


class GUIIdle(arcade.Sprite):
    def __init__(self, filename):
        super().__init__(filename)


class GUIMovable(arcade.Sprite):
    def __init__(self, filename, speed, __height):
        super().__init__(filename)
        self.speed = speed
        self.__height = __height

    def move(self, delta_time):
        self.center_y += self.speed * delta_time
        if self.center_y >= self.__height:
            self.center_y -= self.__height


class GUIText(arcade.Sprite):
    def __init__(self, filename, text, text_color, font, font_size):
        super(GUIText, self).__init__(filename)
        self.text = text
        self.text_color = text_color
        self.font = font
        self.font_size = font_size
        self.text_center_x = 0
        self.text_center_y = 0

    def draw_text(self):
        arcade.draw_text(self.text, self.text_center_x, self.text_center_y, self.text_color,
                         font_name=self.font, font_size=self.font_size, anchor_x='center', anchor_y='center')

    def set_position(self, center_x: float, center_y: float):
        super(GUIText, self).set_position(center_x, center_y)
        self.text_center_x = center_x
        self.text_center_y = center_y

    def draw(self):
        super(GUIText, self).draw()
        self.draw_text()


class GUITextUpgrade(GUIText):
    def __init__(self, filename, text, text_color, font, font_size, icon_1, icon_2):
        super(GUITextUpgrade, self).__init__(filename, text, text_color, font, font_size)
        self.icon_1 = arcade.Sprite()
        self.icon_1.append_texture(icon_1)
        self.icon_1.set_texture(0)
        self.icon_2 = arcade.Sprite()
        self.icon_2.append_texture(icon_2)
        self.icon_2.set_texture(0)

    def set_position(self, center_x: float, center_y: float):
        super(GUITextUpgrade, self).set_position(center_x, center_y)
        self.icon_1.set_position(center_x - self.width / 2 + 36, center_y)
        self.icon_2.set_position(center_x - self.width / 2 + 100, center_y)
        self.text_center_x += 56

    def draw_icons(self):
        self.icon_1.draw()
        self.icon_2.draw()

    def draw(self):
        super(GUITextUpgrade, self).draw()
        self.draw_icons()


class GUIFacilityInfo(arcade.Sprite):
    def __init__(self, filename, icon):
        super(GUIFacilityInfo, self).__init__(filename)
        self.icon_sprite = arcade.Sprite(icon, scale=0.5)
        self.bar_1 = GUIBar('sprites/gui/facility_info/facility_info_bar_blue.png', 23, 1, 23)
        self.bar_2 = GUIBar('sprites/gui/facility_info/facility_info_bar_blue.png', 23, 1, 23)
        self.bar_3 = GUIBar('sprites/gui/facility_info/facility_info_bar_blue.png', 23, 1, 23)
        self.top_text_content = 'a'
        self.bottom_text_content = 'a'
        self.bottom_color = (0, 0, 0)
        self.rel_value_1 = 0
        self.rel_value_2 = 0
        self.rel_value_3 = 0

    def set_content(self, info):
        self.rel_value_1 = info[0]
        self.rel_value_2 = info[1]
        self.rel_value_3 = info[2]
        self.top_text_content = info[3]
        self.bottom_text_content = info[4]
        self.bottom_color = info[5]

    def set_position(self, x, y):
        super(GUIFacilityInfo, self).set_position(x, y)
        self.icon_sprite.set_position(x - 112, y)
        self.bar_1.set_position(self.center_x + 28, self.center_y + 8)
        self.bar_2.set_position(self.center_x + 28, self.center_y)
        self.bar_3.set_position(self.center_x + 28, self.center_y - 8)

    def update(self):
        self.bar_1.upd(self.rel_value_1)
        self.bar_2.upd(self.rel_value_2)
        self.bar_3.upd(self.rel_value_3)

    def draw(self):
        super(GUIFacilityInfo, self).draw()
        self.icon_sprite.draw()
        self.bar_1.draw()
        self.bar_2.draw()
        self.bar_3.draw()
        arcade.draw_text(self.top_text_content, self.center_x - 60, self.center_y + 28, (255, 255, 255),
                         font_name='fonts/editundo.ttf', anchor_y='center')
        arcade.draw_text(self.bottom_text_content, self.center_x - 60, self.center_y - 28, self.bottom_color,
                         font_name='fonts/editundo.ttf', anchor_y='center')