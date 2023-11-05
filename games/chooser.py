from games.controller import Controller
from games.objects import Choice, Logo
from games.screen import Scene
from games.geo_bash import GeoBash
from games.number_crush import NumberCrush
from games.last_survivor import LastSurvivor


class Chooser(Controller):
    name = "Choose a Game"

    def init(self):
        self.scenes = [Choose]


class Choose(Scene):
    def init(self):
        self.games = [GeoBash(self.screen), NumberCrush(self.screen), LastSurvivor(self.screen)]
        self.game_logos = [Logo(0, 0, g.name, g.logo) for g in self.games]
        self.game_choice = Choice(x=self.screen.width / 2, y=int(self.screen.height / 2),
                                  choices=self.game_logos, on_select=self.play,
                                  current=getattr(self.controller, '_last_game_index', None))

    def start(self):
        self.screen.reset(border=True)
        self.screen.add(self.game_choice)

    def escape_pressed(self):
        self.controller.done = True

    def play(self, game_logo):
        game = self.games[self.game_logos.index(game_logo)]
        game.reset()

        self.screen.controller = game
        self.screen.reset()

        while not game.done:
            self.screen.render()
            game.play()

        self.screen.controller = self.controller
        self.controller._last_game_index = self.game_logos.index(game_logo)
        self.controller.reset_scene()
