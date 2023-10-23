from games.controller import Controller
from games.geo_bash.scenes import ChoosePlayer, Intro, Bash
from games.objects import Triangle, Circle, Diamond, ScreenObject, Text
from games.screen import Screen


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        #: Player object that will be set by ChoosePlayer scene and then used by other scenes.
        self.player = None

        self.scenes = [ChoosePlayer, Intro, Bash]


class Logo(ScreenObject):
    def __init__(self, x, y, name, color=None):
        super().__init__(x, y, size=len(name), color=color)
        self.text = Text(x, y, name, is_centered=True, color=color)
        self.triangle = Triangle(x - 10, y, size=3, color=self.screen.COLOR_BLUE)
        self.circle = Circle(x, y, size=3, color=self.screen.COLOR_RED)
        self.diamond = Diamond(x + 10, y, size=3, color=self.screen.COLOR_YELLOW)

    def render(self, screen: Screen):
        super().render(screen)

        self.text.render(screen)
        self.triangle.render(screen)
        self.circle.render(screen)
        self.diamond.render(screen)
