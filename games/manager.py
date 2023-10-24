from games.screen import Screen
from games.objects import Border
from games.chooser import Chooser


class Manager:
    def start(self, fps=30, debug=False):
        screen = Screen(border=Border('*', show_fps=debug), debug=debug, fps=fps)

        with screen:
            game = Chooser(screen)
            screen.controller = game

            while not game.done:
                screen.render()
                game.play()
