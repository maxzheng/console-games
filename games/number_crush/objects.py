from random import randint, choice

from games.screen import Screen
from games.objects import (ScreenObject, KeyListener, Explosion, Text, ScreenObjectGroup, Bitmap,
                           One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Zero,
                           Plus, Minus, Multiply, Divide, Space, Stickman, StickmanScared,
                           StickmanWorried, AbstractPlayer)


class Player(AbstractPlayer):
    def __init__(self, controller):
        super().__init__('Jon', Stickman(int(controller.screen.width / 2), controller.screen.height - 3),
                         controller, score_title='Crushed', show_total=True)

    def react(self, formula: ScreenObject):
        distance = self.y - formula.y
        if distance < 10:
            self.scared()
        elif distance < 15:
            self.worried()
        else:
            self.smile()

    def scared(self):
        self.shape = StickmanScared(self.x, self.y)

    def worried(self):
        self.shape = StickmanWorried(self.x, self.y)

    def smile(self):
        self.shape = Stickman(self.x, self.y)


class Formula(ScreenObjectGroup):
    BITMAPS = dict((b.represents, b) for b in [Zero, One, Two, Three, Four, Five, Six, Seven, Eight,
                                               Nine, Plus, Minus, Multiply, Divide, Space])

    def __init__(self, *args, text, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        for char in text:
            self.add(self.BITMAPS[char](self.x, self.y))


class Numbers(ScreenObject, KeyListener):
    def __init__(self, x, y, player: Player):
        super().__init__(x, y)
        self.player = player
        self.a = None
        self.b = None
        self.formula = None
        self.operand_ranges = {
            '-': (0, 99),  # Keep it 2 digits for better fit on small screens
            '+': (0, 99),
            '/': (0, 10),
            '*': (0, 10)
        }
        self.next()
        self.last_answer = None

    def render(self, screen: Screen):
        super().render(screen)

        if self.ready_for_next:
            # Set operand and numbers
            self.operand = choice(list(self.operand_ranges))
            min_value, max_value = self.operand_ranges[self.operand]
            self.a = randint(min_value, max_value)
            self.b = randint(min_value, max_value)

            if self.operand == '-' and (self.a - self.b) < 0:
                self.a, self.b = self.b, self.a

            if self.operand == '/' and self.b == 0:
                self.b = 1

            if self.operand == '/':
                self.a = self.a * self.b

            # Set text and display
            formula = '{} {} {}'.format(self.a, self.operand, self.b)
            self.formula = Formula(self.x, 5, text=formula, y_delta=0.1, add_bar=True)
            self.kids.add(self.formula)
            screen.add(self.formula)

            self.ready_for_next = False

        self.player.react(self.formula)

        if self.all_coords & self.player.coords:
            self.player.destruct(msg='You got CRUSHED!!')
        else:
            answer = int(eval(self.formula.text))
            for answer_text in list(self.player.kids):
                if answer_text.y <= self.formula.y + 5:
                    self.player.kids.remove(answer_text)
                    self.screen.remove(answer_text)

                    player_answer = int(answer_text.text)
                    if player_answer == answer and self.formula in self.screen:
                        self.kids.remove(self.formula)
                        self.screen.remove(self.formula)
                        for i, kid in enumerate(self.formula.kids):
                            if isinstance(kid, Bitmap):
                                self.screen.add(Explosion(kid.x, kid.y, size=kid.size * 2, on_finish=self.next))

                        self.player.scored()

    def number_pressed(self, number):
        if self.kids and self.player.alive:
            self.numbers_pressed.append(number)
            answer = int(eval(self.formula.text))
            player_answer = eval(''.join([str(n) for n in self.numbers_pressed[-len(str(answer)):]]).lstrip('0') or '0')

            if self.last_answer != player_answer and len(str(player_answer)) == len(str(answer)):
                answer = Text(self.player.x, self.player.y - 2, str(player_answer), y_delta=-1,
                              centered=True)
                self.screen.add(answer)
                self.player.kids.add(answer)
            self.last_answer = player_answer

    def next(self):
        if not self.kids:
            self.ready_for_next = True
            self.numbers_pressed = []
            self.last_answer = None
