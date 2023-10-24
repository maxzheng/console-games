from games.controller import Controller
from games.objects import Text, Choice
from games.screen import Scene
from games.geo_bash import GeoBash
from games.number_crush import NumberCrush


class Chooser(Controller):
    name = "Choose a Game"

    def init(self):
        self.scenes = [Choose]


class Choose(Scene):
    def init(self):
        self.game_classes = [GeoBash, NumberCrush]
        self.game_texts = [Text(0, 0, g.name, is_centered=True) for g in self.game_classes]
        self.game_choice = Choice(x=self.screen.width / 2, y=self.screen.height / 2,
                                  choices=self.game_texts, on_select=self.play)

    def start(self):
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
        self.controller.reset_scene()
