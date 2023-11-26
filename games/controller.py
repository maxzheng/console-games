from time import time
import curses

from games.screen import Screen, Scene
from games.objects import KeyListener, ScreenObject


class Controller(KeyListener):
    #: Name of the game
    name = None

    def __init__(self, screen: Screen):
        if not self.name:
            raise ValueError('Please set class attribute `name` to the name of the game')

        self.screen = screen
        self.reset()

    def reset(self):
        self.key_listeners = set()
        self._key_presses = set()
        self.current_index = 0
        self.current_scene = None
        self.last_key_pressed = None
        self.last_key_time = None
        self.done = False
        self.scenes = []
        self.logo = ScreenObject(0, 0)
        self.init()

    def init(self):
        """ Initialize the game with scenes and other global objects used across scenes:

                self.scenes = [SceneClass1, SceneClass2]    # Required
                self.logo = AnyScreenObjectClass()          # Optional
                self.player = ...                           # Optional

            :raises ValueError: `self.scenes` must be set by overriding this function.
        """
        raise ValueError('Please override init() to set self.scenes to a list of Scene classes')

    def set_scene(self, scene: Scene):
        """ Set the given scene as the active scene to be rendered """
        self.screen.reset()
        self.current_scene = scene
        self.key_listeners = {scene}
        self._key_presses = set()
        scene.start()

    def reset_scene(self):
        """ Restart the current scene """
        if self.current_scene:
            self.set_scene(self.current_scene.__class__(self.screen, self))

    def play(self):
        """ Handle play logic, such as key presses """
        self.screen.border.title = self.name

        if not self.current_scene:
            self.set_scene(self.scenes[self.current_index](self.screen, self))
        elif self.current_scene.done:
            self.current_index += 1
            if self.current_index >= len(self.scenes):
                self.current_index = 0
            self.set_scene(self.scenes[self.current_index](self.screen, self))

        key = self.next_key()

        if key:
            self.key_pressed(key)
        elif self.last_key_time and (time() - self.last_key_time) > 0.5:
            self.key_released()

        if key:
            if key == curses.KEY_LEFT or key == ord('h'):
                self.left_pressed()

            elif key == curses.KEY_RIGHT or key == ord('l'):
                self.right_pressed()

            elif key == curses.KEY_UP or key == ord('k'):
                self.up_pressed()

            elif key == curses.KEY_DOWN or key == ord('j'):
                self.down_pressed()

            elif key == 27 or key == ord('q'):
                self.escape_pressed()

            elif key == ord(' ') or key == ord('f'):
                self.space_pressed()

            elif key == 10:
                self.enter_pressed()

            elif key >= 48 and key <= 57:
                self.number_pressed(key - 48)

            elif key == 45:
                self.minus_pressed()

    def next_key(self):
        """ Get the next unique key from a series of presses """
        key = self.screen.key
        last_key = None
        while key > 0:  # Drain the key buffer to avoid input lag
            if key != last_key and key not in self._key_presses:
                self._key_presses.add(key)
                last_key = key
            key = self.screen.key

        return self._key_presses.pop() if self._key_presses else None

    def key_pressed(self, key):
        if key == ord('d') == self.last_key_pressed:
            self.screen._debug = not self.screen._debug
            if not self.screen._debug:
                self.screen.border.reset()

        if key == ord('D') == self.last_key_pressed:
            self.screen.debug()

        # self.screen.debug(key=key)

        self.last_key_pressed = key
        self.last_key_time = time()

        for listener in self.key_listeners:
            listener.key_pressed(key)

    def key_released(self):
        for listener in self.key_listeners:
            listener.key_released()

    def left_pressed(self):
        for listener in self.key_listeners:
            listener.left_pressed()

    def right_pressed(self):
        for listener in self.key_listeners:
            listener.right_pressed()

    def up_pressed(self):
        for listener in self.key_listeners:
            listener.up_pressed()

    def down_pressed(self):
        for listener in self.key_listeners:
            listener.down_pressed()

    def escape_pressed(self):
        for listener in self.key_listeners:
            listener.escape_pressed()

    def space_pressed(self):
        for listener in self.key_listeners:
            listener.space_pressed()

    def enter_pressed(self):
        for listener in self.key_listeners:
            listener.enter_pressed()

    def minus_pressed(self):
        for listener in self.key_listeners:
            listener.minus_pressed()

    def number_pressed(self, number):
        for listener in self.key_listeners:
            listener.number_pressed(number)
