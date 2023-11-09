from games.screen import Screen
from games.objects import Border
from games.chooser import Chooser


class Manager:
    def start(self, game_filter=None, fps=30, debug=False):
        screen = Screen(border=Border(show_fps=debug), debug=debug, fps=fps)

        with screen:
            game = Chooser(screen, game_filter=game_filter)
            screen.controller = game

            while not game.done:
                screen.render()
                game.play()
