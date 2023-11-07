from unittest.mock import Mock

import pytest

from games.screen import Screen, ScreenBuffer
from games.objects import Border


@pytest.fixture
def screen(monkeypatch):
    monkeypatch.setattr('curses.cbreak', Mock())
    monkeypatch.setattr('curses.nocbreak', Mock())
    monkeypatch.setattr('curses.endwin', Mock())

    screen = Screen(border=Border())
    screen._width = 80
    screen._height = 20
    screen.buffer = ScreenBuffer(80, 20)
    return screen
