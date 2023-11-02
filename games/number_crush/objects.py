from random import randint, choice

from games.screen import Screen
from games.objects import (ScreenObject, KeyListener, Explosion, Text, ScreenObjectGroup, BITMAPS, Bitmap)  # noqa


class Player(ScreenObject, KeyListener):
    def __init__(self, name, shape: ScreenObject, controller: None):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color)

        self.name = name
        self.shape = shape
        self.high_score = 0
        self.total_score = 0
        self.is_playing = False
        self.char = shape.char
        self.controller = controller

        self.reset()

    @property
    def is_alive(self):
        return self.is_visible and self.is_playing

    def reset(self):
        self.score = 0
        self.is_visible = True
        self.size = 3
        if self.screen:
            self.x = int(self.screen.width / 2) + 1
            self.y = self.screen.height - 2

    def render(self, screen: Screen):
        super().render(screen)
        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        crushed = str(self.score)
        if self.score < self.high_score:
            crushed += ' | High: {}'.format(self.high_score)
        if self.score < self.total_score:
            crushed += ' | Total: {}'.format(self.total_score)

        self.screen.border.status['crushed'] = crushed

    def got_crushed(self):
        self.is_visible = False

        self.screen.add(Text((self.screen.width - 16) / 2, self.screen.height / 2, 'You got CRUSHED!!'))
        self.screen.add(Explosion(self.x, self.y, size=20,
                                  on_finish=self.controller.reset_scene))


class Formula(ScreenObjectGroup):
    def __init__(self, *args, text, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        for char in text:
            self.add(BITMAPS[char](self.x, self.y))


class Numbers(ScreenObject, KeyListener):
    def __init__(self, x, y, player: Player = None):
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

        if self.all_coords & self.player.coords:
            self.player.got_crushed()
        else:
            answer = int(eval(self.formula.text))
            for answer_text in list(self.player.kids):
                if answer_text.y <= self.formula.y + 5:
                    self.player.kids.remove(answer_text)
                    self.screen.remove(answer_text)

                    player_answer = int(answer_text.text)
                    if player_answer == answer:
                        self.kids.remove(self.formula)
                        self.screen.remove(self.formula)
                        for i, kid in enumerate(self.formula.kids):
                            if isinstance(kid, Bitmap):
                                self.screen.add(Explosion(kid.x, kid.y, size=kid.size * 2, on_finish=self.next))

                        self.player.score += 1
                        self.player.total_score += 1
                        if self.player.score > self.player.high_score:
                            self.player.high_score = self.player.score

    def number_pressed(self, number):
        if self.kids:
            self.numbers_pressed.append(number)
            answer = int(eval(self.formula.text))
            player_answer = eval(''.join([str(n) for n in self.numbers_pressed[-len(str(answer)):]]).lstrip('0') or '0')

            if self.last_answer != player_answer and len(str(player_answer)) == len(str(answer)):
                answer = Text(self.player.x - 1, self.player.y - 2, str(player_answer), y_delta=-1)
                self.screen.add(answer)
                self.player.kids.add(answer)
            self.last_answer = player_answer

    def next(self):
        if not self.kids:
            self.ready_for_next = True
            self.numbers_pressed = []
