from random import randint, random

from games.controller import Controller
from games.objects import Square, Circle, Projectile, Explosion, Text


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        self.max_enemies = 5
        self.projectile = 'o'
        self.player = Circle(self.screen.width / 2, self.screen.height - 3, size=3, color=self.screen.COLOR_RED)
        self.high_score = 0
        self.reset()

    def reset(self):
        self.enemies = set()
        self.screen.reset()
        self.screen.add(self.player)
        self.score = 0
        self.player.is_visible = True

    def process(self):
        super().process()

        for enemy in list(self.enemies):
            if enemy.is_out:
                self.enemies.remove(enemy)
            else:
                for projectile in list(self.player.kids):
                    if projectile.coords & enemy.coords:
                        self.enemies.remove(enemy)
                        self.screen.remove(enemy)

                        self.player.kids.remove(projectile)
                        self.screen.remove(projectile)

                        self.screen.add(Explosion(enemy.x, enemy.y, size=enemy.size * 2))

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

        if len(self.enemies) < self.max_enemies:
            enemy = Square(randint(3, self.screen.width-3), -3, size=randint(2, 4),
                           y_delta=random() + 0.2)
            self.enemies.add(enemy)
            self.screen.add(enemy)

        self.screen.border.status['score'] = ('{} (High: {})'.format(self.score, self.high_score)
                                              if self.score < self.high_score else self.score)

    def left_pressed(self):
        if self.player.x > 3:
            self.player.x -= 1

    def right_pressed(self):
        if self.player.x < self.screen.width - 2:
            self.player.x += 1

    def up_pressed(self):
        if self.player.y > 2:
            self.player.y -= 1

    def down_pressed(self):
        if self.player.y < self.screen.height - 3:
            self.player.y += 1

    def space_pressed(self):
        if self.player.is_visible:
            projectile = Projectile(self.player.x, self.player.y, shape=self.projectile,
                                    parent=self.player, color=self.player.color)
            self.player.kids.add(projectile)
            self.screen.add(projectile)

    def escape_pressed(self):
        exit()
