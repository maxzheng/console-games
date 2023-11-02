from time import time
import curses

from games.screen import Screen, Scene
from games.objects import KeyListener, ScreenObject, Text


class Controller(KeyListener):
    #: Name of the game
    name = None

    def __init__(self, screen: Screen):
        self.screen = screen
        self.screen.border.title = self.name
        self.key_listeners = set()
        self.current_index = 0
        self.current_scene = None
        self.last_key_pressed = None
        self.last_key_time = None
        self.done = False
        self.init()

    def init(self):
        """ Initialize the game """

    def set_scene(self, scene: Scene):
        self.screen.reset()
        self.current_scene = scene
        self.key_listeners = {scene}
        scene.start()

    def reset_scene(self):
        if self.current_scene:
            self.set_scene(self.current_scene.__class__(self.screen, self))

    def play(self):
        if not self.current_scene:
            self.set_scene(self.scenes[self.current_index](self.screen, self))
        elif self.current_scene.done:
            self.current_index += 1
            if self.current_index >= len(self.scenes):
                self.current_index = 0
            self.set_scene(self.scenes[self.current_index](self.screen, self))

        last_key = key = self.screen.key
        while key > 0:  # Drain the key buffer to avoid input lag
            last_key = key
            key = self.screen.key
        key = last_key

        if key > 0:
            self.key_pressed(key)
        elif self.last_key_time and (time() - self.last_key_time) > 0.5:
            self.key_released()

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

    def key_pressed(self, key):
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

    class Logo(ScreenObject):
        def __init__(self, x, y, name, color=None):
            super().__init__(x, y, size=int(len(name) / 2), color=color)
            self.name = name
            self.text = None

        def render(self, screen: Screen):
            super().render(screen)

            if not self.text:
                self.text = Text(self.x, self.y + 3, self.name, is_centered=True, color=self.color)

            self.text.render(screen)
