import curses
from time import sleep, time

from games.listeners import KeyListener


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

        #: Number of times the screen has rendered
        self.renders = 0

        #: Show debug info
        self._debug = debug

        #: List of screen objects
        self._objects = []

        #: Game controller
        self.controller = None

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

        self.colors = []
        for color in ('RED', 'GREEN', 'BLUE', 'YELLOW', 'CYAN', 'MAGENTA'):
            color_name = 'COLOR_' + color
            color_id = getattr(curses, color_name)
            curses.init_pair(color_id, color_id, -1)
            setattr(self, color_name, curses.color_pair(color_id))
            self.colors.append(getattr(self, color_name))

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
                return

            obj = self._objects.pop(index)
            for kid in obj.kids:
                self.remove(kid)

    def reset(self):
        self._objects = []
        self.renders = 0
        if self.border:
            self.border.reset()

    def resize_screen(self):
        max_height, max_width = self._screen.getmaxyx()
        self._height = max_height - 1
        self._width = max_width - 1
        self.buffer = ScreenBuffer(max_width, max_height)

    def draw(self, x: int, y: int, char: str, color=None):
        """ Draw character on the given position """
        if x >= 0 and x < self._width and y >= 0 and y < self._height:
            self.buffer.add(x, y, char, color)

    def render(self):
        start_time = time()

        self._render()

        render_time = time() - start_time
        if render_time < 1/self.fps:
            sleep(1/self.fps - render_time)

    def _render(self):
        self.renders += 1

        self.buffer.clear()

        for obj in self:
            if obj.is_visible:
                obj.render(self)
            if obj.is_out:
                if obj.parent:
                    try:
                        obj.parent.kids.remove(obj)
                    except Exception:
                        pass
                self.remove(obj)

        if self.border:
            if self._debug:
                self.border.status['objects'] = len(self)
            self.border.render(self)

        try:
            self.buffer.render(self._screen)
        except Exception as e:
            self.debug(exception=str(e))
            self.resize_screen()

    def debug(self, **debug_info):
        """ Show debug info (enabled when --debug flag is used) """
        self.border.status.update(debug_info)


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

    def render(self, screen: Screen):
        for x in range(self.width):
            for y in range(self.height):
                if self.buffer[y][x] != self.screen[y][x]:
                    self.screen[y][x] = self.buffer[y][x]
                    char, color = self.buffer[y][x]
                    if color:
                        screen.addstr(int(y), int(x), char or ' ', color)
                    else:
                        screen.addstr(int(y), int(x), char or ' ')


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
