from unittest.mock import Mock
from games.objects import AbstractPlayer, Stickman, ScreenObject, Circle, Char


def test_player(screen):
    controller = Mock()
    player = AbstractPlayer('Max', Stickman(0, 0), controller, score_title='Wins', show_total=True)

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


def test_all_kids(screen):
    so = ScreenObject(1, 1)
    circle = Circle(10, 10)
    circle.add_kid(Char(10, 10, char='X'))
    so.add_kid(circle)

    assert len(so.all_kids) == 2

    list(circle.kids)[0].render(screen)
    assert so.all_coords == {(10, 10)}

    circle.render(screen)
    assert so.all_coords == {(10, 11), (9, 9), (12, 10), (8, 10), (11, 9), (10, 10), (10, 9), (9, 11), (11, 11)}


def test_is_out(screen):
    so = ScreenObject(0, 0, x_delta=-1)
    assert not so.is_out

    so.render(screen)
    assert so.x == -1
    assert not so.is_out

    so.render(screen)
    assert so.x == -2
    assert so.is_out


def test_sync(screen):
    so = ScreenObject(0, 0, size=0)
    so.sync(ScreenObject(1, 1, size=1))
    assert so.x == so.y == so.size == 1


def test_reset(screen):
    so = ScreenObject(0, 0, size=0)
    circle = Circle(1, 1)
    so.add_kid(circle)
    screen.add(so, circle)

    assert len(so.kids) == 1
    assert so in screen
    assert circle in screen

    so.render(screen)
    so.reset()

    assert len(so.kids) == 0
    assert so in screen
    assert circle not in screen
