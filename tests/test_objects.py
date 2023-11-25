from unittest.mock import Mock
from games.objects import (AbstractPlayer, Stickman, ScreenObject, Circle, Char,
                           ScreenObjectGroup, CompassionateBoss, AbstractEnemies, Bitmap, Text)


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

    player.destruct()
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
    so = Bitmap(0, 0, x_delta=-1)
    assert not so.is_out

    so.render(screen)
    assert so.x == -1
    assert not so.is_out

    for i in range(so.size):
        so.render(screen)
    assert so.x == -so.size - 1
    assert so.is_out


def test_sync(screen):
    so = ScreenObject(0, 0, size=0)
    so.sync(ScreenObject(1, 1, size=1))
    assert so.x == so.y == so.size == 1


def test_reset(screen):
    so = Text(0, 0, "Hello")
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


def test_add_remove_kid():
    so = ScreenObject(0, 0, size=0)
    kid = Circle(1, 1)

    so.add_kid(kid)
    assert kid in so.kids

    so.remove_kid(kid)
    assert kid not in so.kids
    assert len(so.kids) == 0

    so.remove_kid(kid)   # No op


def test_screen_object_group(screen):
    char = Char(0, 0, char='X')
    circle = Circle(0, 0)
    sog = ScreenObjectGroup(10, 10)
    sog.add(char, circle)

    screen.add(sog)
    with screen:
        screen.render()
        screen.render()

    assert sog.kids == {char, circle}

    print(sog.all_coords)
    assert sog.all_coords == {(10, 11), (11, 11), (11, 9), (9, 10), (7, 10), (12, 11), (12, 9),
                              (10, 9), (13, 10)}

    sog.y += 10
    with screen:
        screen.render()
    print(sog.all_coords)
    assert sog.all_coords == {(7, 20), (12, 21), (9, 20), (10, 19), (12, 19), (10, 21), (11, 21),
                              (13, 20), (11, 19)}


def test_compassionate_boss(screen, player):
    boss = CompassionateBoss('Max', Circle(1, 1,), player)
    screen.add(boss)
    boss.render(screen)
    assert boss.y == 1.1


def test_enemies(screen, player):
    class Enemies(AbstractEnemies):
        def create_enemy(self):
            return Circle(1, 1, x_delta=1, y_delta=2)

        def should_spawn_boss(self):
            return self.player.score == 10

        def create_boss(self):
            return Char(20, 1, char='B', y_delta=1)

    # First render creates 1 enemy
    enemies = Enemies(player)
    enemies.render(screen)
    screen.add(enemies)

    assert len(enemies.kids) == 1
    assert len(screen) == 2  # enemies + first_enemy
    first_enemy = list(enemies.kids)[0]

    # Next 10 renders will create max of 5 enemies and no more
    with screen:
        for i in range(10):
            screen.render()
    assert len(enemies.kids) == 5
    assert len(screen) == 6

    assert first_enemy.x == 11
    assert first_enemy.y == 21

    # Satisfy condition to create boss
    player.score = 10
    with screen:
        screen.render()
    assert len(enemies.kids) == 6
    assert len(screen) == 7

    # No more enemies will be created
    with screen:
        screen.render()
    assert len(enemies.kids) == 6
    assert len(screen) == 7

    # Next 10 renders will remove all enemies as they get out of screen when player is no longer active
    player.active = False
    with screen:
        for i in range(10):
            screen.render()
    print(enemies.kids)
    assert len(enemies.kids) == 0
    assert len(screen) == 1  # Just "enemies" object


def test_bitmap(screen):
    class ABC(Bitmap):
        bitmap = r"""
ab
def"""  # noqa

    with screen as s:
        # Normal
        abc = ABC(10, 10)
        s.add(abc)
        s.render()
        assert s.without_distractions() == [
            [('a', None), ('b', None)],
            [('d', None), ('e', None), ('f', None)]]
        assert abc.coords == {
            (9, 9), (10, 9),
            (9, 10), (10, 10), (11, 10)}

        # Flip it
        abc = ABC(10, 10, flip=True)
        s.reset()
        s.add(abc)
        s.render()
        assert s.without_distractions() == [
            [('b', None), ('a', None)],
            [('f', None), ('e', None), ('d', None)]]
        assert abc.coords == {
            (10, 9), (11, 9),
            (9, 10), (10, 10), (11, 10)}
