from games.controller import Controller
from games.last_survivor.scenes import Intro, Survive
from games.last_survivor.objects import Player
from games.objects import Zombie, ScreenObject, Text, Char
from games.screen import Screen


class LastSurvivor(Controller):
    name = "THE LAST SURVIVOR!!"

    def init(self):
        self.player = Player('Jon', Char(self.screen.width / 2, self.screen.height / 2, char='O'))
        self.player.controller = self
        self.scenes = [Intro, Survive]

    class Logo(ScreenObject):
        def __init__(self, x, y, name, color=None):
            super().__init__(x, y, size=7, color=color)
            self.name = name
            self.text = self.zombie = None

        def render(self, screen: Screen):
            super().render(screen)

            if not self.text:
                self.text = Text(self.x, self.y + 3, self.name, is_centered=True, color=self.color)
            if not self.zombie:
                self.zombie = Zombie(self.x, self.y, color=screen.COLOR_GREEN)

            self.zombie.render(screen)
            self.text.render(screen)
