from games.screen import OrderedScreenObjects
from games.objects import Circle, Square, Diamond


def test_ordered_screen_objects():
    so = OrderedScreenObjects()
    circle = Circle(1, 1)
    square = Square(2, 2)
    diamond = Diamond(2, 2)

    so.add(circle)
    assert len(so) == 1

    so.add(square, diamond)
    assert list(so) == [circle, square, diamond]

    so.remove(square)
    assert list(so) == [circle, diamond]

    assert square not in so
    assert circle in so

    so.remove(diamond, circle)
    assert len(so) == 0
