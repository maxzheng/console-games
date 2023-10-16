import curses


class Screen:
    def __init__(self, width=None, height=None, border=None):
        #: Width of the screen
        self._width = width

        #: Height of the screen
        self._height = height

        #: Add border around the frame
        self.border = border

        #: The next frame to be rendered
        self.next_frame = self._new_frame()

        #: The current frame displayed to the user
        self.current_frame = self._new_frame()

        #: List of objets on the screen
        self.objects = []

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def __enter__(self):
        self.screen = curses.initscr()
        self.screen.keypad(True)

        max_height, max_width = self.screen.getmaxyx()
        if not self._height or self._height >= max_height:
            self._height = max_height - 1
        if not self._width or self._width >= max_width:
            self._width = max_width - 1

        curses.noecho()
        curses.cbreak()

        return self.screen

    def __exit__(self, *args):
        self.screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def _new_frame(self):
        """ Return a new blank frame """
        frame = []
        if self._width and self._height:
            for r in range(self._height):
                frame.append([' '] * self._width)
        return frame

    def draw(self, x: int, y: int, char: str):
        """ Draw character on the given position """
        if x >= 0 and x < self._width and y >= 0 and y < self._height:
            self.next_frame[y][x] = char

    def add(self, screen_object):
        """ Add object to be rendered on the screen """
        self.objects.append(screen_object)

    def remove(self, screen_object):
        """ Remove object from the screen """
        try:
            index = self.objects.index(screen_object)
        except ValueError:
            return

        self.objects.pop(index)

    def render(self):
        self.next_frame = self._new_frame()
        if not self.current_frame:
            self.current_frame = self._new_frame()

        for obj in self.objects:
            obj.render(self)
        if self.border:
            self.border.render(self)

        for x in range(self._width):
            for y in range(self._height):
                if self.next_frame[y][x] != self.current_frame[y][x]:
                    self.screen.addstr(y, x, self.next_frame[y][x])
                    self.current_frame[y][x] = self.next_frame[y][x]

        self.screen.refresh()

