import pytest

from games.screen import Screen, ScreenBuffer
from games.objects import Border


@pytest.fixture
def screen():
    screen = Screen(border=Border())
    screen._width = 80
    screen._height = 20
    screen.buffer = ScreenBuffer(80, 20)
    return screen
