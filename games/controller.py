import curses

from games.screen import Screen


class Controller:
    #: Name of the game
    name = None

    def __init__(self, screen: Screen):
        self.screen = screen
        self.screen.border.title = self.name
        self.init()
        self.last_key = None

    def process(self):
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
        pass

    def left_pressed(self):
        pass

    def right_pressed(self):
        pass

    def up_pressed(self):
        pass

    def down_pressed(self):
        pass

    def escape_pressed(self):
        pass

    def space_pressed(self):
        pass

    def enter_pressed(self):
        pass
