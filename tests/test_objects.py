from unittest.mock import Mock
from games.objects import Player, Stickman


def test_player(screen):
    controller = Mock()
    player = Player('Max', Stickman(0, 0), controller, score_title='Wins')

    assert player.alive
    assert player.visible
    assert player.score == player.high_score == player.total_score

    player.scored()
    assert player.score == player.high_score == player.total_score == 1

    player.scored(points=2)
    assert player.score == player.high_score == player.total_score == 3

    assert player.screen is None
    player.render(screen)
    assert player.screen == screen
    assert screen.status['Wins'] == '3'

    player.destroy()
    assert not player.alive and not player.visible

    player.reset()
    assert player.score == 0
    assert player.high_score == player.total_score == 3

    player.scored()
    assert player.score == 1
    assert player.high_score == 3
    assert player.total_score == 4

    player.render(screen)
    assert screen.status['Wins'] == '1 | High: 3 | Total: 4'
