from random import randint, random, choice

from games.screen import Screen
from games.objects import ScreenObject, KeyListener, Zombie, Explosion, Text, Projectile


class Player(ScreenObject, KeyListener):
    def __init__(self, name, shape: ScreenObject):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color)

        self.name = name
        self.shape = shape
        self.high_score = 0
        self.is_playing = False
        self.char = shape.char
        self.delta_index = 0
        self.deltas = ((0, -1, '|'), (1, -1, '/'), (1, 0, '-'), (1, 1, '\\'), (0, 1, '|'), (-1, 1, '/'),
                       (-1, 0, '-'), (-1, -1, '\\'))

        self.reset()

    @property
    def is_alive(self):
        return self.is_visible and self.is_playing

    def reset(self):
        super().reset()
        self.score = 0
        self.is_visible = True
        self.size = 1
        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height / 2

    def render(self, screen: Screen):
        super().render(screen)
        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        self.screen.border.status['killed'] = ('{} (High: {})'.format(
            self.score, self.high_score) if self.score < self.high_score else self.score)

        if (self.screen.renders % 2 == 0) and self.is_alive:
            x_delta, y_delta, shape = self.deltas[self.delta_index]
            projectile = Projectile(self.x, self.y, shape=shape, parent=self,
                                    x_delta=x_delta, y_delta=y_delta)

            self.kids.add(projectile)
            self.screen.add(projectile)

    def got_zombified(self):
        self.is_visible = False

        self.screen.add(Text((self.screen.width - 10) / 2, self.screen.height / 2, 'You got ZOMBIFIED!!'))
        self.screen.add(Explosion(self.x, self.y, size=20,
                                  on_finish=self.controller.reset_scene))

    def left_pressed(self):
        if self.is_alive:
            if self.delta_index > 0:
                self.delta_index -= 1
            else:
                self.delta_index = len(self.deltas) - 1

    def right_pressed(self):
        if self.is_alive:
            if self.delta_index < len(self.deltas) - 1:
                self.delta_index += 1
            else:
                self.delta_index = 0

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass


class Boss(ScreenObject):
    def __init__(self, name, shape: ScreenObject, player: Player = None):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color)
        self.shape = shape
        self.player = player
        self.size = 5
        self.y = -5
        self.y_delta = 0.1
        self.x_delta = max(random() * 0.5, 0.2)
        self.is_hit = False
        self.char = shape.char

    def render(self, screen: Screen):
        super().render(screen)
        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        if not self.color:
            self.color = self.screen.COLOR_GREEN

        if self in screen:
            for projectile in self.kids:
                if projectile.coords & self.player.coords:
                    self.player.got_zombified()

        if self in self.screen:
            # self.screen.border.status['boss'] = str((int(self.x), int(self.y), self.size))
            if self.x > self.player.x:
                self.x_delta = -1 * abs(self.x_delta)
            else:
                self.x_delta = abs(self.x_delta)

            if self.y > self.screen.height + 2.5 and self.player.is_alive:
                self.y = -2.5

            if self.is_hit:
                self.color = self.screen.colors[self.screen.renders % len(self.screen.colors)]
                self.is_hit = False

            # else:
            #   self.screen.border.status['boss'] = 'Dead'


class Enemies(ScreenObject):
    def __init__(self, max_enemies=5, player=None):
        super().__init__(0, 0)
        self.max_enemies = max_enemies
        self.enemies = set()
        self.player = player
        self.boss = None

    def render(self, screen: Screen):
        super().render(screen)

        # Create enemies
        if len(self.enemies) < self.max_enemies + int(self.player.score / 100):
            if random() < 0.5:
                x = choice([0, screen.width])
                y = randint(0, screen.height)
            else:
                y = choice([0, screen.height])
                x = randint(0, screen.width)

            speed = random() * self.player.score / 200 + 0.2
            x_sign = 1 if x < self.player.x else -1
            y_sign = 1 if y < self.player.y else -1
            enemy = Zombie(x, y, x_delta=x_sign * speed, y_delta=y_sign * speed)
            self.enemies.add(enemy)
            self.screen.add(enemy)

        for enemy in list(self.enemies):
            # Make them go fast when player got zombified
            if not self.player.is_visible:
                enemy.y_delta *= 1.1
                enemy.x_delta *= 1.1

            # Add boss every 50 killed
            if self.player.score and self.player.score % 50 == 0 and self.boss not in screen and self.player.is_alive:
                self.boss = Boss('Max',
                                 Zombie(randint(5, screen.width - 5), -5,
                                        y_delta=0.1, color=screen.COLOR_GREEN),
                                 player=self.player)
                self.enemies.add(self.boss)
                screen.add(self.boss)

            # If it is out of the screen, remove it (except for boss or player has been zombified)
            if enemy.is_out and (enemy != self.boss and self.player.is_alive):
                self.enemies.remove(enemy)
                screen.remove(enemy)

            # Otherwise, check if player's projectiles hit the enemies
            else:
                for projectile in list(self.player.kids):
                    if projectile.coords & enemy.coords:
                        if enemy == self.boss:
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
                        self.player.got_zombified()
