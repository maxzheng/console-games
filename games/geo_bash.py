from random import randint, random

from games.controller import Controller
from games.objects import (Square, Circle, Projectile, Explosion, Text, Monologue, Triangle,
                           Diamond)


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        self.max_enemies = 5
        self.player = Diamond(self.screen.width / 2, self.screen.height - 3, size=3,
                              color=self.screen.COLOR_YELLOW, name='Jon')
        self.player = Triangle(self.screen.width / 2, self.screen.height - 3, size=3,
                               color=self.screen.COLOR_BLUE, name='Kate')
        self.player = Circle(self.screen.width / 2, self.screen.height - 3, size=3,
                             color=self.screen.COLOR_RED, name='Nina')
        self.projectile = self.player.char.lower()
        self.high_score = 0
        self.reset()

        def bash():
            self.start = True

        # After reset actions
        self.start = False
        self.intro = Monologue(self.player.x, self.player.y - 2, on_finish=bash,
                               texts=["Hi, I am {}!".format(self.player.name),
                                      "Most people don't like geometry, but not me.",
                                      "I LOVE to bash them!! :D",
                                      "Move me using arrow keys.",
                                      "Ready? Let's BASH!!"])
        self.screen.add(self.intro)

    def reset(self):
        self.enemies = set()
        self.screen.reset()
        self.screen.add(self.player)
        self.score = 0
        self.player.is_visible = True
        self.start = True

    def process(self):
        super().process()

        for enemy in list(self.enemies):
            if not self.player.is_visible:
                enemy.y_delta += 0.5

            if enemy.is_out:
                self.enemies.remove(enemy)
            else:
                for projectile in list(self.player.kids):
                    if projectile.coords & enemy.coords:
                        self.enemies.remove(enemy)
                        self.screen.remove(enemy)

                        self.player.kids.remove(projectile)
                        self.screen.remove(projectile)

                        self.screen.add(Explosion(enemy.x, enemy.y, size=enemy.size * 3))

                        self.score += 1
                        if self.score > self.high_score:
                            self.high_score = self.score
                        break
                else:
                    if enemy.coords & self.player.coords:
                        self.player.is_visible = False
                        self.screen.add(Explosion(self.player.x, self.player.y, size=20,
                                                  on_finish=lambda: self.reset()))
                        self.screen.add(Text((self.screen.width - 10) / 2,
                                             self.screen.height / 2, 'You got BASHED!!'))

        if self.start:
            if len(self.enemies) < self.max_enemies and self.player.is_visible:
                enemy = Square(randint(3, self.screen.width-3), -3, size=randint(2, 4),
                               y_delta=random() * self.score / 100 + 0.25)
                self.enemies.add(enemy)
                self.screen.add(enemy)

            if self.player.is_visible and self.screen.renders % 2 == 0:
                projectile = Projectile(self.player.x, self.player.y, shape=self.projectile,
                                        parent=self.player, color=self.player.color)
                self.player.kids.add(projectile)
                self.screen.add(projectile)

        self.screen.border.status['bashed'] = ('{} (High: {})'.format(self.score, self.high_score)
                                               if self.score < self.high_score else self.score)

    def key_pressed(self, key):
        if self.intro in self.screen.objects:
            self.start = True
            self.screen.remove(self.intro)

    def left_pressed(self):
        if self.player.x > 3:
            self.player.x -= 2

    def right_pressed(self):
        if self.player.x < self.screen.width - 2:
            self.player.x += 2

    def up_pressed(self):
        if self.player.y > 2:
            self.player.y -= 1

    def down_pressed(self):
        if self.player.y < self.screen.height - 3:
            self.player.y += 1

    def space_pressed(self):
        pass

    def escape_pressed(self):
        exit()
