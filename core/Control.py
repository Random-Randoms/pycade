import core.Scenes
from content.content import asteroid, missile
from core.Enemies import TimeSpawner
from core.Scenes import MainMenu, Flight, create_station, Loss


class MenuController:
    def __init__(self, name):
        self.name = name
        self.root = None
        self.base_scene = None
        self.content = None
        self.timelines = None
        self.timeline = None
        self.in_game = False

    def set_content(self, content):
        self.content = content
        self.timelines = content.get_timelines()
        for timeline in self.timelines:
            timeline.set_content(self.content)
        self.timeline = self.timelines[0]

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
    def __init__(self, name):
        self.content = None
        self.name = name
        self.root = None
        self.game_ended = False

    def set_content(self, content):
        self.content = content

    def set_root(self, root):
        self.root = root

    def start(self):
        self.game_ended = False

    def update(self):
        pass


class NodeTimeLine(TimeLine):
    def __init__(self, name):
        super(NodeTimeLine, self).__init__(name)
        self.cur_station = None

    def start(self):
        super(NodeTimeLine, self).start()
        self.root.set_scene(Flight(self.root.player, self.root.width, self.root.height,
                                   [TimeSpawner(self.content.get_object('enemy.asteroid'), 0.15),
                                    TimeSpawner(self.content.get_object('enemy.missile'), 3.0)], 360, 1920 - 360, 200, 1, 250))

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
                                       [TimeSpawner(asteroid, 0.15),
                                        TimeSpawner(missile, 2.0)],
                                       360, 1920 - 360, 200, 1, 250))

        elif state == 'back':
            self.root.set_scene(self.cur_station)

        elif state == 'game ended':
            self.game_ended = True

        elif 'to facility' in state:
            self.root.set_scene(self.cur_station.facilities[int(state[11])])

        elif state == 'close':
            self.root.close()
