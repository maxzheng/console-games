import curses
from time import sleep, time


class Screen:
    def __init__(self, border=None, fps=30, debug=False):
        #: FPS limit to render
        self.fps = fps

        #: Width of the screen
        self._width = None

        #: Height of the screen
        self._height = None

        #: Add border around the frame
        self.border = border

        #: Buffer for next frame to display
        self.buffer = None

        #: List of objets on the screen
        self.objects = []

        #: Number of times the screen has rendered
        self.renders = 0

        #: Show debug info
        self.debug = debug

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def key(self):
        return self._screen.getch()

    def __enter__(self):
        self._screen = curses.initscr()
        self._screen.keypad(True)
        self._screen.nodelay(True)

        self.resize_screen()

        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        self.COLOR_RED = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.COLOR_GREEN = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.COLOR_BLUE = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.COLOR_YELLOW = curses.color_pair(4)
        self.colors = [self.COLOR_RED, self.COLOR_GREEN, self.COLOR_BLUE, self.COLOR_YELLOW]

        return self._screen

    def __exit__(self, *args):
        self._screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def _new_frame(self):
        """ Return a new blank frame """
        frame = []
        if self._width and self._height:
            for r in range(self._height):
                frame.append([' '] * (self._width))
        return frame

    def resize_screen(self):
        max_height, max_width = self._screen.getmaxyx()
        self._height = max_height - 1
        self._width = max_width - 1
        self.buffer = curses.newpad(self.height + 1, self.width + 1)

    def draw(self, x: int, y: int, char: str, color=None):
        """ Draw character on the given position """
        if x >= 0 and x < self._width and y >= 0 and y < self._height:
            if color:
                self.buffer.addstr(int(y), int(x), char, color)
            else:
                self.buffer.addstr(int(y), int(x), char)

    def add(self, *screen_object):
        """ Add object to be rendered on the screen """
        self.objects.extend(screen_object)

    def remove(self, screen_object):
        """ Remove object from the screen """
        try:
            index = self.objects.index(screen_object)
        except ValueError:
            return

        self.objects.pop(index)

    def render(self):
        start_time = time()

        self._render()

        render_time = time() - start_time
        if render_time < 1/self.fps:
            sleep(1/self.fps - render_time)

    def _render(self):
        self.renders += 1

        self.buffer.clear()

        for obj in self.objects:
            if obj.is_visible:
                obj.render(self)
            if obj.is_out:
                if obj.parent:
                    obj.parent.kids.remove(obj)
                self.remove(obj)

        if self.border:
            if self.debug:
                self.border.status['objects'] = len(self.objects)
            self.border.render(self)

        try:
            self.buffer.refresh(0, 0, 0, 0, self.height, self.width)
        except Exception:
            self.resize_screen()

    def reset(self):
        self.objects = []
