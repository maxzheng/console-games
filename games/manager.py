from time import sleep

from games.screen import Screen
from games.objects import BouncyText, Border


class Manager:
    def start(self, fps=30):
        screen = Screen(border=Border('*', show_fps=True))
        text = BouncyText(1, 1, "This is a bouncing text.")
        screen.add(text)

        with screen:
            while True:
                screen.render()
                sleep(0.7/fps)
