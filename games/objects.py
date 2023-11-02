from random import randint, random

from games.screen import Screen
from games.listeners import KeyListener


class ScreenObject:
    """ Base class for all objects on screen """
    def __init__(self, x: int, y: int, x_delta=0, y_delta=0, color=None, size=1, parent=None):
        self.x = x
        self.y = y
        self.x_delta = x_delta
        self.y_delta = y_delta
        self.color = color
        self.size = size
        self.coords = set()
        self.parent = parent
        self.kids = set()
        self.is_visible = True
        self.screen = None

    def copy(self):
        obj = self.__class__(self.x, self.y, x_delta=self.x_delta, y_delta=self.y_delta,
                             color=self.color, size=self.size, parent=self.parent)
        obj.coords = self.coords
        obj.kids = self.kids
        obj.is_visible = self.is_visible
        obj.screen = self.screen
        return obj

    @property
    def all_kids(self):
        kids = self.kids.copy()
        all_kids = set()

        while kids:
            kid = kids.pop()
            all_kids.add(kid)

            if kid.kids:
                kids.update(kid.kids)

        return all_kids

    @property
    def all_coords(self):
        """ All coords of this object and its kids """
        coords = self.coords.copy()
        for kid in self.all_kids:
            coords.update(kid.coords)

        return coords

    @property
    def is_out(self):
        """ Indicates if the object center is outside of the screen border """
        try:
            return (self.x + self.size < 0 or self.x - self.size > self.screen.width
                    or self.y + self.size < 0 or self.y - self.size > self.screen.height)

        except Exception:
            return False

    def sync(self, screen_object):
        self.x = screen_object.x
        self.y = screen_object.y
        self.x_delta = screen_object.x_delta
        self.y_delta = screen_object.y_delta
        self.size = screen_object.size
        self.color = screen_object.color
        self.is_visible = screen_object.is_visible
        self.coords = screen_object.coords

    def render(self, screen: Screen):
        """ Render object onto the given screen """
        self.screen = screen

        if self.x_delta:
            self.x += self.x_delta

        if self.y_delta:
            self.y += self.y_delta

    def reset(self):
        """ Reset object to original state """
        if self.screen:
            for kid in self.kids:
                if kid in self.screen:
                    self.screen.remove(kid)
        self.kids = set()

    def add_kid(self, screen_object):
        self.kids.add(screen_object)

    def remove_kid(self, screen_object):
        if screen_object in self.kids:
            self.kids.remove(screen_object)

    def replace_kid(self, old_object, new_object):
        self.remove_kid(old_object)
        self.add_kid(new_object)


class ScreenObjectGroup(ScreenObject):
    """ Group of objects that move together as one """

    def __init__(self, *args, add_bar=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.ordered_objects = []
        self.add_bar = add_bar

    def add(self, *screen_objects):
        self.ordered_objects.extend(screen_objects)

    def render(self, screen):
        super().render(screen)

        if self.kids:
            for kid in self.kids:
                kid.y = int(self.y + 3 if isinstance(kid, Bar) else self.y)

        else:
            padding = 1
            width = sum((o.size + padding) for o in self.ordered_objects)
            block_size = width / len(self.ordered_objects)
            start_x = int(self.x - width / 2) - 2

            for obj in self.ordered_objects:
                start_x += block_size
                obj.x = start_x

                screen.add(obj)
                self.kids.add(obj)

            if self.add_bar:
                divider = Bar(self.x + 1, self.y + 3, size=width + 1)
                screen.add(divider)
                self.kids.add(divider)


class Bitmap(ScreenObject):
    def __init__(self, *args, char=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.char = getattr(self, 'char', char)
        self._bitmaps = getattr(self, 'bitmaps', [])
        self._frames_per_bitmap = getattr(self, 'frames_per_bitmap', 10)
        self._bitmap_index_offset = randint(0, max(len(self._bitmaps), 1) - 1)

        self._bitmap = getattr(self, 'bitmap', """\
#####
#####
#####
#####
#####
""")  # noqa
        self.size = 5

    def render(self, screen: Screen):
        super().render(screen)

        if self._bitmaps:
            index = (self._bitmap_index_offset + int(screen.renders / self._frames_per_bitmap)) % len(self._bitmaps)
            bitmap = self._bitmaps[index]
        else:
            bitmap = self._bitmap
        bitmap = bitmap.strip('\n').split('\n')

        start_x = int(self.x - self.size / 2)
        start_y = int(self.y - self.size / 2)
        self.coords = set()

        for x in range(start_x, start_x + self.size):
            for y in range(start_y, start_y + self.size):
                if bitmap[y-start_y][x-start_x] != ' ':
                    screen.draw(x, y, self.char or bitmap[y-start_y][x-start_x], color=self.color)
                    self.coords.add((x, y))


class Text(ScreenObject):
    def __init__(self, x: int, y: int, text: str, x_delta=0, y_delta=0, is_centered=False, color=None):
        super().__init__(x, y, size=int(len(text) / 2), x_delta=x_delta, y_delta=y_delta, color=color)
        self.text = text
        self.is_centered = is_centered

    def render(self, screen: Screen):
        super().render(screen)

        if self.text:
            self.coords = set()
            x = self.x - len(self.text) / 2 if self.is_centered else self.x
            for offset, char in enumerate(self.text):
                screen.draw(x + offset, self.y, char, color=self.color)
                self.coords.add((int(x + offset), int(self.y)))


class BouncyText(Text):
    def __init__(self, x: int, y: int, text: str, x_delta=1, y_delta=1):
        super().__init__(x, y, text, x_delta=x_delta, y_delta=y_delta)

    def render(self, screen: Screen):
        super().render(screen)

        if self.x + len(self.text) >= screen.width - 1 or self.x == 1:
            self.x_delta = -self.x_delta
        if self.y >= screen.height - 1 or self.y == 1:
            self.y_delta = -self.y_delta


class Monologue(Text):
    def __init__(self, x: int, y: int, texts=[], on_finish=None, x_delta=0, y_delta=0):
        super().__init__(x, y, texts[0], x_delta=x_delta, y_delta=y_delta)
        self.center_x = x
        self.texts = texts
        self.on_finish = on_finish
        self.reset()

    def reset(self):
        super().reset()
        self.index = 0
        self.renders = 0

    def render(self, screen: Screen):
        self.renders += 1
        self.text = self.texts[self.index]
        self.x = self.center_x - len(self.text) / 2

        super().render(screen)

        if self.renders % 45 == 0:
            self.index += 1
            if self.index >= len(self.texts):
                screen.remove(self)
                if self.on_finish:
                    self.on_finish()


class Border(ScreenObject):
    def __init__(self, char: str, show_fps=False, title=None):
        super().__init__(0, 0)
        self.char = char
        self.show_fps = show_fps
        self.title = title
        self.reset()

    def reset(self):
        super().reset()
        self.status = {}

    def render(self, screen: Screen):
        for x in range(screen.width):
            for y in range(screen.height):
                if x == 0 or y == 0 or x == screen.width - 1 or y == screen.height - 1:
                    screen.draw(x, y, self.char, color=self.color)

        if self.title:
            padded_title = ' ' + self.title + ' '
            start_x = round((screen.width - len(padded_title)) / 2)
            for x_offset in range(len(padded_title)):
                screen.draw(start_x + x_offset, 0, padded_title[x_offset], color=self.color)

        if self.show_fps and screen.fps:
            self.status['FPS'] = screen.fps

        if self.status:
            debug_text = ' ' + ' | '.join(
                ['{}: {}'.format(k[0].upper() + k[1:], v) for k, v in self.status.items()]) + ' '
            start_x = round((screen.width - len(debug_text)) / 2)
            for x_offset in range(len(debug_text)):
                screen.draw(start_x + x_offset, screen.height - 1, debug_text[x_offset], color=self.color)


class Char(ScreenObject):
    def __init__(self, *args, char, **kwargs):
        super().__init__(*args, **kwargs)
        self.char = char

    def render(self, screen: Screen):
        super().render(screen)

        self.coords = {(int(self.x), int(self.y))}

        if not self.is_out:
            screen.draw(self.x, self.y, self.char, color=self.color)


class Projectile(ScreenObject):
    def __init__(self, x: int, y: int, shape='^', x_delta=0, y_delta=-1, color=None, size=1,
                 parent=None, explode_after_renders=None, explosion=None, explosions=1):
        super().__init__(x, y, color=color, x_delta=x_delta, y_delta=y_delta, size=size, parent=parent)
        self.shape = shape
        self.explode_after_renders = explode_after_renders
        self.renders = 0
        self.explosion = explosion
        self.explosions = explosions

    @property
    def char(self):
        return self.shape

    def render(self, screen: Screen):
        super().render(screen)

        self.renders += 1

        self.coords = {(int(self.x), int(self.y))}

        if not self.is_out and self.shape is not None:
            screen.draw(self.x, self.y, self.shape, color=self.color)

        if (self.explode_after_renders and self.renders >= self.explode_after_renders):
            self.explode()

    def explode(self):
        if self.explosion:
            if self.explosions:
                explosion = self.explosion.copy()
                self.x_delta = 0
                self.y_delta = 0
                explosion.x = self.x
                explosion.y = self.y
                self.screen.add(explosion)
                self.parent.add_kid(explosion)
                self.explosions -= 1

            else:
                self.screen.remove(self)
                self.parent.remove_kid(self)


class Circle(ScreenObject):
    def __init__(self, x: int, y: int, size=3, char='O', x_delta=0, y_delta=0, color=None,
                 name=None):
        super().__init__(x, y, x_delta=x_delta, y_delta=y_delta, color=color,
                         size=size)
        self.char = char
        self.name = name

    def render(self, screen: Screen):
        super().render(screen)

        self.coords = {(int(self.x - 1), int(self.y - 1)), (int(self.x), int(self.y - 1)),
                       (int(self.x + 1), int(self.y - 1)), (int(self.x - 2), int(self.y)),
                       (int(self.x + 2), int(self.y)), (int(self.x - 1), int(self.y + 1)),
                       (int(self.x), int(self.y + 1)), (int(self.x + 1), int(self.y + 1))}

        for x, y in self.coords:
            screen.draw(x, y, self.char, color=self.color)


class Diamond(ScreenObject):
    def __init__(self, x: int, y: int, size=3, char='!', x_delta=0, y_delta=0, color=None,
                 name=None):
        super().__init__(x, y, x_delta=x_delta, y_delta=y_delta, color=color,
                         size=size)
        self.char = char
        self.name = name

    def render(self, screen: Screen):
        super().render(screen)

        self.coords = {(int(self.x + 1), int(self.y)), (int(self.x - 1), int(self.y)),
                       (int(self.x), int(self.y + 1)), (int(self.x), int(self.y - 1))}

        for x, y in self.coords:
            screen.draw(x, y, self.char, color=self.color)


class Square(ScreenObject):
    def __init__(self, x: int, y: int, size=3, char='#', x_delta=0, y_delta=0, color=None,
                 name=None, solid=False):
        super().__init__(x, y, x_delta=x_delta, y_delta=y_delta, color=color,
                         size=size)
        self.char = char
        self.name = name
        self.solid = solid

    def render(self, screen: Screen):
        super().render(screen)

        start_x = int(self.x - self.size / 2)
        start_y = int(self.y - self.size / 2)
        self.coords = set()

        for x in range(start_x, int(start_x + self.size)):
            for y in range(start_y, int(start_y + self.size)):
                if self.solid or (x == start_x or x == start_x + self.size - 1
                                  or y == start_y or y == start_y + self.size - 1):
                    self.coords.add((int(x), int(y)))
                    screen.draw(x, y, self.char, color=self.color)


class Explosion(ScreenObject):
    def __init__(self, x: int, y: int, size=10, char='*', on_finish=None, **kwargs):
        super().__init__(x, y, size=size, **kwargs)

        self.current_size = 2
        self.char = char
        self.on_finish = on_finish

    def copy(self):
        obj = super().copy()
        obj.current_size = self.current_size
        obj.char = self.char
        obj.on_finish = self.on_finish
        return obj

    def render(self, screen: Screen):
        super().render(screen)

        start_x = int(self.x - self.current_size / 2)
        start_y = int(self.y - self.current_size / 2)
        self.coords = set()
        colors = [screen.COLOR_YELLOW, screen.COLOR_RED]

        for x in range(start_x, start_x + self.current_size):
            for y in range(start_y, start_y + self.current_size):
                if (x == start_x or x == start_x + self.current_size - 1
                        or y == start_y or y == start_y + self.current_size - 1):
                    distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** (1/2)
                    if distance < self.current_size and random() < 2/self.current_size:
                        self.coords.add((int(x), int(y)))
                        screen.draw(x, y, self.char, color=colors[randint(0, len(colors) - 1)])

        self.current_size += 1
        if self.current_size > self.size:
            screen.remove(self)
            if self.parent:
                self.parent.remove_kid(self)
            if self.on_finish:
                self.on_finish()


class Triangle(ScreenObject):
    def __init__(self, x: int, y: int, size=3, char='^', x_delta=0, y_delta=0, color=None,
                 name=None):
        super().__init__(x, y, x_delta=x_delta, y_delta=y_delta, color=color,
                         size=size)
        self.char = char
        self.name = name

    def render(self, screen: Screen):
        super().render(screen)

        self.coords = {(int(self.x), int(self.y - 1))}

        if self.size >= 2:
            self.coords.update({(int(self.x - 1), int(self.y)), (int(self.x + 1), int(self.y))})
            if self.size == 2:
                self.coords.update({(int(self.x), int(self.y))})

        if self.size >= 3:
            self.coords.update({(int(self.x - 1), int(self.y + 1)), (int(self.x), int(self.y + 1)),
                                (int(self.x + 1), int(self.y + 1)), (int(self.x - 2), int(self.y + 1)),
                                (int(self.x + 2), int(self.y + 1))})

        for x, y in self.coords:
            screen.draw(x, y, self.char, color=self.color)


class Bar(ScreenObject):
    def __init__(self, x: int, y: int, size=3, char='=', x_delta=0, y_delta=0, color=None,
                 parent=None):
        super().__init__(x, y, x_delta=x_delta, y_delta=y_delta, color=color,
                         size=size, parent=parent)
        self.char = char

    def render(self, screen: Screen):
        super().render(screen)

        start_x = int(self.x - self.size / 2 - 0.5)  # Round down
        self.coords = set()

        for x in range(start_x, int(start_x + self.size)):
            self.coords.add((int(x), int(self.y)))
            screen.draw(x, self.y, self.char, color=self.color)


class Choice(ScreenObject, KeyListener):
    def __init__(self, x: int, y: int, color=None, choices=[], on_select=None, on_change=None, current=None):
        super().__init__(x, y, color=color)

        self.choices = choices
        self.on_select = on_select
        self.on_change = on_change
        self._current = current if current is not None else int(len(self.choices) / 2 - 0.5)

        self.reset()

    @property
    def current(self):
        return self.choices[self._current]

    def reset(self):
        super().reset()
        self.bar = None

    def render(self, screen: Screen):
        super().render(screen)

        if not self.bar:
            max_size = max(c.size for c in self.choices)
            bar_size = max_size * 4
            width = bar_size * len(self.choices)
            start_x = int(self.x - width / 2)
            end_x = start_x + width

            self.bar = Bar(self.x, self.y + max_size / 2 + 1, size=bar_size, color=self.color)
            screen.add(self.bar)
            self.kids.add(self.bar)

            instruction = Monologue(self.x, self.y + 1.5 * max_size,
                                    texts=['Change selection using arrow keys',
                                           'Press Space to start or Esc to exit'])
            screen.add(instruction)
            self.kids.add(instruction)

            for i, x in enumerate(range(start_x, end_x, bar_size)):
                choice = self.choices[i]
                choice.x = x + bar_size / 2
                choice.y = self.y
                screen.add(choice)
                self.kids.add(choice)

                if i == self._current:
                    self.bar.x = choice.x + 1

    def left_pressed(self):
        if self._current > 0 and self.bar:
            self._current -= 1
            self.bar.x -= self.bar.size
            if self.on_change:
                self.on_change(self.choices[self._current])

    def right_pressed(self):
        if self._current < len(self.choices) - 1 and self.bar:
            self._current += 1
            self.bar.x += self.bar.size
            if self.on_change:
                self.on_change(self.choices[self._current])

    def enter_pressed(self):
        if self.on_select:
            self.on_select(self.choices[self._current])

    def space_pressed(self):
        self.enter_pressed()


class One(Bitmap):
    represents = '1'
    bitmap = """
 ##  
  #  
  #  
  #  
 ### 
"""  # noqa


class Two(Bitmap):
    represents = '2'
    bitmap = """
 ### 
#   #
   # 
 ##  
#####
"""  # noqa


class Three(Bitmap):
    represents = '3'
    bitmap = """
#### 
    #
 ### 
    #
#### 
"""  # noqa


class Four(Bitmap):
    represents = '4'
    bitmap = """\
   # 
  ## 
 # # 
#####
   # 
"""  # noqa


class Five(Bitmap):
    represents = '5'
    bitmap = """\
#####
#    
#### 
    #
#### 
"""  # noqa


class Six(Bitmap):
    represents = '6'
    bitmap = """\
 ### 
#    
#### 
#   #
 ### 
"""  # noqa


class Seven(Bitmap):
    represents = '7'
    bitmap = """\
#####
   # 
  #  
 #   
#    
"""  # noqa


class Eight(Bitmap):
    represents = '8'
    bitmap = """\
 ### 
#   #
 ### 
#   #
 ### 
"""  # noqa


class Nine(Bitmap):
    represents = '9'
    bitmap = """\
 ### 
#   #
 ####
    #
 ### 
"""  # noqa


class Zero(Bitmap):
    represents = '0'
    bitmap = """\
 ### 
#   #
#   #
#   #
 ### 
"""  # noqa


class Plus(Bitmap):
    represents = '+'
    bitmap = """\
     
  |  
 -+- 
  |  
     
"""  # noqa


class Minus(Bitmap):
    represents = '-'
    bitmap = """\
     
     
 --- 
     
     
"""  # noqa


class Multiply(Bitmap):
    represents = '*'
    bitmap = """\
     
 \ / 
  X  
 / \ 
     
"""  # noqa


class Divide(Bitmap):
    represents = '/'
    bitmap = """\
     
   / 
  /  
 /   
     
"""  # noqa


class Space(Bitmap):
    represents = ' '
    bitmap = """
     
     
     
     
     
"""  # noqa


class Zombie(Bitmap):
    bitmaps = ("""
   O 
 \-/\\
  / |
 /\  
/ |  
""",  # noqa
"""
  O  
\-/\\ 
  | |
 /\  
/ |  
""",  # noqa
"""
  O  
 -|\\_
/ |  
 /\  
 | \\ 
""",  # noqa
"""
  O  
 -|\\|
/ |  
 /\  
 | \\ 
""",  # noqa
"""
  O  
 -|\\_
/ /   
 /\  
/ \\  
""") # noqa


class Stickman(Bitmap):
    bitmap = """
 O 
/|\\
/ \\
"""  # noqa


BITMAPS = dict((b.represents, b) for b in [Zero, One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Plus, Minus,
                                           Multiply, Divide, Space])
