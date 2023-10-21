from random import randint, random

from games.controller import Controller
from games.scenes import ChoosePlayer, Intro, Bash
from games.objects import (Square, Circle, Projectile, Explosion, Text, Monologue, Triangle,
                           Diamond, Bar, Boss)


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        #: Player object that will be set by ChoosePlayer scene
        self.player = None

        self.choose_player = ChoosePlayer()
        self.intro = Intro()
        self.bash = Bash()

        self.set_scene(self.choose_player)

