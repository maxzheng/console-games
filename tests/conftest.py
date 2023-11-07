from unittest.mock import Mock

import pytest

from games.controller import Controller
from games.screen import Screen, ScreenBuffer, Scene
from games.objects import Border, AbstractPlayer, Diamond


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


@pytest.fixture
def game(screen):
    class Game(Controller):
        name = 'Game Test'

        def init(self):
            self.scenes = [Scene]

    return Game(screen)


@pytest.fixture
def player(game):
    return AbstractPlayer('Jon', Diamond(40, 20), game)
