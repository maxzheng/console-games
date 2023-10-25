from games.controller import Controller
from games.objects import Diamond
from games.number_crush.scenes import Crush, Intro
from games.number_crush.objects import Player


class NumberCrush(Controller):
    name = "Number Crush"

    def init(self):
        self.player = Player('Jon', Diamond(self.screen.width / 2, self.screen.height - 3, size=3,
                             color=self.screen.COLOR_YELLOW), controller=self)

        self.scenes = [Intro, Crush]
