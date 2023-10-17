from time import time

from games.screen import Screen


class ScreenObject:
    """ Base class for all objects on screen """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @property
    def is_out(self):
        """ Indicates if the projectile center is outside of the screen border """
        try:
            return (self.x < 0 or self.x > self.screen.width
                    or self.y < 0 or self.y > self.screen.height)

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
            screen.draw(self.x + offset, self.y, char)


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
        self.debug_info = {}

        self._renders = 0
        self._start_time = time()

    def render(self, screen: Screen):
        for x in range(screen.width):
            for y in range(screen.height):
                if x == 0 or y == 0 or x == screen.width - 1 or y == screen.height - 1:
                    screen.draw(x, y, self.char)

        if self.title:
            padded_title = ' ' + self.title + ' '
            start_x = round((screen.width - len(padded_title)) / 2)
            for x_offset in range(len(padded_title)):
                screen.draw(start_x + x_offset, 0, padded_title[x_offset])

        if self.show_fps:
            self._renders += 1
            fps = round(self._renders / (time() - self._start_time))
            self.debug_info['FPS'] = fps

        if self.debug_info:
            debug_text = ' ' + ' | '.join(
                ['{}: {}'.format(k, v) for k, v in self.debug_info.items()]) + ' '
            start_x = round((screen.width - len(debug_text)) / 2)
            for x_offset in range(len(debug_text)):
                screen.draw(start_x + x_offset, screen.height - 1, debug_text[x_offset])


class Square(ScreenObject):
    def __init__(self, x: int, y: int, size=1, char='#'):
        super().__init__(x, y)
        self.size = size
        self.char = char

    def render(self, screen: Screen):
        start_x = int(self.x - self.size / 2)
        start_y = int(self.y - self.size / 2)

        for x in range(start_x, start_x + self.size):
            for y in range(start_y, start_y + self.size):
                if (x == start_x or x == start_x + self.size - 1
                        or y == start_y or y == start_y + self.size - 1):
                    screen.draw(x, y, self.char)


class Projectile(ScreenObject):
    def __init__(self, x: int, y: int, shape='^', x_delta=0, y_delta=-1):
        super().__init__(x, y)
        self.shape = shape
        self.x_delta = x_delta
        self.y_delta = y_delta

    def render(self, screen: Screen):
        self.x += self.x_delta
        self.y += self.y_delta

        if not self.is_out:
            screen.draw(self.x, self.y, self.shape)

        super().render(screen)
