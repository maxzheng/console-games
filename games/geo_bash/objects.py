from random import randint, random

from games.screen import Screen
from games.objects import ScreenObject, KeyListener, Square, Explosion, Text, Projectile, Bar


class Player(ScreenObject, KeyListener):
    def __init__(self, name, shape: ScreenObject):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color)

        self.name = name
        self.shape = shape
        self.high_score = 0
        self.is_playing = False
        self.char = shape.char

        self.reset()

    @property
    def is_active(self):
        return self.is_visible and self.is_playing

    def reset(self):
        self.score = 0
        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height - self.size

    def render(self, screen: Screen):
        super().render(screen)
        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        self.screen.border.status['bashed'] = ('{} (High: {})'.format(
            self.score, self.high_score) if self.score < self.high_score else self.score)

        if (self.screen.renders % 2 == 0 or self.char == '!') and self.is_active:
            if self.char == '!':
                color = self.screen.colors[int(self.screen.renders / 2) % len(self.screen.colors)]
            else:
                color = self.color

            if self.char == 'O':
                projectile = Bar(self.x+1, self.y-1, char=self.char, parent=self, color=color,
                                 y_delta=-1)
            else:
                projectile = Projectile(self.x, self.y-1, shape=self.char, parent=self, color=color)

            self.kids.add(projectile)
            self.screen.add(projectile)

    def got_bashed(self):
        self.is_visible = False
        self.screen.add(Explosion(self.x, self.y, size=20,
                                  on_finish=self.reset))
        self.screen.add(Text((self.screen.width - 10) / 2,
                             self.screen.height / 2, 'You got BASHED!!'))

    def left_pressed(self):
        if self.is_active and self.x > 3:
            self.x -= 2

    def right_pressed(self):
        if self.is_active and self.x < self.screen.width - 2:
            self.x += 2

    def up_pressed(self):
        if self.is_active and self.y > 2:
            self.y -= 1

    def down_pressed(self):
        if self.is_active and self.y < self.screen.height - 3:
            self.y += 1


class Boss(Player):
    def __init__(self, name, shape: ScreenObject, player: Player):
        super().__init__(name, shape)
        self.player = player

    def reset(self):
        super().reset()
        self.size = 5
        self.y = -5
        self.y_delta = 0.1
        self.x_delta = max(random() * 0.5, 0.2)
        self.kids = set()
        self.is_hit = False
        if self.screen:
            self.x = randint(5, self.screen.width - 5)
            self.color = self.screen.COLOR_GREEN

    def render(self, screen: Screen):
        super().render(screen)

        if self in screen:
            for projectile in self.kids:
                if projectile.coords & self.player.coords:
                    self.player.got_bashed()

        if self.player.is_visible:
            if self.boss in self.screen:
                # self.screen.border.status['boss'] = str((int(self.boss.x), int(self.boss.y), self.boss.size))
                if self.player.char == '^':
                    self.boss.x_delta = 0

                if self.boss.x > self.player.x:
                    self.boss.x_delta = -1 * abs(self.boss.x_delta)
                else:
                    self.boss.x_delta = abs(self.boss.x_delta)
                if self.boss.y > self.screen.height + 2.5:
                    self.boss.y = -2.5

                if self.boss.is_hit:
                    self.boss.color = self.screen.colors[self.screen.renders % len(self.screen.colors)]
                    if self.screen.renders % 10 == 0:
                        if self.boss.size >= 4:
                            self.boss.color = self.screen.COLOR_GREEN
                        elif self.boss.size >= 3:
                            self.boss.color = self.screen.COLOR_YELLOW
                        else:
                            self.boss.color = self.screen.COLOR_RED
                        self.boss.is_hit = False

            # else:
            #    self.screen.border.status['boss'] = 'Dead'

            if self.screen.renders % 30 == 0 and self.boss in self.screen:
                projectile = Bar(self.boss.x, self.boss.y+self.boss.size/2, size=self.boss.size,
                                 parent=self.boss, color=self.boss.color, y_delta=0.5,
                                 char=self.boss.char)
                self.boss.kids.add(projectile)
                self.screen.add(projectile)


class Enemies(ScreenObject):
    def __init__(self, max_enemies=5, player=None):
        super().__init__(0, 0)
        self.boss = Boss('Max', Square(0, -5, size=5, char='$', y_delta=0.1, solid=True),
                         player=player)
        self.max_enemies = max_enemies
        self.enemies = set()
        self.player = player

    def render(self, screen: Screen):
        super().render(screen)

        # Create enemies
        if len(self.enemies) < self.max_enemies:
            enemy = Square(randint(3, self.screen.width-3), -3, size=randint(2, 4),
                           y_delta=random() * self.player.score / 200 + 0.2)
            self.enemies.add(enemy)
            self.screen.add(enemy)

        for enemy in list(self.enemies):
            # Make them go fast when player got bashed
            if not self.player.is_visible:
                enemy.y_delta += 0.5

            # Add boss every 50 bashes
            if self.player.score and self.player.score % 50 == 0 and self.boss not in self.screen:
                self.enemies.add(self.boss)
                self.screen.add(self.boss)

            # If it is out of the screen, remove it (except for boss or player has been bashed)
            if enemy.is_out and (enemy != self.boss or self.player.is_visible):
                self.enemies.remove(enemy)
                self.screen.remove(enemy)

            # Otherwise, check if player's projectiles hit the enemies
            else:
                for projectile in list(self.player.kids):
                    if projectile.coords & enemy.coords:
                        if enemy == self.boss and self.boss.size > 2.05:
                            self.boss.size -= 0.05
                            self.boss.is_hit = True
                            break

                        self.enemies.remove(enemy)
                        self.screen.remove(enemy)

                        self.player.kids.remove(projectile)
                        self.screen.remove(projectile)

                        explosion_size = 25 if enemy == self.boss else enemy.size * 3
                        self.screen.add(Explosion(enemy.x, enemy.y, size=explosion_size))

                        self.player.score += 5 if enemy == self.boss else 1
                        if self.player.score > self.player.high_score:
                            self.player.high_score = self.player.score

                        break
                else:
                    if enemy.coords & self.player.coords:
                        self.player.got_bashed()
