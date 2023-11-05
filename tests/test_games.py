import pytest

from games.manager import Manager
from games.controller import Controller
from games.screen import Screen
from games.objects import Border


def test_manager():
    Manager()


def test_controller():
    screen = Screen()
    with pytest.raises(ValueError):
        controller = Controller(screen)  # noqa


def test_game():
    screen = Screen(border=Border('*'))

    class Game(Controller):
        name = 'Test'

        def init(self):
            self.scenes = []

    game = Game(screen)
    assert not game.done
