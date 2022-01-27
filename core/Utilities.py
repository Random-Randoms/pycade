import copy
import random
import builtins
import PIL.Image
import arcade


class Timer:
    def __init__(self, time, func, iterations=-1):
        self.trigger_time = time
        self.current_time = 0
        self.func = func
        self.is_running = True
        self.max_iterations = iterations
        self.iterations = 0

    def trigger_func(self):
        self.func()
        self.iterations += 1
        if self.iterations == self.max_iterations:
            self.stop()
            self.iterations = 0

    def update(self, delta_time):
        if self.is_running:
            self.current_time += delta_time
        if self.current_time >= self.trigger_time:
            self.current_time = 0
            self.trigger_func()

    def stop(self):
        self.is_running = False
        self.current_time = 0

    def start(self):
        self.is_running = True

    def refresh(self):
        self.current_time = 0


class ParamTimer(Timer):
    def __init__(self, time, func, param, iterations=-1):
        super(ParamTimer, self).__init__(time, func, iterations)
        self.param = param

    def trigger_func(self):
        self.func(self.param)


class Controls:
    def __init__(self, right, left, shoot):
        self.right = right
        self.left = left
        self.shoot = shoot


def cut(filename='', rows=1, columns=1, amount=1, scale=1.0):
    num = 0
    source_image = PIL.Image.open(filename)
    width = source_image.width
    height = source_image.height
    textures = []
    width_0 = width / columns
    height_0 = height / rows
    for j in range(rows):
        if num >= amount:
            break
        for i in range(columns):
            num += 1
            x = width * i / columns
            y = height * j / rows
            image = source_image.crop((x, y, x + width_0, y + height_0))
            image = image.resize((round(width_0 * scale), round(height_0 * scale)))
            textures.append(arcade.Texture(str(i * columns + j), image))
            if num >= amount:
                break
    return textures


def choose_random_subset(_set: builtins.list, size):
    result = []
    _set_copy = copy.copy(_set)
    for i in range(size):
        index = random.choice(range(len(_set_copy)))
        result.append(_set_copy[index])
        _set_copy.pop(index)
    return result


def clamp(value, _max, _min):
    if value > _max:
        return _max
    elif value < _min:
        return _min
    else:
        return value


def status_color(positiveness):
    if positiveness == 2:
        return 0, 255, 0
    elif positiveness == 1:
        return 63, 255, 63
    elif positiveness == 0:
        return 255, 255, 0
    elif positiveness == -1:
        return 255, 63, 63
    elif positiveness == -2:
        return 255, 0, 0
    else:
        return 255, 255, 255