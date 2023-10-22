from games.controller import Controller
from games.geo_bash.scenes import ChoosePlayer, Intro, Bash


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        #: Player object that will be set by ChoosePlayer scene and then used by other scenes.
        self.player = None

        self.scenes = [ChoosePlayer, Intro, Bash]
