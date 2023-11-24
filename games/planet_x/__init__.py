from games.controller import Controller
from games.planet_x.scenes import Intro, WormholeAppeared, WormholeSucks, Level1, Level2
from games.planet_x.objects import Player, Wormhole
from games.objects import Helicopter


class PlanetX(Controller):
    name = "Planet X"

    def init(self):
        self.scenes = [Intro, WormholeAppeared, WormholeSucks, Level1, Level2]
        self.logo = Wormhole(0, 0)
        self.player = Player('Max', Helicopter(self.screen.width - 15, self.screen.height / 2), self)
        self.player.controller = self
