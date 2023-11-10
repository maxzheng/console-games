from random import randint, random, choice

from games.screen import Screen
from games.objects import (Zombie, Explosion, Projectile, Monologue,
                           DyingZombie, AbstractPlayer, AbstractEnemies, CompassionateBoss)


class Player(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        self.delta_index = 0
        self.ammos_limit = 1000
        self.gas_limit = 100
        self.deltas = ((0, -1, '|'), (1, -1, '/'), (1, 0, '-'), (1, 1, '\\'), (0, 1, '|'), (-1, 1, '/'),
                       (-1, 0, '-'), (-1, -1, '\\'))

        super().__init__(*args, score_title='Killed', **kwargs)

    def reset(self):
        super().reset()
        self.sync(self.shape)
        self.color = None
        self.delta_index = 0

        # Machine gun upgrade when score reaches 50
        self.ammos = self.ammos_limit
        self.using_machine_gun = False
        self.machine_gun_enabled = False

        # Grenade upgrade when score reaches 100
        self.grenades_limit = 10
        self.grenades = self.grenades_limit
        self.grenades_enabled = False

        # Machine gun upgrade when score reaches 50
        self.gas = self.gas_limit
        self.using_flamethrower = False
        self.flamethrower_enabled = False

        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height / 2
            self.screen.status.pop('Ammos', None)
            self.screen.status.pop('Grenades', None)
            self.screen.status.pop('Gas', None)

    def render(self, screen: Screen):
        super().render(screen)

        if (self.screen.renders % 2 == 0 or self.using_machine_gun or self.using_flamethrower) and self.active:
            x_delta, y_delta, shape = self.deltas[self.delta_index]
            if self.using_machine_gun or self.using_flamethrower:
                x_delta *= 2
                y_delta *= 2
                color = screen.COLOR_YELLOW
                if self.using_flamethrower:
                    shape = None
            else:
                shape = chr(183)
                color = None
            if (not self.using_machine_gun or self.using_machine_gun and self.ammos > 0
                    or self.using_flamethrower and self.gas > 0):
                if self.using_flamethrower:
                    for flame_size in range(10):
                        explosion = Explosion(self.x, self.y, size=flame_size, parent=self)
                        projectile = Projectile(self.x, self.y, shape=shape, parent=self,
                                                x_delta=x_delta, y_delta=y_delta, color=color,
                                                explode_after_renders=flame_size,
                                                explosion=explosion)
                        self.kids.add(projectile)
                        self.screen.add(projectile)
                else:
                    projectile = Projectile(self.x, self.y, shape=shape, parent=self,
                                            x_delta=x_delta, y_delta=y_delta, color=color)
                    self.kids.add(projectile)
                    self.screen.add(projectile)

        if self.using_machine_gun:
            if self.ammos > 0:
                self.ammos -= 1
            else:
                self.using_machine_gun = False
                screen.add(Monologue(self.x, self.y - 1, texts=['Out of ammo!!!',
                                                                'Wait for reload before upgrading.']))
        elif self.ammos < self.ammos_limit:
            self.ammos += 1

        if self.using_flamethrower:
            if self.gas > 0:
                self.gas -= 0.5
            else:
                self.using_flamethrower = False
                self.using_machine_gun = True
                screen.add(Monologue(self.x, self.y - 1, texts=['Out of gas!!!',
                                                                'Wait for refill before upgrading.']))
        elif self.gas < self.gas_limit:
            self.gas += 0.1

        if self.grenades_enabled:
            self.grenades_limit = 10 + int((self.score - 100) / 10)
            if self.grenades < self.grenades_limit and self.screen.renders % 30 == 0:
                self.grenades += 1

        if self.score > 50 and not self.machine_gun_enabled:
            self.machine_gun_enabled = True
            self.using_machine_gun = True
            screen.add(Monologue(self.x, self.y - 1, ['New weapon unlocked: MACHINE GUN!!',
                                                      'It shoots and moves twice as fast,',
                                                      'but watch out as ammos are limited.',
                                                      'Press up/down to switch your weapon']))
            self.ammos = self.ammos_limit

        if self.score > 100 and not self.grenades_enabled:
            self.grenades_enabled = True
            screen.add(Monologue(self.x, self.y - 1, ['New weapon unlocked: GRENADES!!',
                                                      'You got {} of them.'.format(self.grenades_limit),
                                                      'It EXPLODES on impact.',
                                                      'Press Space to launch a grenade']))
            self.grenades = self.grenades_limit

        if self.score > 150 and not self.flamethrower_enabled:
            self.flamethrower_enabled = True
            self.using_flamethrower = True
            self.using_machine_gun = False
            screen.add(Monologue(self.x, self.y - 1, ['New weapon unlocked: FLAMETHROWER!!',
                                                      'Destroy everything before the gas runs out!',
                                                      'Press up/down to switch your weapon']))
            self.gas = self.gas_limit

        if self.machine_gun_enabled:
            screen.border.status['Ammos'] = self.ammos
        if self.grenades_enabled:
            screen.border.status['Grenades'] = self.grenades
            if self.alive:
                if self.grenades:
                    self.color = screen.COLOR_RAINBOW
                else:
                    self.color = None
        if self.flamethrower_enabled:
            screen.border.status['Gas'] = '{}%'.format(int(self.gas))

    def destruct(self):
        super().destruct(msg='You got ZOMBIFIED!!', explosion_size=30)
        self.screen.add(Zombie(self.shape.x, self.shape.y, color=self.screen.COLOR_GREEN, y_delta=-0.1))

    def left_pressed(self):
        if self.alive:
            if self.delta_index > 0:
                self.delta_index -= 1
            else:
                self.delta_index = len(self.deltas) - 1

    def right_pressed(self):
        if self.alive:
            if self.delta_index < len(self.deltas) - 1:
                self.delta_index += 1
            else:
                self.delta_index = 0

    def up_pressed(self):
        if self.using_machine_gun and self.flamethrower_enabled:
            self.using_flamethrower = True
            self.using_machine_gun = False
        elif self.machine_gun_enabled:
            self.using_machine_gun = True

    def down_pressed(self):
        if self.using_flamethrower:
            self.using_flamethrower = False
            self.using_machine_gun = True
        else:
            self.using_machine_gun = False

    def space_pressed(self):
        if self.grenades_enabled and self.grenades > 0 and self.alive:
            self.grenades -= 1
            x_delta, y_delta, shape = self.deltas[self.delta_index]
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
