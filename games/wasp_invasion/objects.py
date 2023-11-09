from random import randint, random, choice

from games.screen import Screen
from games.objects import (Wasp, Explosion, Projectile, Monologue,
                           DyingWasp, AbstractPlayer, AbstractEnemies, CompassionateBoss)


class Player(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        self.gas_limit = 100
        self.left_deltas = (-3, 0)
        self.right_deltas = (3, 0)
        self.projectile_deltas = self.right_deltas

        super().__init__(*args, score_title='Killed', **kwargs)

    def reset(self):
        super().reset()
        self.sync(self.shape)

        self.gas = self.gas_limit
        self.flame_on = True

        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height - 2
            self.screen.status.pop('Gas', None)

    def render(self, screen: Screen):
        super().render(screen)

        if self.active:
            if self.y_delta:
                # Jumps up
                if self.y_delta < 0:
                    self.y_delta *= 0.9

                    if self.y_delta > -0.2:
                        self.y_delta *= -1

                # Comes back down
                else:
                    if self.y_delta < 0.5:
                        self.y_delta *= 1.1

                    if self.y >= self.screen.height - 2.5:
                        self.y_delta = 0

            screen.debug(y=int(self.y), y_delta=round(self.y_delta, 3))

            x_delta, y_delta = self.projectile_deltas

            if self.flame_on:
                if self.gas > 0:
                    for flame_size in range(10):
                        explosion = Explosion(self.x, self.y, size=flame_size, parent=self)
                        projectile = Projectile(self.x, self.y, shape=None, parent=self,
                                                x_delta=x_delta, y_delta=y_delta, color=screen.COLOR_YELLOW,
                                                explode_after_renders=flame_size,
                                                explosion=explosion)
                        self.kids.add(projectile)
                        self.screen.add(projectile)

                if self.gas > 0:
                    self.gas -= 0.01
                else:
                    screen.add(Monologue(self.x, self.y - 2, texts=['Out of gas!!!',
                                                                    'Look for green gas refills']))

        screen.border.status['Gas'] = '{}%'.format(int(self.gas))

    def destroy(self):
        super().destroy(msg='You got STUNG!!', explosion_size=30)
        self.screen.add(Wasp(self.shape.x, self.shape.y, color=self.screen.COLOR_YELLOW, y_delta=-0.1))

    def left_pressed(self):
        if self.alive:
            if self.x > self.size:
                self.x -= 1
            self.projectile_deltas = self.left_deltas

    def right_pressed(self):
        if self.alive:
            if self.x < self.screen.width - self.size:
                self.x += 1

            self.projectile_deltas = self.right_deltas

    def up_pressed(self):
        if self.alive and not self.y_delta:
            self.y_delta = -1

    def down_pressed(self):
        pass

    def space_pressed(self):
        self.flame_on = not self.flame_on


class Enemies(AbstractEnemies):
    def create_enemy(self):
        if random() < 0.5:
            x = choice([0, self.screen.width])
            y = randint(0, self.screen.height)
        else:
            y = 0
            x = randint(0, self.screen.width)

        speed = random() * self.player.score / 10000 + 0.2
        x_sign = (1 if x < self.player.x else -1) * random()
        y_sign = (1 if y < self.player.y else -1) * random()

        return Wasp(x, y, x_delta=x_sign * speed, y_delta=y_sign * speed, random_start=True)

    def on_death(self, enemy):
        wasp = DyingWasp(enemy.x, enemy.y, color=self.screen.COLOR_RED)
        self.screen.add(wasp)

    def should_spawn_boss(self):
        return self.player.score and self.player.score % 50 == 0

    def create_boss(self):
        return CompassionateBoss('Max',
                                 Wasp(randint(5, self.screen.width - 5), -5,
                                      y_delta=0.1, color=self.screen.COLOR_YELLOW, random_start=True),
                                 self.player,
                                 hp=self.player.score/25)
