from random import randint, random

from games.screen import Screen
from games.listeners import KeyListener
from games.objects import (Bitmap, Monologue, AbstractPlayer, AbstractEnemies, Landscape, Circle)


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
                self.gas -= 0.01
            elif self.gas != -1:
                screen.add(Monologue(self.x, self.y - 2, on_finish=self.destruct,
                                     texts=['Out of gas!!!',
                                            'Better fly faster next time!']))
                self.gas = -1
                self.y_delta = 0.1
                self.active = False

    def left_pressed(self):
        if self.active:
            self.shape.flip = False

            if self.can_move_x(x_delta=-1):
                self.x -= 1

    def right_pressed(self):
        if self.active:
            self.shape.flip = True

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


class CrabClaw(Bitmap):
    color = 'red'
    bitmaps = (r"""
__________
|        |
| \/     |
|  \ /   |
|   /\   |
|  /  \  /
\  |  / /
 \ \ /_/
  \_\
""",  # noqa
r"""
__________
|        |
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
   RVRR    VR  V  R   R    RVR    VRV   R  R   R   RV   VR
""" # noqa
