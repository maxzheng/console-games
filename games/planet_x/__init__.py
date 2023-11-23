from games.controller import Controller
from games.planet_x.scenes import Intro, Survive
from games.planet_x.objects import Player, X3D
from games.objects import Helicopter


class PlanetX(Controller):
    name = "Planet X"

    def init(self):
        self.scenes = [Intro, Survive]
        self.logo = X3D(0, 0, color='cyan', rotate_axes=(0, 0, 1))
        self.player = Player('Jon', Helicopter(5, self.screen.height / 2, flip=True), self)
        self.player.controller = self
