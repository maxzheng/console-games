from contextlib import contextmanager
from time import sleep, time

from games.screen import Screen
from games.objects import BouncyText, Border
from games.geo_bash import GeoBash


class Manager:
    def start(self, fps=30):
        screen = Screen(border=Border('*', show_fps=True))

        with screen:
            geo_bash = GeoBash(screen)

            while True:
                with self.fps_limit(fps):
                    screen.render()
                    geo_bash.process()

    @contextmanager
    def fps_limit(self, fps):
        start_time = time()

        yield

        render_time = time() - start_time
        if render_time < 1/fps:
            sleep(1/fps - render_time)
