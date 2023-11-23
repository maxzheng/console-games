from games.controller import Controller
from games.objects import Choice, Logo
from games.screen import Scene
from games.geo_bash import GeoBash
from games.number_crush import NumberCrush
from games.last_survivor import LastSurvivor
from games.wasp_invasion import WaspInvasion
from games.planet_x import PlanetX


class Chooser(Controller):
    name = "Choose a Game"

    def __init__(self, *args, game_filter=None, **kwargs):
        super().__init__(*args, **kwargs)

        #: Filter games that matches the name
        self.game_filter = game_filter

    def init(self):
        self.scenes = [Choose]


class Choose(Scene):
    def init(self):
        self.games = [GeoBash(self.screen), PlanetX(self.screen), NumberCrush(self.screen),
                      WaspInvasion(self.screen), LastSurvivor(self.screen)]
        if self.controller.game_filter:
            self.games = list(filter(lambda g: self.controller.game_filter.lower() in g.name.lower(), self.games))
        self.game_logos = [Logo(0, 0, g.name, g.logo) for g in self.games]
        self.game_choice = Choice(x=self.screen.width / 2, y=int(self.screen.height / 2),
                                  choices=self.game_logos, on_select=self.play,
                                  current=getattr(self.controller, '_last_game_index', None))

        if not len(self.games):
            exit('No games matching name')
        elif len(self.games) == 1:
            self.play(self.game_logos[0])

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

        if len(self.games) == 1:
            self.controller.done = True
        else:
            self.screen.controller = self.controller
            self.controller._last_game_index = self.game_logos.index(game_logo)
            self.controller.reset_scene()
