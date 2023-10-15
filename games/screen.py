import curses


class Screen:
    def __enter__(self):
        self.screen = curses.initscr()
        self.screen.keypad(True)

        curses.noecho()
        curses.cbreak()

        return self.screen

    def __exit__(self):
        self.screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
