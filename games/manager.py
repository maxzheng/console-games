from games.screen import Screen
from games.objects import Border
from games.geo_bash import GeoBash


class Manager:
    def start(self, fps=30, debug=False):
        screen = Screen(border=Border('*', show_fps=debug), debug=debug, fps=fps)

        with screen:
            geo_bash = GeoBash(screen)

            while True:
                screen.render()
                geo_bash.process()
