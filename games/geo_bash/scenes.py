from games.screen import Scene
from games.objects import Circle, Monologue, Triangle, Diamond, Choice
from games.geo_bash.objects import Player, Enemies


class ChoosePlayer(Scene):
    def init(self):
        choices = [
            Player('Kate', Triangle(int(self.screen.width / 2), self.screen.height - 3, size=3,
                                    color=self.screen.COLOR_BLUE), self.controller),
            Player('Nina', Circle(int(self.screen.width / 2), self.screen.height - 3, size=3,
                                  color=self.screen.COLOR_RED), self.controller),
            Player('Jon', Diamond(int(self.screen.width / 2), self.screen.height - 3, size=3,
                                  color=self.screen.COLOR_YELLOW), self.controller)
        ]
        self.choice = Choice(self.screen.width / 2, self.screen.height / 2,
                             choices=choices, color=self.screen.COLOR_CYAN,
                             on_select=self.next,
                             current=getattr(self.controller, '_last_player_index', None))

    def start(self):
        self.screen.add(self.choice)

    def next(self, chosen: Player):
        super().next()
        chosen.y = self.screen.height - chosen.size
        chosen.x = self.screen.width / 2
        self.controller.player = chosen
        self.controller._last_player_index = self.choice.choices.index(chosen)
        chosen.controller = self.controller

    def escape_pressed(self):
        self.controller.done = True


class Intro(Scene):
    def init(self):
        if self.controller.player.name == 'Jon':
            intro = 'the fastest shape'
        elif self.controller.player.name == 'Kate':
            intro = 'the stealthiest shape'
        else:
            intro = 'the most powerful shape'
        self.intro = Monologue(self.controller.player.x, self.controller.player.y - 2,
                               on_finish=self.next,
                               texts=["Hi, I am {} -- {}!".format(self.controller.player.name, intro),
                                      "Most people don't like geometry, but not me.",
                                      "I LOVE to bash them!! :D",
                                      "Move me using arrow keys.",
                                      "Ready? Let's BASH!!"])
        self.controller.player.reset()

    def start(self):
        self.screen.add(self.intro, self.controller.player)

    def key_pressed(self, key):
        self.next()


class Bash(Scene):
    def init(self):
        self.enemies = Enemies(self.controller.player)
        self.player.reset()
        self.controller.player.active = True

    def start(self):
        self.screen.add(self.player, self.enemies)

    def escape_pressed(self):
        self.next()
