from time import sleep

from games.screen import Screen
from games.objects import BouncyText, Border


class Manager:
    def start(self):
        screen = Screen(border=Border('*'))
        text = BouncyText(1, 1, "This is a bouncing text.")
        screen.add(text)

        with screen:
            while True:
                screen.render()
                sleep(0)
