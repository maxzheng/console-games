from games.screen import Scene
from games.objects import Monologue
from games.wasp_invasion.objects import Enemies, Landscape0, Landscape1, Landscape2


class Intro(Scene):
    def init(self):
        self.intro = Monologue(self.controller.player.x, self.controller.player.y - 3,
                               on_finish=self.next,
                               texts=["Hi, I am {}.".format(self.controller.player.name),
                                      "Wasp kaijus have invaded Earth!!",
                                      "We don't know why they are here,",
                                      "but they have taken control of all wasps",
                                      "and started killing everyone.",
                                      "Luckily, I got my trusty flamethrower with me.",
                                      "Oh no! Here they come. GET READY!!",
                                      "Move around using left/right keys",
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
        self.landscapes = (Landscape0(0, 0), Landscape1(0, 0), Landscape2(0, 0))
        self.player.reset()

    def start(self):
        self.screen.add(*self.landscapes, self.player, self.enemies)

    def escape_pressed(self):
        self.controller.done = True