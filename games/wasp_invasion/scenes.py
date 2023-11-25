from games.screen import Scene
from games.objects import Monologue, Sun
from games.wasp_invasion.objects import Enemies, Landscape1, Landscape2, Obstacles


class Intro(Scene):
    def init(self):
        self.intro = Monologue(self.controller.player.x, self.controller.player.y - 3,
                               on_finish=self.next,
                               texts=["Hi, I am {}.".format(self.controller.player.name),
                                      "10 WASP KAIJUS have INVADED Earth!!",
                                      "We don't know why they are here,",
                                      "but they have taken control of all wasps",
                                      "and started killing everyone.",
                                      "Luckily, I got my trusty flamethrower with me.",
                                      "Oh no! Here they come. GET READY!!",
                                      "Move me around using arrow/space keys",
                                      "and control the flame using up/down keys."])
        self.controller.player.reset()
        self.controller.player.active = False

    def start(self):
        self.screen.add(self.intro, self.controller.player)

    def key_pressed(self, key):
        self.next()


class Survive(Scene):
    def init(self):
        self.enemies = Enemies(self.controller.player, max_enemies=int(self.screen.width / 10))
        self.landscapes = (Sun(self.screen.width / 2, 2),
                           Landscape1(0, self.screen.height / 2 - 5, player=self.player),
                           Landscape2(0, self.screen.height / 2, player=self.player))
        self.obstacles = Obstacles(self.screen.width / 2, self.screen.height - 6, player=self.player)
        self.player.reset()
        self.player.obstacles = self.obstacles

    def start(self):
        self.screen.add(*self.landscapes, self.obstacles, self.enemies, self.player)

    def escape_pressed(self):
        self.controller.done = True
