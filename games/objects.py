from random import randint, random
from time import time

from games.screen import Screen


class ScreenObject:
    """ Base class for all objects on screen """
    def __init__(self, x: int, y: int, color=None, size=1, parent=None):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.coords = set()
        self.parent = parent
        self.kids = set()
        self.is_visible = True

    @property
    def is_out(self):
        """ Indicates if the projectile center is outside of the screen border """
        try:
            return (self.x + self.size < 0 or self.x - self.size > self.screen.width
                    or self.y + self.size < 0 or self.y - self.size > self.screen.height)

        except Exception:
            return False

    def render(self, screen: Screen):
        """ Render object onto the given screen """
        self.screen = screen


class Text(ScreenObject):
    def __init__(self, x: int, y: int, text: str):
        super().__init__(x, y)
        self.text = text

    def render(self, screen: Screen):
        for offset, char in enumerate(self.text):
            screen.draw(self.x + offset, self.y, char, color=self.color)


class BouncyText(Text):
    def __init__(self, x: int, y: int, text: str, x_delta=1, y_delta=1):
        super().__init__(x, y, text)
        self.x_delta = x_delta
        self.y_delta = y_delta

    def render(self, screen: Screen):
        self.x += self.x_delta
        self.y += self.y_delta
        if self.x + len(self.text) >= screen.width - 1 or self.x == 1:
            self.x_delta = -self.x_delta
        if self.y >= screen.height - 1 or self.y == 1:
            self.y_delta = -self.y_delta

        super().render(screen)


class Border(ScreenObject):
    def __init__(self, char: str, show_fps=False, title=None):
        super().__init__(0, 0)
        self.char = char
        self.show_fps = show_fps
        self.title = title
        self.status = {}

        self._renders = 0
        self._start_time = time()

    def render(self, screen: Screen):
        for x in range(screen.width):
            for y in range(screen.height):
                if x == 0 or y == 0 or x == screen.width - 1 or y == screen.height - 1:
                    screen.draw(x, y, self.char, color=self.color)

        if self.title:
            padded_title = ' ' + self.title + ' '
            start_x = round((screen.width - len(padded_title)) / 2)
            for x_offset in range(len(padded_title)):
                screen.draw(start_x + x_offset, 0, padded_title[x_offset], color=self.color)

        if self.show_fps:
            self._renders += 1
            fps = round(self._renders / (time() - self._start_time))
            self.status['FPS'] = fps

        if self.status:
            debug_text = ' ' + ' | '.join(
                ['{}: {}'.format(k[0].upper() + k[1:], v) for k, v in self.status.items()]) + ' '
            start_x = round((screen.width - len(debug_text)) / 2)
            for x_offset in range(len(debug_text)):
                screen.draw(start_x + x_offset, screen.height - 1, debug_text[x_offset], color=self.color)


class Projectile(ScreenObject):
    def __init__(self, x: int, y: int, shape='^', x_delta=0, y_delta=-1, color=None, size=1,
                 parent=None):
        super().__init__(x, y, color=color, size=size)
        self.shape = shape
        self.x_delta = x_delta
        self.y_delta = y_delta
        self.parent = parent

    def render(self, screen: Screen):
        super().render(screen)

        self.x += self.x_delta
        self.y += self.y_delta

        self.coords = {(int(self.x), int(self.y))}

        if not self.is_out and self.shape is not None:
            screen.draw(self.x, self.y, self.shape,
                        color=self.color or screen.colors[randint(0, len(screen.colors)-1)])


class Circle(Projectile):
    def __init__(self, x: int, y: int, size=3, char='O', x_delta=0, y_delta=0, color=None):
        super().__init__(x, y, shape=None, x_delta=x_delta, y_delta=y_delta, color=color,
                         size=size)
        self.char = char

    def render(self, screen: Screen):
        super().render(screen)

        self.coords = {(int(self.x + 1), int(self.y)), (int(self.x - 1), int(self.y)),
                       (int(self.x), int(self.y + 1)), (int(self.x), int(self.y - 1))}

        for x, y in self.coords:
            screen.draw(x, y, self.char, color=self.color)


class Square(Projectile):
    def __init__(self, x: int, y: int, size=3, char='#', x_delta=0, y_delta=0, color=None):
        super().__init__(x, y, shape=None, x_delta=x_delta, y_delta=y_delta, color=color,
                         size=size)

        self.char = char

    def render(self, screen: Screen):
        super().render(screen)

        start_x = int(self.x - self.size / 2)
        start_y = int(self.y - self.size / 2)
        self.coords = set()

        for x in range(start_x, start_x + self.size):
            for y in range(start_y, start_y + self.size):
                if (x == start_x or x == start_x + self.size - 1
                        or y == start_y or y == start_y + self.size - 1):
                    self.coords.add((int(x), int(y)))
                    screen.draw(x, y, self.char, color=self.color)


class Explosion(ScreenObject):
    def __init__(self, x: int, y: int, size=10, char='*', color=None, on_finish=None):
        super().__init__(x, y, color=color, size=size)

        self.current_size = 2
        self.char = char
        self.on_finish = on_finish

    def render(self, screen: Screen):
        super().render(screen)

        start_x = int(self.x - self.current_size / 2)
        start_y = int(self.y - self.current_size / 2)
        self.coords = set()
        colors = [screen.COLOR_YELLOW, screen.COLOR_RED]

        for x in range(start_x, start_x + self.current_size):
            for y in range(start_y, start_y + self.current_size):
                if (x == start_x or x == start_x + self.current_size - 1
                        or y == start_y or y == start_y + self.current_size - 1):
                    self.coords.add((int(x), int(y)))
                    distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** (1/2)
                    if distance < self.current_size and random() < 2/self.current_size:
                        screen.draw(x, y, self.char, color=colors[randint(0, len(colors) - 1)])

        self.current_size += 1
        if self.current_size > self.size:
            screen.remove(self)
            if self.on_finish:
                self.on_finish()
