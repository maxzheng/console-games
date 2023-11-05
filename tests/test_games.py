import pytest

from games.manager import Manager
from games.controller import Controller
from games.screen import Screen


def test_manager():
    Manager()


def test_controller():
    screen = Screen()
    with pytest.raises(ValueError):
        controller = Controller(screen)  # noqa
