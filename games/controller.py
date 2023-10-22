import curses

from games.screen import Screen, Scene
from games.objects import KeyListener


class Controller(KeyListener):
    #: Name of the game
    name = None

    def __init__(self, screen: Screen):
        self.screen = screen
        self.screen.border.title = self.name
        self.key_listeners = set()
        self.current_index = 0
        self.current_scene = None
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
            self.current_scene.reset()

    def play(self):
        if not self.current_scene:
            self.set_scene(self.scenes[self.current_index](self.screen, self))
        elif self.current_scene.done:
            self.current_index += 1
            if self.current_index >= len(self.scenes):
                self.current_index = 0
            self.set_scene(self.scenes[self.current_index](self.screen, self))

        key = self.screen.key

        if key > 0:
            self.key_pressed(key)
            # self.screen.border.status['key'] = key

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

    def key_pressed(self, key):
        """
        A key has been pressed

        :param int: ASCII code of the key
        """
        for listener in self.key_listeners:
            listener.key_pressed(key)

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
