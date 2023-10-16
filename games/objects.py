from time import time

from games.screen import Screen


class ScreenObject:
    """ Base class for all objects on screen """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def render(self, screen: Screen):
        """ Render object onto the given screen """
        raise NotImplementedError


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
    def __init__(self, char: str, show_fps=False):
        super().__init__(0, 0)
        self.char = char
        self.show_fps = show_fps

        self._renders = 0
        self._start_time = time()

    def render(self, screen: Screen):
        for x in range(screen.width):
            for y in range(screen.height):
                if x == 0 or y == 0 or x == screen.width - 1 or y == screen.height - 1:
                    screen.draw(x, y, self.char)

        if self.show_fps:
            self._renders += 1
            fps = round(self._renders / (time() - self._start_time))
            fps_text = ' FPS: {} '.format(fps)
            start_x = round((screen.width - len(fps_text)) / 2)
            for x_offset in range(len(fps_text)):
                screen.draw(start_x + x_offset, screen.height - 1, fps_text[x_offset])
