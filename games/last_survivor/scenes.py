from games.screen import Scene
from games.objects import Monologue
from games.last_survivor.objects import Enemies


class Intro(Scene):
    def init(self):
        self.intro = Monologue(self.controller.player.x, self.controller.player.y - 2,
                               on_finish=self.next,
                               texts=["Hi, I am {}, THE LAST SURVIVOR".format(self.controller.player.name),
                                      "of the zombie apocalypse.",
                                      "It all started by a crazy scientist",
                                      "experimenting with a rat",
                                      "and injected it with the wrong formula.",
                                      "It turned into a zombie ...",
                                      "and spreaded to everyone.",
                                      "Oh no! Here they come. GET READY!!",
                                      "Move your weapon using left/right keys."])
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
