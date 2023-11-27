from games.screen import Scene
from games.objects import Monologue, Sun, One, Two, Wormhole, Three, Four, Five, Six, Seven
from games.planet_x.objects import (Landscape1, Landscape2, Obstacles, CrabClawEnemies,
                                    AcidBubbleEnemies, VolcanoEnemies, JellyFishEnemies,
                                    CubeEnemies, SpinnerEnemies, XEnemies)


class Intro(Scene):
    def init(self):
        self.screen.border.reset()
        self.controller.player.reset()
        self.controller.player.active = False
        self.controller.player.show_score = False
        self.intro = Monologue(self.controller.player.x - 1, self.controller.player.y + 4,
                               on_finish=self.next,
                               texts=["This is your daily news",
                                      "from the sky with Kate & Kelly.",
                                      "It's a beautiful sunny day!"])
        self.landscapes = (Sun(self.screen.width / 2, 2),
                           Landscape1(0, self.screen.height / 2 - 5, player=self.player),
                           Landscape2(0, self.screen.height / 2, player=self.player))
        self.obstacles = Obstacles(-self.screen.width, self.screen.height - 6, player=self.player)

    def start(self):
        self.screen.add(*self.landscapes, self.obstacles, self.intro, self.controller.player)

    def key_pressed(self, key):
        self.next()

    def escape_pressed(self):
        self.controller.done = True


class WormholeAppeared(Intro):
    def init(self):
        super().init()
        self.intro = Monologue(self.controller.player.x - 1, self.controller.player.y + 4,
                               on_finish=self.next,
                               texts=["Wait...",
                                      "What is that??!!",
                                      "Some kind of wormhole",
                                      "just appeared out of no where!"])
        self.wormhole = Wormhole(self.controller.player.x - 30, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        super().start()
        self.screen.add(self.wormhole)


class WormholeSucks(WormholeAppeared):
    def init(self):
        super().init()
        self.intro = Monologue(self.controller.player.x - 1, self.controller.player.y + 4,
                               texts=["Oh no!!",
                                      "We are being sucked in!!",
                                      "Hold on ti..."])
        self.controller.player.x_delta = -0.2


class Level1(Scene):
    def init(self):
        self.level = One(self.screen.width / 2, self.screen.height / 2, remove_after_renders=30)
        self.player.reset()
        self.player.score = 1
        self.enemies = CrabClawEnemies(self.controller.player, max_enemies=int(self.screen.width/20))
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self
        self.intro = Monologue(self.controller.player.x - 2, self.controller.player.y + 4,
                               texts=["Looks like...",
                                      "We are in another planet.",
                                      "There is nothing,",
                                      "but strange obstacles",
                                      "and a wormhole.",
                                      "Perhaps we can get home thru it.",
                                      "Move me using arrow keys."])

    def start(self):
        self.screen.add(self.level, self.enemies, self.player, self.wormhole, self.intro)

    def escape_pressed(self):
        self.controller.done = True


class Level2(Scene):
    def init(self):
        self.level = Two(self.screen.width / 2, self.screen.height / 2, remove_after_renders=30)
        hp = self.player.hp
        gas = self.player.gas
        self.player.reset()
        self.player.score = 2
        self.player.hp = hp
        self.player.gas = gas

        self.enemies = AcidBubbleEnemies(self.controller.player, max_enemies=int(self.screen.width/17.5))
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        self.screen.add(self.level, self.enemies, self.player, self.wormhole)

    def escape_pressed(self):
        self.controller.done = True


class Level3(Scene):
    def init(self):
        self.level = Three(self.screen.width / 2, self.screen.height / 2, remove_after_renders=30)
        hp = self.player.hp
        gas = self.player.gas
        self.player.reset()
        self.player.score = 3
        self.player.hp = hp
        self.player.gas = gas

        self.enemies = VolcanoEnemies(self.controller.player, max_enemies=int(self.screen.width/15))
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        self.screen.add(self.level, self.enemies, self.player, self.wormhole)

    def escape_pressed(self):
        self.controller.done = True


class Level4(Scene):
    def init(self):
        self.level = Four(self.screen.width / 2, self.screen.height / 2, remove_after_renders=30)
        hp = self.player.hp
        gas = self.player.gas
        self.player.reset()
        self.player.score = 4
        self.player.hp = hp
        self.player.gas = gas

        self.enemies = JellyFishEnemies(self.controller.player, max_enemies=int(self.screen.width/12.5))
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        self.screen.add(self.level, self.enemies, self.player, self.wormhole)

    def escape_pressed(self):
        self.controller.done = True


class Level5(Scene):
    def init(self):
        self.level = Five(self.screen.width / 2, self.screen.height / 2, remove_after_renders=30)
        hp = self.player.hp
        gas = self.player.gas
        self.player.reset()
        self.player.score = 5
        self.player.hp = hp
        self.player.gas = gas

        self.enemies = CubeEnemies(self.controller.player, max_enemies=int(self.screen.width/20))
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        self.screen.add(self.level, self.enemies, self.player, self.wormhole)

    def escape_pressed(self):
        self.controller.done = True


class Level6(Scene):
    def init(self):
        self.level = Six(self.screen.width / 2, self.screen.height / 2, remove_after_renders=30)
        hp = self.player.hp
        gas = self.player.gas
        self.player.reset()
        self.player.score = 6
        self.player.hp = hp
        self.player.gas = gas

        self.enemies = SpinnerEnemies(self.controller.player, max_enemies=int(self.screen.width/17.5))
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        self.screen.add(self.level, self.enemies, self.player, self.wormhole)

    def escape_pressed(self):
        self.controller.done = True


class Level7(Scene):
    def init(self):
        self.level = Seven(self.screen.width / 2, self.screen.height / 2, remove_after_renders=30)
        hp = self.player.hp
        gas = self.player.gas
        self.player.reset()
        self.player.score = 7
        self.player.hp = hp
        self.player.gas = gas

        size = int(self.screen.height / 3)
        max_enemies = max(1, int((self.screen.width - 30) / (size * 2)))
        self.enemies = XEnemies(self.controller.player, max_enemies=max_enemies, size=size)
        self.wormhole = Wormhole(6, self.screen.height / 2)
        self.wormhole.player = self.controller.player
        self.wormhole.scene = self

    def start(self):
        self.screen.add(self.level, self.enemies, self.player, self.wormhole)

    def escape_pressed(self):
        self.controller.done = True


class Home(Scene):
    def init(self):
        self.controller.player.reset()
        self.controller.player.active = False
        self.controller.player.x = self.screen.width / 2
        self.controller.player.y = self.screen.height / 2
        self.controller.player.color = 'red'
        self.controller.player.show_score = False

        self.screen.border.reset()

        self.outro = Monologue(self.controller.player.x - 1, self.controller.player.y + 4,
                               texts=["Yay!! We are finally home!",
                                      "Listeners, you would not believe",
                                      "the strange things that we had seen...",
                                      "We will tell you next time.",
                                      "For now, we need a rest and vacation!",
                                      "This is Kate & Kelly signing out.",
                                      "THE END",
                                      "Press Space to play again or Esc to exit"])
        self.landscapes = (Sun(self.screen.width / 2, 2),
                           Landscape1(0, self.screen.height / 2 - 5, player=self.player),
                           Landscape2(0, self.screen.height / 2, player=self.player))
        self.obstacles = Obstacles(-self.screen.width, self.screen.height - 6, player=self.player)

    def start(self):
        self.screen.add(*self.landscapes, self.obstacles, self.outro, self.controller.player)

    def escape_pressed(self):
        self.controller.done = True

    def space_pressed(self):
        self.next()
