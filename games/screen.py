from collections import deque
import curses
from random import choice
from time import sleep, time

from games.listeners import KeyListener


class Screen:
    #: Special rainbow color
    COLOR_RAINBOW = (-1,)

    def __init__(self, border=None, fps=30, debug=False):
        #: FPS limit to render
        self.fps_limit = fps

        #: Width of the screen
        self._width = None

        #: Height of the screen
        self._height = None

        #: Add border around the frame
        self.border = border

        #: Buffer for next frame to display
        self.buffer = None

        #: Number of times the screen has rendered
        self.renders = 0

        #: Tracks the last N render times
        self._render_secs = deque(maxlen=30)

        #: Show debug info
        self._debug = debug

        #: List of screen objects
        self._objects = []

        #: Game controller
        self.controller = None

        #: Curses screen object
        self._screen = None

        #: Map of color name to actual color pairs for Curses screen. Full set is populated in __enter__
        self.colors = {
            'white': None,
            'rainbow': self.COLOR_RAINBOW}
        self.rainbow_colors = []

        self.reset()

    def __contains__(self, screen_object):
        return screen_object in self._objects

    def __iter__(self):
        yield from self._objects

    def __len__(self):
        return len(self._objects)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def key(self):
        return self._screen.getch()

    @property
    def fps(self):
        if self._render_secs:
            return round(1 / (sum(self._render_secs) / len(self._render_secs)))

    @property
    def status(self):
        return self.border and self.border.status

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

        for color in ('RED', 'GREEN', 'BLUE', 'YELLOW', 'CYAN', 'MAGENTA'):
            color_name = 'COLOR_' + color
            color_id = getattr(curses, color_name)
            curses.init_pair(color_id, color_id, -1)
            setattr(self, color_name, curses.color_pair(color_id))
            self.colors[color.lower()] = getattr(self, color_name)
            self.rainbow_colors.append(getattr(self, color_name))

        return self

    def __exit__(self, *args):
        self._screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def add(self, *screen_objects):
        """ Add screen objects to the list """
        for obj in screen_objects:
            self._objects.append(obj)
            if isinstance(obj, KeyListener) and self.controller:
                self.controller.key_listeners.add(obj)

    def remove(self, *screen_objects):
        """ Remove screen objects from the list """
        for screen_object in screen_objects:
            try:
                index = self._objects.index(screen_object)
            except ValueError:
                continue

            if screen_object and self.controller and screen_object in self.controller.key_listeners:
                self.controller.key_listeners.remove(screen_object)

            obj = self._objects.pop(index)
            for kid in obj.kids:
                self.remove(kid)

    def replace(self, old_object, new_object):
        self.remove(old_object)
        self.add(new_object)

    def reset(self, border=False):
        self._objects = []
        self.renders = 0
        self._start_time = time()
        if self.border and border:
            self.border.reset()

    def resize_screen(self, when_changed=False):
        max_height, max_width = self._screen.getmaxyx()
        max_height -= 1  # Seems to be off by one

        if (not when_changed or max_width != self._width or max_height != self._height):
            self._height = max_height
            self._width = max_width
            self._screen.clear()
            self.buffer = ScreenBuffer(max_width, max_height)
            if self.controller:
                self.controller.reset_scene()

    def draw(self, x: int, y: int, char: str, color=None):
        """ Draw character on the given position """
        if x >= 0 and x < self._width and y >= 0 and y < self._height:
            if type(color) in (tuple, list) and isinstance(color[0], str):
                color = self.colors[choice(color)]
            if color in self.colors:
                color = self.colors[color]
            if color == self.COLOR_RAINBOW:
                color = choice(self.rainbow_colors)

            if isinstance(color, str):
                raise ValueError(('Invalid color name: {}\n'
                                  'Please choose from: {}').format(color, ', '.join(self.colors)))

            self.buffer.add(x, y, char, color)

    def render(self):
        start_time = time()

        self._render()

        render_time = time() - start_time
        # self.debug(secs_to_render_fps_limit=round(render_time * self.fps_limit, 1))

        # Sleep to ensure FPS doesn't exceed set limit
        sleep_time = 1 / self.fps_limit - render_time
        if sleep_time > 1 / self.fps_limit * 0.1:
            sleep(sleep_time)
            render_time += sleep_time

        self.renders += 1
        self._render_secs.append(render_time)

    def _render(self):
        if self.renders % self.fps_limit == 0:
            self.resize_screen(when_changed=True)

        self.buffer.clear()

        for obj in list(self):
            if obj.is_out:
                if obj.parent:
                    try:
                        obj.parent.kids.remove(obj)
                    except Exception:
                        pass
                self.remove(obj)
            elif obj.visible:
                obj.render(self)

        if self.border:
            if self._debug:
                self.border.status['objects'] = len(self)
            self.border.render(self)

        try:
            self.buffer.render(self._screen, self)
        except Exception:
            if self._debug:
                raise
            self.resize_screen()

    def debug(self, **debug_info):
        """ Show debug info (enabled when --debug flag is used) or start debugger """
        if debug_info:
            if self._debug:
                self.border.status.update(debug_info)
        else:
            self.__exit__()
            import pdb
            pdb.set_trace()
            curses.noecho()  # Remove echo after continuing


class ScreenBuffer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen = self._new_buffer()
        self.clear()

    def _new_buffer(self):
        buffer = []
        for y in range(self.height):
            buffer.append([(None, None)] * self.width)
        return buffer

    def add(self, x, y, char, color=None):
        self.buffer[int(y)][int(x)] = (char, color)

    def clear(self):
        self.buffer = self._new_buffer()

    def render(self, curses_screen, screen: Screen):
        blanks = set()
        for x in range(self.width):
            for y in range(self.height):
                if self.buffer[y][x] != self.screen[y][x]:
                    self.screen[y][x] = self.buffer[y][x]
                    char, color = self.buffer[y][x]
                    if char:
                        if color:
                            curses_screen.addch(y, x, char, color)
                        else:
                            curses_screen.addch(y, x, char)
                    else:
                        curses_screen.addch(y, x, '.')  # Need to write something before erasing to work 100%
                        blanks.add((y, x))

        curses_screen.refresh()
        if blanks:
            for y, x in blanks:
                curses_screen.addch(y, x, ' ')  # for macBook Pro console, otherwise some artifacts are left behind.
            curses_screen.refresh()


class Scene(KeyListener):
    def __init__(self, screen, controller):
        self.screen = screen
        self.controller = controller
        self.next_scene = None
        self.done = False
        self.init()

    @property
    def player(self):
        return self.controller.player

    def next(self):
        self.done = True

    def init(self):
        """ Initialize the scene """

    def start(self):
        """ Start the scene """
