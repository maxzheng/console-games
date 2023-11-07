from games.manager import Manager
from games.controller import Controller
from games.screen import Scene


def test_manager():
    Manager()


def test_game(screen):
    class Game(Controller):
        name = 'Test'

        def init(self):
            self.scenes = [Scene]

    with screen:
        game = Game(screen)
        assert not game.done

        game.play()
        assert game.current_scene
        game.reset_scene()
