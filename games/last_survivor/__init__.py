from games.controller import Controller
from games.last_survivor.scenes import Intro, Survive
from games.last_survivor.objects import Player
from games.objects import Zombie, Char


class LastSurvivor(Controller):
    name = "THE LAST SURVIVOR!!"

    def init(self):
        self.scenes = [Intro, Survive]
        self.logo = Zombie(0, 0, color=self.screen.COLOR_GREEN)
        self.player = Player('Jon', Char(self.screen.width / 2, self.screen.height / 2, char='☻'), self)
        self.player.controller = self
