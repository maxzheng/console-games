from random import randint, choice

from games.screen import Screen
from games.objects import ScreenObject, KeyListener, Explosion, Text


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
            self.x = self.screen.width / 2
            self.y = self.screen.height - self.size

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

        self.screen.add(Text((self.screen.width - 10) / 2, self.screen.height / 2, 'You got CRUSHED!!'))
        self.screen.add(Explosion(self.x, self.y, size=20,
                                  on_finish=self.controller.reset_scene))


class Numbers(ScreenObject, KeyListener):
    def __init__(self, x, y, player: Player = None):
        super().__init__(x, y)
        self.player = player
        self.a = None
        self.b = None
        self.numbers_text = None
        self.operand_ranges = {
            '-': (0, 100),
            '+': (0, 100),
            '/': (0, 10),
            '*': (0, 10)
        }
        self.next()

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
            self.numbers_text = Text(self.x - len(formula) / 2 + 1, 0, formula, y_delta=0.1)
            self.kids.add(self.numbers_text)
            screen.add(self.numbers_text)

            self.ready_for_next = False

        if self.all_coords & self.player.coords:
            self.player.got_crushed()

    def number_pressed(self, number):
        if self.kids:
            self.numbers_pressed.append(number)
            answer = int(eval(self.numbers_text.text))
            player_answer = eval(''.join([str(n) for n in self.numbers_pressed[-len(str(answer)):]]).lstrip('0') or '0')
            if player_answer == answer:
                self.kids.remove(self.numbers_text)
                self.screen.remove(self.numbers_text)
                self.screen.add(Explosion(self.numbers_text.x + len(self.numbers_text.text) / 2,
                                          self.numbers_text.y, size=15, on_finish=self.next))

                self.player.score += 1
                self.player.total_score += 1
                if self.player.score > self.player.high_score:
                    self.player.high_score = self.player.score

    def next(self):
        self.ready_for_next = True
        self.numbers_pressed = []
