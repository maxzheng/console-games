from games.screen import Scene
from games.number_crush.objects import Numbers


class Crush(Scene):
    def init(self):
        self.numbers = Numbers(x=self.screen.width / 2, y=0, player=self.player)
        self.player.reset()
        self.player.is_playing = True

    def start(self):
        self.screen.add(self.player, self.numbers)

    def escape_pressed(self):
        self.controller.done = True
