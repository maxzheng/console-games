from games.screen import Scene
from games.objects import Monologue
from games.number_crush.objects import Numbers


class Crush(Scene):
    def init(self):
        self.numbers = Numbers(x=self.screen.width / 2, y=0, player=self.player)
        self.player.reset()
        self.player.is_playing = True

    def start(self):
        self.screen.add(self.player, self.numbers)

    def escape_pressed(self):
        self.controller.done = True


class Intro(Scene):
    def init(self):
        self.intro = Monologue(self.controller.player.x, self.controller.player.y - 3,
                               on_finish=self.next,
                               texts=["Hi, I am {}!".format(self.controller.player.name),
                                      "Most people don't like math, but not me.",
                                      "I LOVE to crush them!! :D",
                                      "Type the answer using number keys.",
                                      "Ready? Let's CRUSH!!"])

    def start(self):
        self.screen.add(self.intro, self.controller.player)

    def key_pressed(self, key):
        self.next()
