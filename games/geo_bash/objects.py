from random import randint, random

from games.screen import Screen
from games.objects import (Square, Explosion, Projectile, Bar, AbstractPlayer,
                           AbstractEnemies, CompassionateBoss)


class Player(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, score_title='Bashed', **kwargs)

    def reset(self):
        super().reset()
        self.continuous_moves = 0
        self.size = 3
        self.active = False
        if self.screen:
            self.x = int(self.screen.width / 2)
            self.y = self.screen.height - self.size

    def render(self, screen: Screen):
        super().render(screen)

        # Cap it
        move_cap = 100 if self.char == '^' else 5
        if self.continuous_moves > move_cap:
            self.continuous_moves = move_cap

        if self.continuous_moves % 30 == 0 and self.char == '^':
            self.size = max(1, 3 - self.continuous_moves / 30)

        if (self.screen.renders % 2 == 0 or self.char == '!') and self.active:
            if self.char == '!':
                color = self.screen.rainbow_colors[int(self.screen.renders / 2) % len(self.screen.rainbow_colors)]
            else:
                color = self.color

            if self.char == 'O':
                for x_delta in range(-1, 2):
                    projectile = Projectile(self.x + x_delta, self.y-1, shape=self.char, parent=self,
                                            color=color)
                    self.kids.add(projectile)
                    self.screen.add(projectile)
            else:
                projectile = Projectile(self.x, self.y-1, shape=self.char, parent=self, color=color)
                self.kids.add(projectile)
                self.screen.add(projectile)

    def destruct(self):
        super().destruct(msg='You got BASHED!!')

    def left_pressed(self):
        if self.continuous_moves >= 5:
            speed = 3 if self.char == '!' else 2
        else:
            speed = 1
        if self.active:
            if self.x - speed >= 1:
                self.x -= speed
                self.continuous_moves += 1
            elif self.x - 1 >= 1:
                self.x -= 1
                self.continuous_moves += 1

    def right_pressed(self):
        if self.continuous_moves >= 5:
            speed = 3 if self.char == '!' else 2
        else:
            speed = 1
        if self.active:
            if self.x + speed < self.screen.width - 1:
                self.x += speed
                self.continuous_moves += 1
            elif self.x + 1 < self.screen.width - 1:
                self.x += 1
                self.continuous_moves += 1

    def up_pressed(self):
        if self.active and self.y >= self.size:
            self.y -= 1
            self.continuous_moves += 1

    def down_pressed(self):
        if self.active and self.y < self.screen.height - self.size:
            self.y += 1
            self.continuous_moves += 1

    def key_released(self):
        if self.continuous_moves >= 1:
            self.continuous_moves -= 1


class Boss(CompassionateBoss):
    def got_hit(self):
        self.size = int(self.hp / self.max_hp * 3 + 2)

        if self.screen.renders % 10 == 0:
            if self.size >= 4:
                self.color = self.screen.COLOR_GREEN
            elif self.size >= 3:
                self.color = self.screen.COLOR_YELLOW
            else:
                self.color = self.screen.COLOR_RED

            return False
        else:
            return True

    def render(self, screen: Screen):
        super().render(screen)

        if not self.color:
            self.color = self.screen.COLOR_GREEN

        if self in screen:
            for projectile in self.kids:
                if projectile.coords & self.player.coords:
                    self.player.destruct()

            if self.player.size == 1 or not self.player.alive:
                self.x_delta = 0
            elif not self.x_delta:
                self.x_delta = self.initial_x_delta

            if self.screen.renders % 60 == 0 and self in self.screen:
                projectile = Bar(self.x, self.y+self.size/2, size=self.size,
                                 parent=self, color=self.color, y_delta=0.5,
                                 char=self.char)
                self.kids.add(projectile)
                self.screen.add(projectile)


class Enemies(AbstractEnemies):
    def create_enemy(self):
        return Square(randint(3, self.screen.width-3), -3, size=randint(2, 4),
                      y_delta=random() * self.player.score / 200 + 0.2)

    def on_death(self, enemy):
        """ Optionally add custom actions when an enemy dies """
        explosion_size = 25 if enemy == self.boss else enemy.size * 3
        self.screen.add(Explosion(enemy.x, enemy.y, size=explosion_size))

    def should_spawn_boss(self):
        """ Override this to customize logic for when a boss should be created """
        return self.player.score and self.player.score % 50 == 0

    def create_boss(self):
        return Boss('Max',
                    Square(randint(5, self.screen.width - 5), -5, size=5, char='$',
                           y_delta=0.1, solid=True, color=self.screen.COLOR_GREEN),
                    player=self.player,
                    hp=self.player.score)

    def additional_enemies(self):
        """ Increase enemies as the player levels up """
        return int(self.player.score / 100)
