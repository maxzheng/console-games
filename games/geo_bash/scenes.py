from games.screen import Scene
from games.objects import Circle, Monologue, Triangle, Diamond, Choice
from games.geo_bash.objects import Player, Enemies


class ChoosePlayer(Scene):
    def init(self):
        choices = [
            Player('Kate', Triangle(self.screen.width / 2, self.screen.height - 3, size=3,
                                    color=self.screen.COLOR_BLUE)),
            Player('Nina', Circle(self.screen.width / 2, self.screen.height - 3, size=3,
                                  color=self.screen.COLOR_RED)),
            Player('Jon', Diamond(self.screen.width / 2, self.screen.height - 3, size=3,
                                  color=self.screen.COLOR_YELLOW))
        ]
        self.choice = Choice(self.screen.width / 2, self.screen.height / 2,
                             choices=choices, color=self.screen.COLOR_CYAN,
                             on_select=self.next)

    def start(self):
        self.screen.add(self.choice)

    def next(self, chosen: Player):
        super().next()
        chosen.y = self.screen.height - chosen.size
        chosen.x = self.screen.width / 2
        self.controller.player = chosen
        chosen.controller = self.controller

    def escape_pressed(self):
        self.controller.done = True
        exit()


class Intro(Scene):
    def init(self):
        self.intro = Monologue(self.controller.player.x, self.controller.player.y - 2,
                               on_finish=self.next,
                               texts=["Hi, I am {}!".format(self.controller.player.name),
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
        self.enemies = Enemies(player=self.controller.player)
        self.player.reset()
        self.player.is_playing = True

    def start(self):
        self.screen.add(self.player, self.enemies)

    def escape_pressed(self):
        self.next()
