from games.controller import Controller
from games.objects import Choice
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
        self.game_classes = [GeoBash, NumberCrush, LastSurvivor]
        self.game_texts = [g.Logo(0, 0, g.name) for g in self.game_classes]
        self.game_choice = Choice(x=self.screen.width / 2, y=int(self.screen.height / 2),
                                  choices=self.game_texts, on_select=self.play,
                                  current=getattr(self.controller, '_last_game_index', None))

    def start(self):
        self.screen.reset(border=True)
        self.screen.add(self.game_choice)

    def escape_pressed(self):
        self.controller.done = True

    def play(self, game_text):
        game_class = self.game_classes[self.game_texts.index(game_text)]
        game = game_class(self.screen)
        self.screen.controller = game
        self.screen.reset()

        while not game.done:
            self.screen.render()
            game.play()

        self.screen.controller = self.controller
        self.controller._last_game_index = self.game_texts.index(game_text)
        self.controller.reset_scene()
