from games.controller import Controller
from games.planet_x.scenes import (Intro, WormholeAppeared, WormholeSucks, Home, Level1, Level2, Level3,
                                   Level4)
from games.planet_x.objects import Player
from games.objects import Helicopter, Wormhole


class PlanetX(Controller):
    name = "Planet X"

    def init(self):
        self.scenes = [Intro, WormholeAppeared, WormholeSucks, Level1, Level2, Level3, Level4, Home]
        self.logo = Wormhole(0, 0)
        self.player = Player('Max', Helicopter(self.screen.width - 15, self.screen.height / 2), self)
        self.player.controller = self
