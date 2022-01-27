import core.Scenes
from content.content import default_enemy, default_enemy_2
from core.Enemies import TimeSpawner
from core.Scenes import MainMenu, Flight, create_station, Loss


class MenuController:
    def __init__(self, timeline):
        self.root = None
        self.base_scene = None
        self.timeline = timeline
        self.in_game = False

    def set_root(self, root):
        self.root = root
        self.set_base_scene()
        self.timeline.set_root(root)

    def set_base_scene(self):
        self.base_scene = MainMenu(self.root.width, self.root.height)

    def start(self):
        self.set_base_scene()
        self.root.set_scene(self.base_scene)

    def update(self):
        width = self.root.width
        height = self.root.height
        if self.in_game:
            self.timeline.update()
            if self.timeline.game_ended:
                self.in_game = False
                self.timeline.game_ended = False
                self.start()
        else:
            state = self.root.scene.state
            if state == 'new game':
                self.root.set_scene(core.Scenes.ChooseNewGame(width, height))

            elif state == 'choose ship':
                self.in_game = True
                self.root.set_player(self.root.scene.player)
                self.root.scene.clear_state()
                self.timeline.start()

            elif state == 'close':
                self.root.close()


class TimeLine:
    def __init__(self):
        self.root = None
        self.game_ended = False

    def set_root(self, root):
        self.root = root

    def start(self):
        self.game_ended = False

    def update(self):
        pass


class NodeTimeLine(TimeLine):
    def __init__(self):
        super(NodeTimeLine, self).__init__()
        self.cur_station = None

    def start(self):
        super(NodeTimeLine, self).start()
        self.root.set_scene(Flight(self.root.player, self.root.width, self.root.height,
                                   [TimeSpawner(default_enemy, 0.15),
                                    TimeSpawner(default_enemy_2, 3.0)], 360, 1920 - 360, 200, 2, 200))

    def update(self):
        player = self.root.player
        width = self.root.width
        height = self.root.height
        state = self.root.scene.state
        self.root.scene.clear_state()
        if state == 'flight_ended_victory':
            self.cur_station = create_station(player, width, height)
            self.root.set_scene(self.cur_station)

        elif state == 'flight_ended_loss':
            self.root.set_scene(Loss(player, width, height))

        elif state == 'ended':
            self.root.set_scene(Flight(self.root.player, self.root.width, self.root.height,
                                       [TimeSpawner(default_enemy, 0.15),
                                        TimeSpawner(default_enemy_2, 2.0)], 360, 1920 - 360, 200, 1, 200))

        elif state == 'back':
            self.root.set_scene(self.cur_station)

        elif state == 'game ended':
            self.game_ended = True

        elif 'to facility' in state:
            self.root.set_scene(self.cur_station.facilities[int(state[11])])

        elif state == 'close':
            self.root.close()
