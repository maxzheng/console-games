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
    def is_alive(self):
        return self.is_visible and self.is_playing

    def reset(self):
        super().reset()
        self.score = 0
        self.is_visible = True
        self.continuous_moves = 0
        self.size = 3
        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height - self.size

    def render(self, screen: Screen):
        super().render(screen)
        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        if self.continuous_moves % 30 == 0 and self.char == '^':
            self.size = max(1, 3 - self.continuous_moves / 30)

            # Cap it
            move_cap = 100 if self.char == '^' else 5
            if self.continuous_moves > move_cap:
                self.continuous_moves = move_cap

        self.screen.border.status['bashed'] = ('{} (High: {})'.format(
            self.score, self.high_score) if self.score < self.high_score else self.score)

        if (self.screen.renders % 2 == 0 or self.char == '!') and self.is_alive:
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

        self.screen.add(Text((self.screen.width - 10) / 2, self.screen.height / 2, 'You got BASHED!!'))
        self.screen.add(Explosion(self.x, self.y, size=20,
                                  on_finish=self.controller.reset_scene))

    def left_pressed(self):
        if self.continuous_moves > 3:
            speed = 3 if self.char == '!' else 2
        else:
            speed = 1
        if self.is_alive:
            if self.x - speed >= 1:
                self.x -= speed
                self.continuous_moves += 1
            elif self.x - 1 >= 1:
                self.x -= 1
                self.continuous_moves += 1

    def right_pressed(self):
        if self.continuous_moves > 3:
            speed = 3 if self.char == '!' else 2
        else:
            speed = 1
        if self.is_alive:
            if self.x + speed < self.screen.width - 1:
                self.x += speed
                self.continuous_moves += 1
            elif self.x + 1 < self.screen.width - 1:
                self.x += 1
                self.continuous_moves += 1

    def up_pressed(self):
        if self.is_alive and self.y >= self.size:
            self.y -= 1
            self.continuous_moves += 1

    def down_pressed(self):
        if self.is_alive and self.y < self.screen.height - self.size:
            self.y += 1
            self.continuous_moves += 1

    def key_released(self):
        if self.continuous_moves >= 1:
            self.continuous_moves -= 1


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
                    self.player.got_bashed()

        if self in self.screen:
            if self.player.score < 100 or self.player.char == '^':
                self.x_delta = 0

            # self.screen.border.status['boss'] = str((int(self.x), int(self.y), self.size))
            if self.player.char == '^':
                self.x_delta = 0

            if self.x > self.player.x:
                self.x_delta = -1 * abs(self.x_delta)
            else:
                self.x_delta = abs(self.x_delta)

            if self.y > self.screen.height + 2.5 and self.player.is_alive:
                self.y = -2.5

            if self.is_hit:
                self.color = self.screen.colors[self.screen.renders % len(self.screen.colors)]
                if self.screen.renders % 10 == 0:
                    if self.size >= 4:
                        self.color = self.screen.COLOR_GREEN
                    elif self.size >= 3:
                        self.color = self.screen.COLOR_YELLOW
                    else:
                        self.color = self.screen.COLOR_RED
                    self.is_hit = False

            # else:
            #   self.screen.border.status['boss'] = 'Dead'

            if self.screen.renders % 60 == 0 and self in self.screen:
                projectile = Bar(self.x, self.y+self.size/2, size=self.size,
                                 parent=self, color=self.color, y_delta=0.5,
                                 char=self.char)
                self.kids.add(projectile)
                self.screen.add(projectile)


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
            enemy = Square(randint(3, self.screen.width-3), -3, size=randint(2, 4),
                           y_delta=random() * self.player.score / 200 + 0.2)
            self.enemies.add(enemy)
            self.screen.add(enemy)

        for enemy in list(self.enemies):
            # Make them go fast when player got bashed
            if not self.player.is_visible:
                enemy.y_delta += 0.5

            # Add boss every 50 bashes
            if self.player.score and self.player.score % 50 == 0 and self.boss not in screen and self.player.is_alive:
                self.boss = Boss('Max',
                                 Square(randint(5, screen.width - 5), -5, size=5, char='$',
                                        y_delta=0.1, solid=True, color=screen.COLOR_GREEN),
                                 player=self.player)
                self.enemies.add(self.boss)
                screen.add(self.boss)

            # If it is out of the screen, remove it (except for boss or player has been bashed)
            if enemy.is_out and (enemy != self.boss and self.player.is_alive):
                self.enemies.remove(enemy)
                screen.remove(enemy)

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
