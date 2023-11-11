from games.screen import Screen
from games.objects import Circle, Square, Diamond


def test_add_and_remove():
    so = Screen()
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

    so.reset()
    assert len(so) == 0


def test_enter_exit(screen):
    # These don't seem to work under pytest
    with screen as s:
        assert len(s.colors) == 8
        assert s.width
        assert s.height
        assert s.buffer


def test_buffer_render(screen):
    def without_distractions(buffer):
        content = []
        for y, row in enumerate(buffer):
            new_row = []
            for x, col in enumerate(row):
                if x != 0 and y != 0 and x != len(row) - 1 and y != len(buffer) - 1 and (col[0] or col[1]):
                    new_row.append(col)
            if new_row:
                content.append(new_row)
        return content

    with screen as s:
        assert s.renders == 0

        s.add(Circle(10, 10))
        s.render()

        assert s.renders == 1
        assert without_distractions(s.buffer.screen) == [
            [('O', None), ('O', None), ('O', None)],
            [('O', None), ('O', None)],
            [('O', None), ('O', None), ('O', None)]]

        s.reset()
        s.add(Circle(10, 10, color=s.COLOR_RED))
        s.render()

        assert s.renders == 1
        assert without_distractions(s.buffer.screen) == [
            [('O', 256), ('O', 256), ('O', 256)],
            [('O', 256), ('O', 256)],
            [('O', 256), ('O', 256), ('O', 256)]]
