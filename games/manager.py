from games.screen import Screen
from games.objects import Border
# from games.geo_bash import GeoBash
from games.number_crush import NumberCrush


class Manager:
    def start(self, fps=30, debug=False):
        screen = Screen(border=Border('*', show_fps=debug), debug=debug, fps=fps)

        with screen:
            game = NumberCrush(screen)
            screen.controller = game

            while True:
                screen.render()
                game.play()
