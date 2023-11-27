from math import pi, sin, cos
from random import randint, random, choice

from games.screen import Screen
from games.listeners import KeyListener


class ScreenObject:
    """ Base class for all objects on screen """
    def __init__(self, x: int, y: int, x_delta=0, y_delta=0, color=None, size=1, parent=None,
                 remove_after_renders=None, on_remove=None, random_movement=False, player=None):
        self.x = x
        self.y = y
        self.x_delta = x_delta
        self.y_delta = y_delta
        self.color = color or getattr(self, 'color', None)
        self._size = size
        self.coords = set()
        self.parent = parent
        self.kids = set()
        self.screen = None
        self.visible = True
        self.renders = 0
        self.remove_after_renders = remove_after_renders
        self.on_remove = on_remove
        self._random_movement = random_movement or getattr(self, 'random_movement', False)
        self.player = player

    def reset(self):
        """ Reset object to original state """
        self.renders = 0
        if self.screen:
            for kid in self.kids:
                if kid in self.screen:
                    self.screen.remove(kid)
        self.kids = set()

    def copy(self):
        obj = self.__class__(self.x, self.y, x_delta=self.x_delta, y_delta=self.y_delta,
                             color=self.color, size=self.size, parent=self.parent)
        obj.coords = self.coords
        obj.kids = self.kids
        obj.visible = self.visible
        obj.screen = self.screen
        return obj

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.on_size_change(value)

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

    def on_size_change(self, size):
        pass

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
        if self.renders == 0:
            self.render_init(screen)

        self.renders += 1
        self.screen = screen

        if self.x_delta and self.can_move_x():
            self.x += self.x_delta

        if self.y_delta and self.can_move_y():
            self.y += self.y_delta

        if self.remove_after_renders and self.renders > self.remove_after_renders:
            self.remove()

        if self._random_movement:
            self.x_delta *= 0.95
            self.y_delta *= 0.95

            if abs(self.x_delta) + abs(self.y_delta) < 0.01:
                self.x_delta = random() * 0.75 * choice([1, -1])
                self.y_delta = random() * 0.75 * choice([1, -1])

    def render_init(self, screen: Screen):
        """ Only called once when self.renders = 0. Useful for initializing objects to render later """

    def add_kid(self, screen_object):
        self.kids.add(screen_object)
        if not screen_object.parent:
            screen_object.parent = self

    def remove_kid(self, screen_object):
        if screen_object in self.kids:
            self.kids.remove(screen_object)

    def replace_kid(self, old_object, new_object):
        self.remove_kid(old_object)
        self.add_kid(new_object)

    def remove(self):
        self.screen.remove(self)
        if self.parent:
            self.parent.remove_kid(self)
        if self.on_remove:
            self.on_remove()


class Object3D(ScreenObject):
    def __init__(self, *args, points=None, connect_points=False, rotate_axes=None, random_start=False,
                 magnify_by_size=False, **kwargs):
        super().__init__(*args, **kwargs)

        #: Coordinates in 3D space
        self._points = points or getattr(self, 'points', [])

        #: Connect points sequentially to form lines / shapes
        self.connect_points = connect_points

        #: Axes (x, y, z) to rotate
        self._rotate_axes = rotate_axes or getattr(self, 'rotate_axes', (1, 1, 2, 1))

        #: Factor to multiply theta to adjust rotation
        if len(self._rotate_axes) > 3:
            self.theta_factor = self._rotate_axes[3]
        else:
            self.theta_factor = 1
        if random_start:
            self.theta_factor = (random() + 0.1) * choice([1, -1]) * self.theta_factor

        #: Factor to magnify the points
        self.magnify_by_size = magnify_by_size

    @staticmethod
    def dot(m1, m2):
        """ Return the product of the given two matrices """
        return [[sum(a * b for a, b in zip(m1_row, m2_col)) for m2_col in zip(*m2)] for m1_row in m1]

    def rotate_point(self, point, theta):
        """ Rotate the given point using self._rotate_axes and theta (radian) """
        new_point = [[point[0]], [point[1]], [point[2]]]

        if self._rotate_axes[0]:  # x
            x_rotation = [
                [self._rotate_axes[0], 0, 0],
                [0, cos(theta), -sin(theta)],
                [0, sin(theta), cos(theta)],
            ]
            new_point = self.dot(x_rotation, new_point)

        if self._rotate_axes[1]:  # y
            y_rotation = [
                [cos(theta), 0, sin(theta)],
                [0, self._rotate_axes[1], 0],
                [-sin(theta), 0, cos(theta)],
            ]
            new_point = self.dot(y_rotation, new_point)

        if self._rotate_axes[2]:  # z
            z_rotation = [
                [cos(theta), -sin(theta), 0],
                [sin(theta), cos(theta), 0],
                [0, 0, self._rotate_axes[2]],
            ]
            new_point = self.dot(z_rotation, new_point)

        return new_point[0][0], new_point[1][0], new_point[2][0]

    def render(self, screen: Screen):
        super().render(screen)
        self.coords = set()

        points = []
        for point in self._points:
            color = (point[3] if len(point) > 3 else None) or self.color
            theta = (screen.renders / 10 * self.theta_factor) % (2 * pi)
            new_point = self.rotate_point(point, theta)
            x, y, _ = new_point

            if self.magnify_by_size:
                x *= self.size
                y *= self.size

            abs_x = int(self.x + x)
            abs_y = int(self.y + y)

            screen.draw(abs_x, abs_y, chr(0x2588), color)
            points.append((abs_x, abs_y))
            self.coords.add((abs_x, abs_y))

        if self.connect_points:
            last_point = None
            connecting_points = set()
            for point in points:
                if last_point:
                    x_offset = last_point[0]
                    y_offset = last_point[1]
                    x_delta = (point[0] - last_point[0])
                    y_delta = (point[1] - last_point[1])
                    x_sign = 1 if point[0] >= last_point[0] else -1
                    y_sign = 1 if point[1] >= last_point[1] else -1

                    if x_delta:
                        slope = (point[1] - last_point[1]) / x_delta

                        if abs(x_delta) > abs(y_delta):
                            for x in range(last_point[0], point[0], x_sign):
                                y = slope * (x - x_offset) + y_offset
                                connecting_points.add((int(x), int(y)))
                        else:
                            for y in range(last_point[1], point[1], y_sign):
                                x = (y - y_offset) / slope + x_offset
                                connecting_points.add((int(x), int(y)))

                    else:
                        for y in range(last_point[1], point[1], y_sign):
                            connecting_points.add((x_offset, int(y)))

                last_point = point

            for point in (connecting_points - set(points)):
                screen.draw(point[0], point[1], chr(0x2588), self.color)
                self.coords.add((int(point[0]), int(point[1])))


class Line3D(Object3D):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, connect_points=True, **kwargs)


class Cube(Line3D):
    def __init__(self, *args, size=7, **kwargs):
        super().__init__(*args, size=size, points=self._make_cube(size=size), **kwargs)

    def on_size_change(self, size):
        self._points = self._make_cube()

    def _make_cube(self, size=None):
        if not size:
            size = self.size
        return [[-size, -size, size],
                [size, -size, size],
                [size, size, size],
                [-size, size, size],
                [-size, -size, size],
                [-size, -size, -size],
                [-size, size, -size],
                [-size, size, size],
                [-size, size, -size],
                [size, size, -size],
                [size, size, size],
                [size, size, -size],
                [size, -size, -size],
                [-size, -size, -size],
                [size, -size, -size],
                [size, -size, size],
                ]


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
            start_x = int(self.x - width / 2) - 3

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
                 max_hp=1, **kwargs):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color, **kwargs)

        self.name = name
        self.shape = shape
        self._original_shape = shape
        self._original_x = self.x
        self._original_y = self.y
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
        self.x_delta = self.y_delta = 0
        self.x = self._original_x
        self.y = self._original_y
        self.shape.sync(self)
        self.show_score = True

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
                     or not (self.obstacles.coords & self.shifted_coords(x_delta=x_delta))))

    def can_move_y(self, y_delta=0):
        y_delta = y_delta or self.y_delta or 0
        return (self.screen
                and (self.y + y_delta > self.size / 2 and self.y + y_delta < self.screen.height-self.size/2)
                and (not self.obstacles
                     or not (self.obstacles.coords & self.shifted_coords(y_delta=y_delta))))

    def render(self, screen: Screen):
        super().render(screen)

        # screen.debug(all_kids=len(self.all_kids), kids=len(self.kids))

        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        score = str(self.score)
        if self.score < self.high_score:
            score += ' | High: {}'.format(self.high_score)
        if self.show_total and self.score < self.total_score:
            score += ' | Total: {}'.format(self.total_score)

        if self.show_score:
            self.screen.status[self.score_title] = score
        else:
            self.screen.status.pop(self.score_title, None)

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

    def destruct(self, msg=None, explode=True, explosion_size=30, on_finish=None):
        self.alive = False
        self.active = False
        if msg:
            self.screen.add(Text(self.screen.width / 2, self.screen.height / 2, msg,
                                 centered=True))
        if explode:
            self.screen.add(Explosion(self.x, self.y, size=explosion_size,
                                      on_finish=on_finish or self.controller.reset_scene))


class CompassionateBoss(ScreenObject):
    def __init__(self, name, shape: ScreenObject, player: AbstractPlayer, hp=5):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color,
                         x_delta=shape.x_delta, y_delta=shape.y_delta,
                         player=player)
        self.name = name
        self.shape = shape
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
    def __init__(self, player: AbstractPlayer, max_enemies=5, **kwargs):
        super().__init__(0, 0, player=player, **kwargs)
        self.max_enemies = max_enemies
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
            if len(self.kids) < self.max_enemies + self.additional_enemies():
                enemy = self.create_enemy()
                enemy.parent = self
                self.add_kid(enemy)
                screen.add(enemy)

            # Create boss
            if self.should_spawn_boss() and self.boss not in screen:
                self.boss = self.create_boss()
                self.boss.parent = self
                self.add_kid(self.boss)
                screen.add(self.boss)

        for enemy in list(self.kids):
            # Make them go fast when player is destroyed
            if not self.player.active:
                if enemy.y_delta:
                    enemy.y_delta *= 1.2
                if enemy.x_delta:
                    enemy.x_delta *= 1.2

            # If it is out of the screen, remove it (except for boss or player is dead)
            if enemy.is_out and (enemy != self.boss or not self.player.active):
                enemy.remove()

            # Otherwise, check if player's projectiles hit the enemies
            else:
                for projectile in list(self.player.all_kids):
                    if projectile.coords & enemy.coords:
                        if enemy == self.boss and self.boss.hp > 0:
                            self.boss.hp -= 1
                            self.boss.is_hit = True
                            break

                        enemy.remove()

                        self.player.remove_kid(projectile)
                        projectile.remove()

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
        self.flip = flip
        self._flip_map = getattr(self, 'flip_map', {})
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

        if self._bitmaps:
            index = (self._bitmap_index_offset + int(self.renders / self._frames_per_bitmap)) % len(self._bitmaps)
            bitmap = self._bitmaps[index]
        else:
            bitmap = self._bitmap
        bitmap = bitmap.strip('\n').split('\n')

        x_size = max(len(b) for b in bitmap)
        if self.centered:
            start_x = int(self.x - x_size / 2 + 0.5)
            start_y = int(self.y - self.size / 2 + 0.5)
        else:
            start_x = int(self.x)
            start_y = int(self.y)
        self.coords = set()

        for y in range(start_y, start_y + self.size):
            y_offset = y - start_y
            # x_size = len(bitmap[y_offset])
            for x in range(start_x, start_x + x_size):
                x_offset = x - start_x
                if self.flip:
                    x_offset = x_size - x_offset - 1
                if x_offset < len(bitmap[y_offset]) and bitmap[y_offset][x_offset] != ' ':
                    char = self.char or bitmap[y_offset][x_offset]
                    if self.flip and char in self._flip_map:
                        char = self._flip_map[char]
                    self.draw(x, y, char, screen)

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
        return False  # We want to be rendered always

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
    def __init__(self, x: int, y: int, text: str, x_delta=None, y_delta=None, centered=False, color=None):
        super().__init__(x, y, size=int(len(text) / 2), x_delta=x_delta, y_delta=y_delta, color=color)
        self.text = text
        self.centered = centered

    def render(self, screen: Screen):
        super().render(screen)

        if self.text:
            self.coords = set()
            x = self.x - int(len(self.text) / 2) if self.centered else self.x
            for offset, char in enumerate(self.text):
                screen.draw(x + offset, self.y, char, color=self.color)
                self.coords.add((int(x + offset), int(self.y)))


class Logo(ScreenObject):
    def __init__(self, x, y, name: str, shape: ScreenObject, color=None):
        super().__init__(x, y, size=7, color=color)
        self.text = Text(self.x, self.y + 3, name, centered=True, color=self.color)
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

    def render(self, screen: Screen):
        self.text = self.texts[self.index]
        self.x = self.center_x - len(self.text) / 2

        super().render(screen)

        if self.renders >= 30 + len(self.text):
            self.renders = 0
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
        super().render(screen)

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
        self.explosion = explosion
        self.explosions = explosions

    @property
    def char(self):
        return self.shape

    def render(self, screen: Screen):
        super().render(screen)

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
                self.remove()


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
        super().render(screen)

        if self.current_size > self.size:
            self.remove()
            if self.on_finish:
                self.on_finish()
            return

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
            bar_size = int(max_size * 3.5)
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


class Flame(ScreenObject):
    def render_init(self, screen: Screen):
        for flame_size in range(self.size):
            explosion = Explosion(self.x, self.y, size=flame_size, parent=self)
            projectile = Projectile(self.x, self.y, shape=None, parent=self,
                                    x_delta=self.x_delta * (1 + flame_size / 20),
                                    y_delta=self.y_delta, color=screen.COLOR_YELLOW,
                                    explode_after_renders=flame_size,
                                    explosion=explosion)
            self.add_kid(projectile)
            screen.add(projectile)

    def render(self, screen: Screen):
        super().render(screen)

        if not self.kids:  # Flamed out (explosions/projectiles are gone)
            self.remove()


class VolcanoErupting(ScreenObject):
    def render_init(self, screen: Screen):
        volcano = Volcano(self.x, self.y, color=self.color)
        screen.add(volcano)
        self.add_kid(volcano)

        flame = Flame(self.x, self.y, y_delta=-1, size=self.size)
        screen.add(flame)
        self.add_kid(flame)


class Helicopter(Bitmap):
    frames_per_bitmap = 1
    color = 'red'
    flip_map = {'/': '\\', '\\': '/', 'e': 'ɘ', 's': 'ƨ', 'N': 'И'}
    bitmaps = (r"""
  ----
 __|___
/_|    \____ \
| News |___/\/
\______/
 _/  _\_/
""",  # noqar
r"""
 - ---
 __|___
/_|    \____/ 
| News |___/\/
\______/
 _/  _\_/
""",  # noqa
r"""
 -- --
 __|___
/_|    \____/\
| News |___/\ 
\______/
 _/  _\_/
""",  # noqa
r"""
 --- -
 __|___
/_|    \____/\
| News |___/ /
\______/
 _/  _\_/
""",  # noqa
r"""
 ----
 __|___
/_|    \____ \
| News |___/\/
\______/
 _/  _\_/
""")  # noqa


class JellyFish(Bitmap):
    random_movement = True
    color = 'magenta'
    frames_per_bitmap = 5
    bitmaps = (r"""
 __--__
/ -  - \
|______|
/ \ /| \
| / |/  \
\ |//   |
/ \||   \
""",  # noqar
r"""
 __--__
/  - - \
|______|
/ \ /| \
| |/ / |
\ \\ | \
 \|/ \  \
""",  # noqa
r"""
 __--__
/   -- \
|______|
/ \ || \
| | /\ |
\ \ || \
/  \\\ |
""",  # noqa
r"""
 __--__
/    - \
|______|
/ \ /| |
| |/ / |
| \|/ /
/ /|| |
""",  # noqa
r"""
 __--__
/ -  - \
|______|
/ \ /| |
| | |/ |
| \//  \
/ /\|   \
""")  # noqa


class Wormhole(Line3D):
    color = 'cyan'
    rotate_axes = (0, 0, 1)
    points = [
        # O
        (-3, -1, 0),
        (-1, -3, 0),
        (1, -3, 0),
        (3, -1, 0),
        (3, 1, 0),
        (1, 3, 0),
        (-1, 3, 0),
        (-3, 1, 0),
        (-3, -1, 0),

        # X
        (-1, -1, 0),
        (1, 1, 0),
        (0, 0, 0),
        (-1, 1, 0),
        (1, -1, 0)
    ]

    def render(self, screen: Screen):
        super().render(screen)

        if self.player and len(self.coords & self.player.coords) > 10:
            self.scene.next()


class Spinner(Object3D):
    def __init__(self, *args, size=5, explode_on_impact=False, rotate_axes=(0, 0, 1, 7),
                 random_movement=True, random_start=True, **kwargs):
        super().__init__(*args, points=[(size, size, 0)], size=size, rotate_axes=rotate_axes,
                         random_movement=random_movement, random_start=random_start, **kwargs)
        self.explode_on_impact = explode_on_impact

    def render(self, screen: Screen):
        super().render(screen)

        if self.explode_on_impact and self.player and self.coords & self.player.coords:
            x, y = list(self.coords)[0]
            explosion = Explosion(x, y)
            if self.parent:
                self.parent.add_kid(explosion)
            screen.add(explosion)
            self.remove()


class Landscape(ObjectMap, KeyListener):
    move_speed = 0
    object_map = {
        'S': Sun,
        'T': Tree,
        'R': Rock,
        'V': Volcano
    }

    def left_pressed(self):
        if not self.player or self.player.can_move_x(x_delta=-1):
            self.x += self.move_speed

    def right_pressed(self):
        if not self.player or self.player.can_move_x(x_delta=1):
            self.x -= self.move_speed
