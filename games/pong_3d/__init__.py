from games.controller import Controller
from games.pong_3d.scenes import Intro
from games.pong_3d.objects import Player
from games.objects import Circle, Stickman


class Pong3D(Controller):
    name = "Pong 3D"

    def init(self):
        self.scenes = [Intro]
        self.logo = Circle(0, 0, color=self.screen.COLOR_BLUE)
        self.player = Player('Jon', Stickman(self.screen.width / 2, self.screen.height - 2), self)
        self.player.controller = self
