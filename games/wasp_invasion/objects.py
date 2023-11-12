from random import randint, random, choice

from games.screen import Screen
from games.listeners import KeyListener
from games.objects import (Wasp, Explosion, Projectile, Monologue,
                           Stickman, AbstractPlayer, AbstractEnemies, CompassionateBoss,
                           WaspKaiju, DyingWaspKaiju, Char, Landscape)


class Player(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        self.gas_limit = 100
        self.left_deltas = (-2, 0, '⇚')
        self.upleft_deltas = (-2, -1, '⇖')
        self.right_deltas = (2, 0, '⇛')
        self.upright_deltas = (2, -1, '⇗')
        self.projectile_deltas = self.right_deltas

        super().__init__(*args, score_title='Killed', max_hp=100, **kwargs)

    def reset(self):
        super().reset()
        self.sync(self.shape)

        self.gas = self.gas_limit
        self.flame_on = True

        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height - 2

        self.flamethrower = Char(self.x, self.y, char=None)

    def render(self, screen: Screen):
        super().render(screen)

        if self.active:
            screen.border.set_levels(self.hp / self.max_hp, self.gas / self.gas_limit)

            if self.is_hit:
                self.color = screen.COLOR_YELLOW
                self.is_hit = False
            else:
                self.color = None

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

            x_delta, y_delta, char = self.projectile_deltas
            self.flamethrower.x = self.x + x_delta - 0.5
            self.flamethrower.y = self.y + y_delta - 0.5

            if self.flame_on:
                self.flamethrower.char = char
                self.flamethrower.color = choice([screen.COLOR_RED, screen.COLOR_YELLOW])

                if self.flamethrower not in screen:
                    screen.add(self.flamethrower)

                if self.gas > 0:
                    for flame_size in range(min(15, int(screen.width / 9))):
                        explosion = Explosion(self.x, self.y, size=flame_size, parent=self)
                        projectile = Projectile(self.x, self.y, shape=None, parent=self,
                                                x_delta=x_delta * (1 + flame_size / 20),
                                                y_delta=y_delta, color=screen.COLOR_YELLOW,
                                                explode_after_renders=flame_size,
                                                explosion=explosion)
                        self.kids.add(projectile)
                        self.screen.add(projectile)

                if self.gas > 0:
                    self.gas -= 0.01
                elif self.gas != -1:
                    screen.add(Monologue(self.x, self.y - 2, texts=['Out of gas!!!',
                                                                    'Look for green gas refills']))
                    self.gas = -1
            else:
                self.flamethrower.char = '⇓'
                self.flamethrower.color = None
                self.flamethrower.y = self.y + 0.5

    def destruct(self):
        super().destruct(msg='You got STUNG!!', explosion_size=30)
        self.screen.add(Stickman(self.shape.x, self.shape.y, color=self.screen.COLOR_YELLOW, y_delta=-0.1))

    def left_pressed(self):
        if self.alive:
            if self.projectile_deltas in (self.upright_deltas, self.upleft_deltas):
                self.projectile_deltas = self.upleft_deltas
            else:
                self.projectile_deltas = self.left_deltas

    def right_pressed(self):
        if self.alive:
            if self.projectile_deltas in (self.upleft_deltas, self.upright_deltas):
                self.projectile_deltas = self.upright_deltas
            else:
                self.projectile_deltas = self.right_deltas

    def up_pressed(self):
        if self.alive:
            if not self.flame_on:
                self.flame_on = True
            elif self.projectile_deltas == self.right_deltas:
                self.projectile_deltas = self.upright_deltas
            elif self.projectile_deltas == self.left_deltas:
                self.projectile_deltas = self.upleft_deltas
            elif not self.y_delta or not self.can_move_y():
                self.y_delta = -1

    def down_pressed(self):
        if self.alive and self.y_delta and self.y_delta < 0:
            self.y_delta *= -1

        if self.projectile_deltas in (self.left_deltas, self.right_deltas):
            self.flame_on = False
        elif self.projectile_deltas == self.upleft_deltas:
            self.projectile_deltas = self.left_deltas
        else:
            self.projectile_deltas = self.right_deltas

    def space_pressed(self):
        if self.alive:
            if not self.y_delta or not self.can_move_y():
                self.y_delta = -1


class Enemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        if random() < 0.5:
            x = choice([0, self.screen.width])
            y = randint(0, self.screen.height)
        else:
            y = 0
            x = randint(0, self.screen.width)

        distance_score = abs(self.player.obstacles.x - self.player.x) / 2
        speed = min(2, random() * (self.player.score + distance_score) / 100 + 0.2)
        x_sign = (1 if x < self.player.x else -1) * random()
        y_sign = (1 if y < self.player.y else -1) * random()

        return Wasp(x, y, x_delta=x_sign * speed, y_delta=y_sign * speed, random_start=True,
                    flip=x_sign > 0, color=self.screen.COLOR_YELLOW)

    def on_death(self, enemy):
        enemy_class = DyingWaspKaiju if isinstance(enemy, CompassionateBoss) else enemy.__class__
        wasp = enemy_class(enemy.x, enemy.y, color=self.screen.COLOR_RED, remove_after_animation=True,
                           flip=getattr(enemy, 'flip', False))
        self.screen.add(wasp)

    def should_spawn_boss(self):
        return self.player.score and self.player.score % 50 == 0

    def additional_enemies(self):
        return super().additional_enemies() + abs((self.player.obstacles.x - self.player.x) / 50)

    def create_boss(self):
        if random() < 0.5:
            x_delta = -0.1
            x = self.screen.width
        else:
            x_delta = 0.1
            x = 0

        return CompassionateBoss('Kaiju',
                                 WaspKaiju(x, self.screen.height - 10,
                                           x_delta=x_delta, y_delta=0.01,
                                           color=self.screen.COLOR_YELLOW, random_start=True),
                                 self.player,
                                 hp=self.player.score)

    def left_pressed(self):
        if self.player.can_move_x(x_delta=-1):
            for enemy in self.enemies:
                enemy.x += 1

    def right_pressed(self):
        if self.player.can_move_x(x_delta=1):
            for enemy in self.enemies:
                enemy.x -= 1


class Landscape1(Landscape):
    move_speed = 0.1
    bitmap = """
   T    T           T        T       T      T           T              T   T            T      T   T
"""  # noqa


class Landscape2(Landscape):
    move_speed = 0.2
    bitmap = """
TT       T     T    T     T     T  T    T         T   T     T   TT   T   T T TTT   T    T    T     T TT
"""  # noqa


class Obstacles(Landscape):
    move_speed = 1
    bitmap = """
  RR  R    RVR    R VV      R    VVV    RRR    R  R    R    R    RVR    VRV   R  R   R   RV   VR
"""  # noqa
