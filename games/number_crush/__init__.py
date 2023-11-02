from games.controller import Controller
from games.screen import Screen
from games.objects import ScreenObject, Text, One, Two, Plus, Stickman
from games.number_crush.scenes import Crush, Intro
from games.number_crush.objects import Player


class NumberCrush(Controller):
    name = "Number Crush"

    def init(self):
        self.player = Player('Jon', Stickman(int(self.screen.width / 2) + 1, self.screen.height - 2, size=3),
                             controller=self)

        self.scenes = [Intro, Crush]

    class Logo(ScreenObject):
        def __init__(self, x, y, name, color=None):
            super().__init__(x, y, size=7, color=color)
            self.name = name
            self.text = self.one = self.two = self.three = None

        def render(self, screen: Screen):
            super().render(screen)

            if not self.text:
                self.text = Text(self.x, self.y + 3, self.name, is_centered=True, color=self.color)
                screen.add(self.text)

            if not self.one:
                self.one = One(self.x - 5, self.y)
                screen.add(self.one)

            if not self.two:
                self.two = Plus(self.x, self.y)
                screen.add(self.two)

            if not self.three:
                self.three = Two(self.x + 6, self.y)
                screen.add(self.three)
