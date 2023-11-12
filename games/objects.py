from random import randint, random

from games.screen import Screen
from games.listeners import KeyListener


class ScreenObject:
    """ Base class for all objects on screen """
    def __init__(self, x: int, y: int, x_delta=None, y_delta=None, color=None, size=1, parent=None):
        self.x = x
        self.y = y
        self.x_delta = x_delta
        self.y_delta = y_delta
        self.color = color or getattr(self, 'color', None)
        self.size = size
        self.coords = set()
        self.parent = parent
        self.kids = set()
        self.screen = None
        self.visible = True

    def copy(self):
        obj = self.__class__(self.x, self.y, x_delta=self.x_delta, y_delta=self.y_delta,
                             color=self.color, size=self.size, parent=self.parent)
        obj.coords = self.coords
        obj.kids = self.kids
        obj.visible = self.visible
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

    def can_move_x(self, x_delta=0):
        """ Indicates if object can move by given or self delta """
        return x_delta or self.x_delta or True

    def can_move_y(self, y_delta=0):
        """ Indicates if object can move by given or self delta """
        return y_delta or self.y_delta or True

    def shifted_coords(self, x_delta=0, y_delta=0):
        x_adjustment = (self.x - int(self.x)) if x_delta else 0
        y_adjustment = (self.y - int(self.y)) * 1.1 if y_delta else 0  # Times 1.1 to avoid stuck in rock
        new_coords = set()
        for x, y in self.coords:
            new_coords.add((int(x + x_delta + x_adjustment), int(y + y_delta + y_adjustment)))
        return new_coords

    def sync(self, screen_object, location_only=False):
        self.x = screen_object.x
        self.y = screen_object.y

        if not location_only:
            self.x_delta = screen_object.x_delta
            self.y_delta = screen_object.y_delta
            self.size = screen_object.size
            self.color = screen_object.color
            self.visible = screen_object.visible
            self.coords = screen_object.coords

    def render(self, screen: Screen):
        """ Render object onto the given screen """
        self.screen = screen

        if self.x_delta and self.can_move_x():
            self.x += self.x_delta

        if self.y_delta and self.can_move_y():
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

    def __init__(self, *args, objects=None, add_bar=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.ordered_objects = list(objects) if objects else []
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


class AbstractPlayer(ScreenObject, KeyListener):
    def __init__(self, name, shape: ScreenObject, controller, score_title='score', show_total=False,
                 max_hp=1):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color)

        self.name = name
        self.shape = shape
        self._original_shape = shape
        self.high_score = 0
        self.total_score = 0
        self.show_total = show_total
        self.char = shape.char
        self.controller = controller
        self.score_title = score_title
        self.max_hp = max_hp

        self.reset()

    def reset(self):
        super().reset()
        self.hp = self.max_hp
        self.score = 0
        self.alive = True
        self.active = True  # Indicates if the player is taking action, such as shooting
        self.is_hit = False
        self.size = self.shape.size
        self.shape = self._original_shape
        self.obstacles = None
        if self.screen:
            self.x = int(self.screen.width / 2) + 1
            self.y = self.screen.height - int(self.size / 2) - 1

    @property
    def visible(self):
        return self.alive

    @visible.setter
    def visible(self, visible):
        self.alive = visible

    def can_move_x(self, x_delta=0):
        x_delta = x_delta or self.x_delta or 0
        return (self.screen
                and (self.x + x_delta > self.size and self.x + x_delta < self.screen.width - self.size)
                and (not self.obstacles
                     or not(self.obstacles.coords & self.shifted_coords(x_delta=x_delta))))

    def can_move_y(self, y_delta=0):
        y_delta = y_delta or self.y_delta or 0
        return (self.screen
                and (self.y + y_delta > self.size and self.y + y_delta < self.screen.height-self.size/2)
                and (not self.obstacles
                     or not(self.obstacles.coords & self.shifted_coords(y_delta=y_delta))))

    def render(self, screen: Screen):
        super().render(screen)

        # screen.debug(kids=len(self.kids))

        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        score = str(self.score)
        if self.score < self.high_score:
            score += ' | High: {}'.format(self.high_score)
        if self.show_total and self.score < self.total_score:
            score += ' | Total: {}'.format(self.total_score)

        self.screen.status[self.score_title] = score

    def scored(self, points=1):
        """ Add given points, defaults to 1, to the player's score """
        self.score += points
        self.total_score += points
        if self.score > self.high_score:
            self.high_score = self.score

    def killed_enemy(self):
        self.scored()

    def killed_boss(self):
        self.scored(points=5)

    def got_hit(self, points=1):
        """ Decrease player's HP by the given points and destruct when HP hits 0 """
        self.is_hit = True
        self.hp -= points
        if self.hp <= 0:
            self.hp = 0
            self.destruct()

    def destruct(self, msg='The End', explode=True, explosion_size=20):
        self.alive = False
        self.active = False
        self.screen.add(Text(self.screen.width / 2, self.screen.height / 2, msg,
                             is_centered=True))
        if explode:
            self.screen.add(Explosion(self.x, self.y, size=explosion_size,
                                      on_finish=self.controller.reset_scene))


class CompassionateBoss(ScreenObject):
    def __init__(self, name, shape: ScreenObject, player: AbstractPlayer, hp=5):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color,
                         x_delta=shape.x_delta, y_delta=shape.y_delta)
        self.name = name
        self.shape = shape
        self.player = player
        if self.y_delta is None:
            self.y_delta = 0.1
        if self.x_delta is None:
            self.x_delta = self.initial_x_delta
        self.is_hit = False
        self.char = shape.char
        self.hp = hp
        self.max_hp = hp

    @property
    def initial_x_delta(self):
        return max(random() * 0.5, 0.2)

    def got_hit(self):
        """ React to getting hit and return state for is_hit """
        return False

    def render(self, screen: Screen):
        super().render(screen)
        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        if self in self.screen:
            if self.x > self.player.x:
                self.x_delta = -1 * abs(self.x_delta)
            else:
                self.x_delta = abs(self.x_delta)

            if self.y > self.screen.height + 2.5 and self.player.alive:
                self.y = -2.5

            if self.is_hit:
                self.color = self.screen.rainbow_colors[self.screen.renders % len(self.screen.rainbow_colors)]
                self.is_hit = self.got_hit()


class AbstractEnemies(ScreenObject):
    def __init__(self, player: AbstractPlayer, max_enemies=5):
        super().__init__(0, 0)
        self.max_enemies = max_enemies
        self.enemies = set()
        self.player = player
        self.boss = None

    def create_enemy(self) -> ScreenObject:
        """ Create an enemy instance """
        raise NotImplementedError

    def on_death(self, enemy):
        """ Optionally add custom actions when an enemy dies """

    def should_spawn_boss(self):
        """ Override this to customize logic for when a boss should be created """
        return False

    def create_boss(self) -> ScreenObject:
        """ Create a boss instance """
        raise NotImplementedError

    def additional_enemies(self):
        """ Increase enemies as the player levels up """
        return int(self.player.score / 100)

    def render(self, screen: Screen):
        super().render(screen)

        if self.player.active:
            # Create enemies
            if len(self.enemies) < self.max_enemies + self.additional_enemies():
                enemy = self.create_enemy()
                self.enemies.add(enemy)
                screen.add(enemy)

            # Create boss
            if self.should_spawn_boss() and self.boss not in screen:
                self.boss = self.create_boss()
                self.enemies.add(self.boss)
                screen.add(self.boss)

        for enemy in list(self.enemies):
            # Make them go fast when player is destroyed
            if not self.player.active:
                if enemy.y_delta:
                    enemy.y_delta *= 1.2
                if enemy.x_delta:
                    enemy.x_delta *= 1.2

            # If it is out of the screen, remove it (except for boss or player is dead)
            if enemy.is_out and (enemy != self.boss or not self.player.active):
                self.enemies.remove(enemy)
                screen.remove(enemy)

            # Otherwise, check if player's projectiles hit the enemies
            else:
                for projectile in list(self.player.kids):
                    if projectile.coords & enemy.coords:
                        if enemy == self.boss and self.boss.hp > 0:
                            self.boss.hp -= 1
                            self.boss.is_hit = True
                            break

                        self.enemies.remove(enemy)
                        screen.remove(enemy)

                        self.player.kids.remove(projectile)
                        screen.remove(projectile)

                        self.on_death(enemy)

                        if hasattr(projectile, 'explode'):
                            projectile.explode()

                        if enemy == self.boss:
                            self.player.killed_boss()
                        else:
                            self.player.killed_enemy()

                        break
                else:
                    if enemy.all_coords & self.player.coords and self.player.active:
                        self.player.got_hit()


class Bitmap(ScreenObject):
    def __init__(self, *args, char=None, random_start=False, remove_after_animation=False,
                 flip=False, centered=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.char = getattr(self, 'char', char)  # or chr(0x2588)
        self._bitmaps = getattr(self, 'bitmaps', [])
        self._frames_per_bitmap = getattr(self, 'frames_per_bitmap', 10)
        self._remove_after_animation = getattr(self, 'remove_after_animation', remove_after_animation)
        self._bitmap_index_offset = randint(0, max(len(self._bitmaps), 1) - 1) if random_start else 0
        self.renders = 0
        self.flip = flip
        self.centered = centered
        self._bitmap = self._bitmaps and self._bitmaps[0] or getattr(self, 'bitmap', """\
▓▓▓▓▓
▓▓▓▓▓
▓▓▓▓▓
▓▓▓▓▓
▓▓▓▓▓
""")  # noqa
        self.size = len(self._bitmap.strip('\n').split('\n'))

    def draw(self, x, y, char, screen: Screen):
        color = self.color[self.renders % len(self.color)] if type(self.color) in (tuple, list) else self.color
        screen.draw(x, y, char, color=color)
        self.coords.add((x, y))

    def render(self, screen: Screen):
        super().render(screen)
        self.renders += 1

        if self._bitmaps:
            index = (self._bitmap_index_offset + int(self.renders / self._frames_per_bitmap)) % len(self._bitmaps)
            bitmap = self._bitmaps[index]
        else:
            bitmap = self._bitmap
        bitmap = bitmap.strip('\n').split('\n')

        x_size = len(bitmap[0])
        if self.centered:
            start_x = int(self.x - x_size / 2)
            start_y = int(self.y - self.size / 2)
        else:
            start_x = int(self.x)
            start_y = int(self.y)
        self.coords = set()

        for y in range(start_y, start_y + self.size):
            x_size = len(bitmap[y-start_y])
            for x in range(start_x, start_x + x_size):
                if self.flip:
                    x_offset = (start_x + x_size - 1) - x
                else:
                    x_offset = x - start_x
                if bitmap[y-start_y][x_offset] != ' ':
                    self.draw(x, y, self.char or bitmap[y-start_y][x_offset], screen)

        if self._remove_after_animation and self.renders > self._frames_per_bitmap * (len(self._bitmaps) - 1):
            screen.remove(self)
            if self.parent:
                self.parent.remove_kid(self)


class ObjectMap(Bitmap):
    """ Represents screen objects using characters on a bitmap """
    def __init__(self, *args, grid_size=5, **kwargs):
        super().__init__(*args, centered=False, **kwargs)

        #: Number of characters each object represents
        self.grid_size = grid_size

        #: Map of object characters to colors
        self._object_map = getattr(self, 'object_map', {})

        self._objects_mapped = 0

    @property
    def is_out(self):
        return False

    def render(self, screen: Screen):
        # from time import time
        # start = time()

        super().render(screen)

        # if not getattr(screen, 'render_secs', None):
        #    screen.render_secs = {}
        # screen.render_secs[self.__class__.__name__] = round((time() - start) * screen.fps_limit * 60, 2)
        # screen.debug(render_secs=screen.render_secs)

    def draw(self, x, y, char, screen):
        x = (x - int(self.x)) * self.grid_size + int(self.x)
        y = (y - int(self.y)) * self.grid_size + int(self.y) + self.grid_size / 2
        if char in self._object_map:
            if (x > screen.width + self.grid_size or y > screen.height + self.grid_size
                    or x < -self.grid_size or y < -self.grid_size):
                return
            obj_cls = self._object_map[char]
            obj = obj_cls(x, y)
            self._objects_mapped += 1
            # screen.debug(objects_mapped_per_frame=int(self._objects_mapped / screen.renders))
            obj.renders = self.renders + x
            obj.render(screen)
            self.coords.update(obj.coords)


class Text(ScreenObject):
    def __init__(self, x: int, y: int, text: str, x_delta=None, y_delta=None, is_centered=False, color=None):
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


class Logo(ScreenObject):
    def __init__(self, x, y, name: str, shape: ScreenObject, color=None):
        super().__init__(x, y, size=7, color=color)
        self.text = Text(self.x, self.y + 3, name, is_centered=True, color=self.color)
        self.shape = shape

    def render(self, screen: Screen):
        super().render(screen)

        self.text.sync(self, location_only=True)
        self.text.y += 3
        self.shape.sync(self, location_only=True)

        self.text.render(screen)
        self.shape.render(screen)


class Monologue(Text):
    def __init__(self, x: int, y: int, texts=[], on_finish=None, x_delta=None, y_delta=None):
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
    def __init__(self, char: str = None, show_fps=False, title=None):
        super().__init__(0, 0)
        self.char = char
        self.show_fps = show_fps
        self.title = title
        self.reset()

    def reset(self):
        super().reset()

        #: A value from 0 to 1 indicating the level of player's health
        self.health_level = 0

        #: A value from 0 to 1 indicating the level of player's energy
        self.energy_level = 0
        self.status = {}

    def set_levels(self, health_level, energy_level):
        health_level = round(health_level, 2)  # Easier to compare with
        energy_level = round(energy_level, 2)
        if self.health_level != health_level:
            self.health_level = health_level

        if self.energy_level != energy_level:
            self.energy_level = energy_level

    def render(self, screen: Screen):
        for x in range(screen.width):
            for y in range(screen.height):
                if x == 0 or y == 0 or x == screen.width - 1 or y == screen.height - 1:
                    char = (self.char
                            or (x == 0 and y == 0) and chr(0x2554)
                            or (x == screen.width - 1 and y == 0) and chr(0x2557)
                            or (x == 0 and y == screen.height - 1) and chr(0x255A)
                            or (x == screen.width - 1 and y == screen.height - 1) and chr(0x255D)
                            or (y == 0 or y == screen.height - 1) and chr(0x2550)
                            or (x == 0 or x == screen.width - 1) and chr(0x2551))

                    if self.health_level and x == 0 and y < screen.height - 1:
                        y_level = int((screen.height - 1) * self.health_level + 0.5)
                        if screen.height - 1 - y <= y_level:
                            screen.draw(1, y, '│', color=screen.COLOR_RED)

                    if self.energy_level and x == screen.width - 1 and y < screen.height - 1:
                        y_level = int((screen.height - 2) * self.energy_level + 0.5)
                        if screen.height - 1 - y <= y_level:
                            screen.draw(screen.width - 2, y, '│', color=screen.COLOR_GREEN)

                    screen.draw(x, y, char, color=self.color)

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
    def __init__(self, x: int, y: int, shape='^', x_delta=None, y_delta=-1, color=None, size=1,
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

        self.coords = set() if self.shape is None else {(int(self.x), int(self.y))}

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
    def __init__(self, x: int, y: int, size=5, char='O', x_delta=None, y_delta=None, color=None,
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
    def __init__(self, x: int, y: int, size=2, char='!', x_delta=None, y_delta=None, color=None,
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
    def __init__(self, x: int, y: int, size=3, char='#', x_delta=None, y_delta=None, color=None,
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
        if self.current_size > self.size:
            screen.remove(self)
            if self.parent:
                self.parent.remove_kid(self)
            if self.on_finish:
                self.on_finish()
            return

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


class Triangle(ScreenObject):
    def __init__(self, x: int, y: int, size=5, char='^', x_delta=None, y_delta=None, color=None,
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
    def __init__(self, x: int, y: int, size=3, char='=', x_delta=None, y_delta=None, color=None,
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

            self.bar = Bar(self.x, self.y + max_size / 2 + 1, size=bar_size, color=self.color or screen.COLOR_CYAN)
            screen.add(self.bar)
            self.kids.add(self.bar)

            instruction = Monologue(self.x, self.y + 1.5 * max_size,
                                    texts=['Change selection using arrow keys',
                                           'Press Space to start or Esc to exit'])
            screen.add(instruction)
            self.kids.add(instruction)

            for i, x in enumerate(range(start_x, end_x, bar_size)):
                chosen = self.choices[i]
                chosen.x = x + bar_size / 2
                chosen.y = self.y
                screen.add(chosen)
                self.kids.add(chosen)

                if i == self._current:
                    self.bar.x = chosen.x + 1

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
 ▓▓  
  ▓  
  ▓  
  ▓  
 ▓▓▓ 
"""  # noqa


class Two(Bitmap):
    represents = '2'
    bitmap = """
 ▓▓▓ 
▓   ▓
   ▓ 
 ▓▓  
▓▓▓▓▓
"""  # noqa


class Three(Bitmap):
    represents = '3'
    bitmap = """
▓▓▓▓ 
    ▓
 ▓▓▓ 
    ▓
▓▓▓▓ 
"""  # noqa


class Four(Bitmap):
    represents = '4'
    bitmap = """\
  ▓▓ 
 ▓ ▓ 
▓  ▓ 
▓▓▓▓▓
   ▓ 
"""  # noqa


class Five(Bitmap):
    represents = '5'
    bitmap = """\
▓▓▓▓▓
▓    
▓▓▓▓ 
    ▓
▓▓▓▓ 
"""  # noqa


class Six(Bitmap):
    represents = '6'
    bitmap = """\
 ▓▓▓ 
▓    
▓▓▓▓ 
▓   ▓
 ▓▓▓ 
"""  # noqa


class Seven(Bitmap):
    represents = '7'
    bitmap = """\
▓▓▓▓▓
   ▓ 
  ▓  
 ▓   
▓    
"""  # noqa


class Eight(Bitmap):
    represents = '8'
    bitmap = """\
 ▓▓▓ 
▓   ▓
 ▓▓▓ 
▓   ▓
 ▓▓▓ 
"""  # noqa


class Nine(Bitmap):
    represents = '9'
    bitmap = """\
 ▓▓▓ 
▓   ▓
 ▓▓▓▓
    ▓
 ▓▓▓ 
"""  # noqa


class Zero(Bitmap):
    represents = '0'
    bitmap = """\
 ▓▓▓ 
▓   ▓
▓   ▓
▓   ▓
 ▓▓▓ 
"""  # noqa


class Plus(Bitmap):
    represents = '+'
    bitmap = """\
     
  │  
 ─┼─ 
  │  
     
"""  # noqa


class Minus(Bitmap):
    represents = '-'
    bitmap = """\
     
     
 ─── 
     
     
"""  # noqa


class Multiply(Bitmap):
    represents = '*'
    bitmap = """\
     
 ╲ ╱ 
  ╳  
 ╱ ╲ 
     
"""  # noqa


class Divide(Bitmap):
    represents = '/'
    bitmap = """\
     
   ╱ 
  ╱  
 ╱   
     
"""  # noqa


class Space(Bitmap):
    represents = ' '
    bitmap = """
     
     
     
     
     
"""  # noqa


class Zombie(Bitmap):
    bitmaps = (r"""
   O 
 \-/\
  / |
 /\  
/ |  
""",  # noqa
r"""
  O  
\-/\ 
  | |
 /\  
/ |  
""",  # noqa
r"""
  O  
 -|\_
/ |  
 /\  
 | \ 
""",  # noqa
r"""
  O  
 -|\|
/ |  
 /\  
 | \ 
""",  # noqa
r"""
  O  
 -|\_
/ /  
 /\  
/  \ 
""") # noqa


class DyingZombie(Bitmap):
    remove_after_animation = True
    frames_per_bitmap = 3
    bitmaps = (r"""
   O 
 \-/\
  / |
 /\  
/ |  
""",  # noqa
r"""
     
  O  
\-/\ 
 /\  
/ |  
""",  # noqa
r"""
     
     
 O   
\-|\_
_| \_
""",  # noqa
r"""
     
     
     
| O\ 
\-|\|
""",  # noqa
r"""
     
     
     
_  \ 
\-O-/
""",  # noqa
r"""
     
     
     
     
\-O-/
""") # noqa


class Stickman(Bitmap):
    bitmap = r"""
 ☻ 
/|\
/ \
"""  # noqa


class StickmanCelebrate(Bitmap):
    bitmaps = (r"""
\☻/
 |
/ \
""",
r"""
 ☻
/|\
/ \
""")  # noqa


class StickmanWorried(Bitmap):
    bitmap = r"""
 ☺ 
\|/
/ \
"""  # noqa


class StickmanScared(Bitmap):
    bitmap = r"""
\☹/
 | 
/ \
"""  # noqa


class Wasp(Bitmap):
    frames_per_bitmap = 1
    bitmaps = (r"""
 vv
8oQ
""",  # noqa
r"""
 ww
8oQ
""")  # noqa noqa


class WaspKaiju(Bitmap):
    bitmaps = (r"""
 __      __
/  \_--_/  \
   |O  O|
    \  /
     \/
""",  # noqa
r"""
--_      __
   \_--_/  \
   |O  O|
    \  /
     ||
""",  # noqa
r"""
-__      ___
   \_--_/
   |O  O|
    \  /
     \/
""",  # noqa
r"""
--_      __
   \_--_/  \
   |O  O|
    \  /
     ||
""")  # noqa


class DyingWaspKaiju(Bitmap):
    remove_after_animation = True
    frames_per_bitmap = 3
    bitmaps = (r"""
 __      __
/  \_--_/  \
   \O  O/
    |  |
    \\//
""",  # noqa noqa
r"""
 
--_      _--
   \_--_/
   \O  O/
    \||/
""",  # noqa noqa
r"""
 
 
__      __
  \O  O/
   \\//
""",  # noqa noqa
r"""
 
 
 
_     _
 \O-O/
""") # noqa


class HealthPotion(Char):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, char='♥', **kwargs)


class Tree(Bitmap):
    color = 'green'
    bitmaps = (r"""
 __  /   __
//\\|\\_/\\\
// |\||/
     ||
     ||
     ||
""",  # noqa
r"""
 __  |   __
\//\|\\_/\ /
\/ |\||\
     ||
     ||
     ||
""",  # noqa
r"""
 __  \   __
 \/\|\\_/\ \
\\ |\||\
     ||
     ||
     ||
""")  # noqa


class Sun(Bitmap):
    color = ('white', 'yellow')
    bitmap = (r"""
   \ | /
    ooo
-- ooooo --
-- ooooo --
    ooo
   / | \
""")  # noqa


class Rock(Bitmap):
    color = 'magenta'
    bitmap = r"""
  
  
 /¯\
/_//¯¯\
"""  # noqa


class Volcano(Bitmap):
    color = 'magenta'
    bitmap = r"""
   /V\
  / \ \
 / / \_¯\
/________\
"""  # noqa


class Landscape(ObjectMap, KeyListener):
    move_speed = 0
    object_map = {
        'S': Sun,
        'T': Tree,
        'R': Rock,
        'V': Volcano
    }

    def __init__(self, *args, player: AbstractPlayer = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.player = player

    def left_pressed(self):
        if not self.player or self.player.can_move_x(x_delta=-1):
            self.x += self.move_speed

    def right_pressed(self):
        if not self.player or self.player.can_move_x(x_delta=1):
            self.x -= self.move_speed
