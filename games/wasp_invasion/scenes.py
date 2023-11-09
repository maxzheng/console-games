from games.screen import Scene
from games.objects import Monologue
from games.wasp_invasion.objects import Enemies


class Intro(Scene):
    def init(self):
        self.intro = Monologue(self.controller.player.x, self.controller.player.y - 3,
                               on_finish=self.next,
                               texts=["Hi, I am {}.".format(self.controller.player.name),
                                      "A WASP KAIJU has invaded Earth!!",
                                      "We don't know why it is here,",
                                      "but it has taken control of all wasps",
                                      "and killing everyone.",
                                      "Luckily, I got my trusty flamethrower with me.",
                                      "Uh oh! Here they come. GET READY!!",
                                      "Move around using arrow keys",
                                      "and jump using Space bar."])
        self.controller.player.reset()
        self.controller.player.active = False

    def start(self):
        self.screen.add(self.intro, self.controller.player)

    def key_pressed(self, key):
        self.next()


class Survive(Scene):
    def init(self):
        self.enemies = Enemies(self.controller.player)
        self.player.reset()

    def start(self):
        self.screen.add(self.player, self.enemies)

    def escape_pressed(self):
        self.controller.done = True
