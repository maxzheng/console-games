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
            super().__init__(x, y, size=7, color=color)
            self.name = name
            self.text = self.triangle = self.circle = self.diamond = None

        def render(self, screen: Screen):
            super().render(screen)

            if not self.text:
                self.text = Text(self.x, self.y + 3, self.name, is_centered=True, color=self.color)
            if not self.triangle:
                self.triangle = Triangle(self.x - 6, self.y, size=3, color=screen.COLOR_BLUE)
            if not self.circle:
                self.circle = Circle(self.x, self.y, size=3, color=screen.COLOR_RED)
            if not self.diamond:
                self.diamond = Diamond(self.x + 5, self.y, size=3, color=screen.COLOR_YELLOW)

            self.triangle.render(screen)
            self.circle.render(screen)
            self.diamond.render(screen)
            self.text.render(screen)
