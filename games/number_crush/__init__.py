from games.controller import Controller
from games.objects import One, Two, Plus, Stickman, ScreenObjectGroup, Player
from games.number_crush.scenes import Crush, Intro


class NumberCrush(Controller):
    name = "Number Crush"

    def init(self):
        self.scenes = [Intro, Crush]
        self.logo = ScreenObjectGroup(0, 0, objects=[
            One(0, 0),
            Plus(0, 0),
            Two(0, 0)
        ])
        self.player = Player('Jon',
                             Stickman(int(self.screen.width / 2) + 1, self.screen.height - 2),
                             controller=self,
                             score_title='Crushed',
                             show_total=True)
