from random import randint, random, choice

from games.screen import Screen
from games.objects import (Zombie, Explosion, Projectile, Monologue,
                           DyingZombie, AbstractPlayer, AbstractEnemies, CompassionateBoss)


class Player(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        self.ammos_limit = 1000
        self.gas_limit = 100
        self.left_deltas = (-3, 0)
        self.right_deltas = (3, 0)
        self.projectile_deltas = self.right_deltas

        super().__init__(*args, score_title='Killed', **kwargs)

    def reset(self):
        super().reset()
        self.sync(self.shape)

        # Grenade upgrade when score reaches 100
        self.grenades_limit = 10
        self.grenades = self.grenades_limit
        self.grenades_enabled = True

        # Machine gun upgrade when score reaches 50
        self.gas = self.gas_limit

        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height / 2
            self.screen.status.pop('Grenades', None)
            self.screen.status.pop('Gas', None)

    def render(self, screen: Screen):
        super().render(screen)

        if self.active:
            x_delta, y_delta = self.projectile_deltas

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

        if self.grenades_enabled:
            screen.border.status['Grenades'] = self.grenades

        screen.border.status['Gas'] = '{}%'.format(int(self.gas))

    def destroy(self):
        super().destroy(msg='You got ZOMBIFIED!!', explosion_size=30)
        self.screen.add(Zombie(self.shape.x, self.shape.y, color=self.screen.COLOR_GREEN, y_delta=-0.1))

    def left_pressed(self):
        if self.alive:
            if self.x > self.size / 2:
                self.x -= 1
            self.projectile_deltas = self.left_deltas

    def right_pressed(self):
        if self.alive:
            if self.x < self.screen.width - self.size / 2:
                self.x += 1

            self.projectile_deltas = self.right_deltas

    def up_pressed(self):
        if self.alive:
            if self.y > self.size / 2:
                self.y -= 1

    def down_pressed(self):
        if self.alive:
            if self.y < self.screen.height - self.size / 2:
                self.y += 1

    def space_pressed(self):
        if self.grenades_enabled and self.grenades > 0 and self.alive:
            self.grenades -= 1
            x_delta, y_delta = self.deltas
            explosion = Explosion(self.x, self.y, size=min(self.screen.width, self.screen.height),
                                  parent=self)
            projectile = Projectile(self.x, self.y, shape=chr(0x274d), parent=self,
                                    x_delta=x_delta, y_delta=y_delta, color=self.color,
                                    explode_after_renders=10,
                                    explosion=explosion, explosions=5)
            self.kids.add(projectile)
            self.screen.add(projectile)


class Enemies(AbstractEnemies):
    def create_enemy(self):
        if random() < 0.5:
            x = choice([0, self.screen.width])
            y = randint(0, self.screen.height)
        else:
            y = choice([0, self.screen.height])
            x = randint(0, self.screen.width)

        speed = random() * self.player.score / 10000 + 0.2
        x_sign = (1 if x < self.player.x else -1) * random()
        y_sign = (1 if y < self.player.y else -1) * random()

        return Zombie(x, y, x_delta=x_sign * speed, y_delta=y_sign * speed, random_start=True)

    def on_death(self, enemy):
        zombie = DyingZombie(enemy.x, enemy.y, color=self.screen.COLOR_RED)
        self.screen.add(zombie)

    def should_spawn_boss(self):
        return self.player.score and self.player.score % 50 == 0

    def create_boss(self):
        return CompassionateBoss('Max',
                                 Zombie(randint(5, self.screen.width - 5), -5,
                                        y_delta=0.1, color=self.screen.COLOR_GREEN, random_start=True),
                                 self.player,
                                 hp=self.player.score/25)
