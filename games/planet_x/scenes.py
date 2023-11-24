from games.screen import Scene
from games.objects import Monologue, Sun
from games.planet_x.objects import Enemies, Landscape1, Landscape2, Obstacles, Wormhole


class Intro(Scene):
    def init(self):
        self.controller.player.reset()
        self.controller.player.active = False
        self.intro = Monologue(self.controller.player.x, self.controller.player.y + 4,
                               on_finish=self.next,
                               texts=["This is your daily news",
                                      "from the sky.",
                                      "It's a beautiful sunny day!"])
        self.landscapes = (Sun(self.screen.width / 2, 2),
                           Landscape1(0, self.screen.height / 2 - 5, player=self.player),
                           Landscape2(0, self.screen.height / 2, player=self.player))
        self.obstacles = Obstacles(-self.screen.width, self.screen.height - 5, player=self.player)

    def start(self):
        self.screen.add(*self.landscapes, self.obstacles, self.intro, self.controller.player)

    def key_pressed(self, key):
        self.next()


class WormholeAppeared(Intro):
    def init(self):
        super().init()
        self.intro = Monologue(self.controller.player.x, self.controller.player.y + 4,
                               on_finish=self.next,
                               texts=["Wait...",
                                      "What is that??!!",
                                      "Some kind of wormhole",
                                      "just appeared out of no where!"])
        self.wormhole = Wormhole(self.controller.player.x - 30, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        super().start()
        self.screen.add(self.wormhole)


class WormholeSucks(WormholeAppeared):
    def init(self):
        super().init()
        self.intro = Monologue(self.controller.player.x, self.controller.player.y + 4,
                               texts=["Oh no!!",
                                      "We are being sucked in!!",
                                      "Hold on ti..."])
        self.controller.player.x_delta = -0.2


class Level1(Scene):
    def init(self):
        self.player.reset()
        self.player.score = 1
        self.enemies = Enemies(self.controller.player)
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        self.screen.add(self.enemies, self.player, self.wormhole)

    def escape_pressed(self):
        self.controller.done = True


class Level2(Scene):
    def init(self):
        hp = self.player.hp
        gas = self.player.gas
        self.player.reset()
        self.player.score = 2
        self.player.hp = hp
        self.player.gas = gas

        self.enemies = Enemies(self.controller.player)
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        self.screen.add(self.enemies, self.player, self.wormhole)

    def escape_pressed(self):
        self.controller.done = True
