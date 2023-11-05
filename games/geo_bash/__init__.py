from games.controller import Controller
from games.geo_bash.scenes import ChoosePlayer, Intro, Bash
from games.objects import Triangle, Circle, Diamond, ScreenObjectGroup


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        self.scenes = [ChoosePlayer, Intro, Bash]
        self.logo = ScreenObjectGroup(0, 0, objects=[
            Triangle(0, 0, color=self.screen.COLOR_BLUE),
            Circle(0, 0, color=self.screen.COLOR_RED),
            Diamond(0, 0, color=self.screen.COLOR_YELLOW)
        ])
        #: Player object that will be set by ChoosePlayer scene and then used by other scenes.
        self.player = None
