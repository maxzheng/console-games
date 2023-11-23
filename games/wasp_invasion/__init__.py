from games.controller import Controller
from games.wasp_invasion.scenes import Intro, Survive
from games.wasp_invasion.objects import Player
from games.objects import WaspKaiju, Stickman


class WaspInvasion(Controller):
    name = "Wasp Invasion"

    def init(self):
        self.scenes = [Intro, Survive]
        self.logo = WaspKaiju(0, 0, color=self.screen.COLOR_YELLOW)
        self.player = Player('Jon', Stickman(self.screen.width / 2, self.screen.height - 3), self)
        self.player.controller = self
