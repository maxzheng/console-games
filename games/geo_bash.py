from random import randint, random

from games.controller import Controller
from games.scenes import ChoosePlayer, Intro, Bash
from games.objects import (Square, Circle, Projectile, Explosion, Text, Monologue, Triangle,
                           Diamond, Bar, Boss)


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        #: Player object that will be set by ChoosePlayer scene and then used by other scenes.
        self.player = None

        self.scenes = [ChoosePlayer, Intro, Bash]
