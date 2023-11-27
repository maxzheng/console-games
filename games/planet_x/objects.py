from random import randint, random, choice

from games.screen import Screen
from games.listeners import KeyListener
from games.objects import (Bitmap, Monologue, AbstractPlayer, AbstractEnemies, Landscape, Circle,
                           VolcanoErupting, JellyFish, Cube, Spinner, Line3D)


class Player(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        self.gas_limit = 100

        super().__init__(*args, score_title='Level', max_hp=100, **kwargs)

    def reset(self):
        super().reset()

        self.gas = self.gas_limit

    def render(self, screen: Screen):
        super().render(screen)

        if self.active:
            screen.border.set_levels(self.hp / self.max_hp, self.gas / self.gas_limit)

            if self.is_hit:
                self.color = 'rainbow'
                self.is_hit = False
            else:
                self.color = 'red'

            if self.gas > 0:
                self.gas -= 0.025
            elif self.gas != -1:
                screen.add(Monologue(self.x, self.y - 2, on_finish=self.destruct,
                                     texts=['Out of gas!!!',
                                            'Better fly faster next time!']))
                self.gas = -1
                self.y_delta = 0.1
                self.active = False

    def left_pressed(self):
        self.shape.flip = False

        if self.active:
            if self.can_move_x(x_delta=-1):
                self.x -= 1

    def right_pressed(self):
        self.shape.flip = True

        if self.active:
            if self.can_move_x(x_delta=1):
                self.x += 1

    def up_pressed(self):
        if self.active:
            if self.can_move_y(y_delta=-1):
                self.y -= 1

    def down_pressed(self):
        if self.active:
            if self.can_move_y(y_delta=1):
                self.y += 1

    def destruct(self, *args, **kwargs):
        super().destruct(*args, **kwargs, on_finish=self.controller.reset)


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
   RVRR    VR  V  R   R    RVR    VRV   RV   VR RVRR    VR  V  R   R    RVR    VRV   R  R   R   RV   VR
""" # noqa


class CrabClaw(Bitmap):
    color = 'red'
    bitmaps = (r"""
 ________
/        \
| \/     |
|  \ /   |
|   /\   |
|  /  \  /
\  |  / /
 \ \ /_/
  \_\
""",  # noqa
r"""
 ________
/        \
| \/     |
|  \ /   |
|   /\   |
|  /  \  /
\  |  | /
 \ |  |/
  \|
""")  # noqa


class CrabClawEnemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        x = randint(self.player.size, self.screen.width - 20)
        y = 0

        y_delta = random()

        return CrabClaw(x, y, y_delta=y_delta, random_start=True)


class AcidBubbleEnemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        x = randint(self.player.size, self.screen.width - 20)
        y = self.screen.height

        y_delta = -random()

        return Circle(x, y, y_delta=y_delta, color='green')


class VolcanoEnemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        x = randint(self.player.size, self.screen.width - 20)
        y = self.screen.height - 3
        y_delta = -random()
        size = randint(int(self.screen.height / 3), int(self.screen.height / 1.2))

        return VolcanoErupting(x, y, y_delta=y_delta, size=size)


class JellyFishEnemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        x = randint(self.player.size, self.screen.width - 20)
        y = choice([3, self.screen.height - 3])
        y_delta = random() if y == 3 else -random()

        return JellyFish(x, y, y_delta=y_delta)


class CubeEnemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        x = randint(self.player.size, self.screen.width - 20)
        y = choice([3, self.screen.height - 3])
        y_delta = random() if y == 3 else -random()

        cube = Cube(x, y, y_delta=y_delta, size=5, color='rainbow', random_start=True,
                    random_movement=True)
        cube.connect_points = False
        return cube


class SpinnerEnemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        x = randint(self.player.size, self.screen.width - 20)
        y = choice([3, self.screen.height - 3])
        y_delta = random() if y == 3 else -random()

        return Spinner(x, y, y_delta=y_delta, player=self.player, explode_on_impact=True)


class X(Line3D):
    color = 'green'
    rotate_axes = (0, 0, 1, 2)
    points = [
        # X
        (-1, -1, 0),
        (1, 1, 0),
        (0, 0, 0),
        (-1, 1, 0),
        (1, -1, 0)
    ]

    def render(self, screen: Screen):
        super().render(screen)

        if abs(screen.height / 2 - self.y) <= 0.5:
            self.y_delta = 0


class XEnemies(AbstractEnemies, KeyListener):
    def create_enemy(self):
        existing_x_points = set((p.x, p.theta_factor) for p in self.kids)
        thetas = [0.75, -0.75]
        x_points = set(((i + 1) * self.size * 2, thetas[i % 2]) for i in range(self.max_enemies))
        x_point = choice(list(x_points - existing_x_points or x_points))
        x, theta_factor = x_point
        y = choice([3, self.screen.height - 3])
        y_delta = 1 if y == 3 else -1

        return X(x, y, y_delta=y_delta, player=self.player, magnify_by_size=True,
                 size=self.size, rotate_axes=(0, 0, 1, theta_factor))
