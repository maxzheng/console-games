from random import randint, random, choice

from games.screen import Screen
from games.listeners import KeyListener
from games.objects import (Wasp, Monologue,
                           Stickman, AbstractPlayer, AbstractEnemies, CompassionateBoss,
                           WaspKaiju, DyingWaspKaiju, Char, Landscape, StickmanScared,
                           StickmanWorried, StickmanCelebrate, Flame)


class Player(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        self.gas_limit = 100
        self.left_deltas = (-2, 0, '⇚')
        self.upleft_deltas = (-2, -1, '⇖')
        self.right_deltas = (2, 0, '⇛')
        self.upright_deltas = (2, -1, '⇗')
        self.projectile_deltas = self.right_deltas
        self.scared = StickmanScared(0, 0)
        self.worried = StickmanWorried(0, 0)
        self.celebrate = StickmanCelebrate(0, 0)
        self.kaijus_killed_high = 0

        super().__init__(*args, score_title='Killed', max_hp=100, **kwargs)

    def reset(self):
        super().reset()
        self.sync(self.shape)

        self.gas = self.gas_limit
        self.flame_on = True
        self.kaijus_killed = 0

        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height - 3
            self.screen.status.pop('Kaijus', None)

        self.flamethrower = Char(self.x, self.y, char=None)

    def killed_boss(self):
        super().killed_boss()
        self.kaijus_killed += 1
        if self.kaijus_killed > self.kaijus_killed_high:
            self.kaijus_killed_high = self.kaijus_killed
        self.screen.status['Kaijus'] = self.kaijus_killed

    def render(self, screen: Screen):
        super().render(screen)

        if self.kaijus_killed < self.kaijus_killed_high:
            self.screen.status[self.score_title] += ' ({} K)'.format(self.kaijus_killed_high)

        if self.active:
            screen.border.set_levels(self.hp / self.max_hp, self.gas / self.gas_limit)

            if self.kaijus_killed:
                if self.kaijus_killed >= 10 and self.shape != self.celebrate:
                    self.color = None
                    self.y_delta = 0
                    self.x_delta = 0
                    self.celebrate.sync(self)
                    self.shape = self.celebrate
                    self.active = False
                    screen.add(Monologue(self.x, self.y - 5, texts=['CONGRATS!',
                                                                    'YOU DEFEATED ALL THE KAIJUS!!!',
                                                                    'And saved humanity all thanks to',
                                                                    'to having your trusty flamethrower',
                                                                    'with you today.',
                                                                    'Never leave home without it! ;)',
                                                                    'THE END',
                                                                    'Press Space to play again '
                                                                    'or Esc to exit.'
                                                                    ],
                                         ))

            if self.is_hit:
                self.color = screen.COLOR_YELLOW
                self.scared.sync(self)
                self.worried.sync(self)
                self.shape = choice([self.scared, self.worried])
                self.is_hit = False
            elif self.shape not in (self._original_shape, self.celebrate):
                self.color = None
                self._original_shape.sync(self)
                self.shape = self._original_shape

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

                    if self.y >= self.screen.height - 3:
                        self.y_delta = 0

            x_delta, y_delta, char = self.projectile_deltas
            self.flamethrower.x = self.x + x_delta
            self.flamethrower.y = self.y + y_delta

            if self.flame_on:
                self.flamethrower.char = char
                self.flamethrower.color = choice([screen.COLOR_RED, screen.COLOR_YELLOW])

                if self.flamethrower not in screen:
                    screen.add(self.flamethrower)

                if self.gas > 0:
                    size = min(15, int(screen.width / 9))
                    flame = Flame(self.x, self.y, x_delta=x_delta, y_delta=y_delta, size=size,
                                  parent=self)
                    self.add_kid(flame)
                    self.screen.add(flame)

                if self.gas > 0:
                    self.gas -= 0.01
                elif self.gas != -1:
                    screen.add(Monologue(self.x, self.y - 2, texts=['Out of gas!!!',
                                                                    'Better not be wasteful in next life']))
                    self.gas = -1
            else:
                self.flamethrower.char = '⇓'
                self.flamethrower.color = None
                self.flamethrower.y = self.y + 0.5

    def destruct(self):
        super().destruct(msg='You got STUNG to death!!', explosion_size=30)
        self.screen.add(Stickman(self.shape.x, self.shape.y, color=self.screen.COLOR_YELLOW, y_delta=-0.1))

    def left_pressed(self):
        if self.active:
            if self.projectile_deltas in (self.upright_deltas, self.upleft_deltas):
                self.projectile_deltas = self.upleft_deltas
            else:
                self.projectile_deltas = self.left_deltas

    def right_pressed(self):
        if self.active:
            if self.projectile_deltas in (self.upleft_deltas, self.upright_deltas):
                self.projectile_deltas = self.upright_deltas
            else:
                self.projectile_deltas = self.right_deltas

    def up_pressed(self):
        if self.active:
            if not self.flame_on:
                self.flame_on = True
            elif self.projectile_deltas == self.right_deltas:
                self.projectile_deltas = self.upright_deltas
            elif self.projectile_deltas == self.left_deltas:
                self.projectile_deltas = self.upleft_deltas
            elif not self.y_delta or not self.can_move_y():
                self.y_delta = -1

    def down_pressed(self):
        if self.active and self.y_delta and self.y_delta < 0:
            self.y_delta *= -1

        if self.projectile_deltas in (self.left_deltas, self.right_deltas):
            self.flame_on = False
        elif self.projectile_deltas == self.upleft_deltas:
            self.projectile_deltas = self.left_deltas
        else:
            self.projectile_deltas = self.right_deltas

    def space_pressed(self):
        if self.active:
            if not self.y_delta or not self.can_move_y():
                self.y_delta = -1
        else:
            self.controller.current_scene.next()


class Enemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        if random() < 0.75:
            x = choice([0, self.screen.width])
            y = randint(0, self.screen.height)
        else:
            y = 0
            x = randint(0, self.screen.width)

        speed = min(2, random() * self.player.score / 420 + 0.2)
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
        return self.player.score % 42 == 0 and self.player.score

    def additional_enemies(self):
        return super().additional_enemies() + abs((self.player.obstacles.x - self.player.x) / 50)

    def create_boss(self):
        if getattr(self, 'last_move', None) == 'right':
            x_delta = -0.2
            x = self.screen.width
        else:
            x_delta = 0.2
            x = 0

        return CompassionateBoss('Kaiju',
                                 WaspKaiju(x, self.screen.height - 10,
                                           x_delta=x_delta, y_delta=0.01,
                                           color=self.screen.COLOR_YELLOW, random_start=True),
                                 self.player,
                                 hp=self.player.score)

    def left_pressed(self):
        if self.player.can_move_x(x_delta=-1):
            for enemy in self.kids:
                enemy.x += 1
            self.last_move = 'left'

    def right_pressed(self):
        if self.player.can_move_x(x_delta=1):
            for enemy in self.kids:
                enemy.x -= 1
            self.last_move = 'right'


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
    bitmap = """\
  RR  R    RVR    R VV      R    VVV    RRR    R  R    R    R    RVR    VRV   R  R   R   RV   VR\
""" * 2 # noqa
