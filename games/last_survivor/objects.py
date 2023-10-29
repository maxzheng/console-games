from random import randint, random, choice

from games.screen import Screen
from games.objects import ScreenObject, KeyListener, Zombie, Explosion, Text, Projectile, Monologue


class Player(ScreenObject, KeyListener):
    def __init__(self, name, shape: ScreenObject):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color)

        self.name = name
        self.shape = shape
        self.original_shape = shape
        self.high_score = 0
        self.is_playing = False
        self.char = shape.char
        self.delta_index = 0
        self.gun_ammos_limit = 1000
        self.grenades_limit = 10
        self.deltas = ((0, -1, '|'), (1, -1, '/'), (1, 0, '-'), (1, 1, '\\'), (0, 1, '|'), (-1, 1, '/'),
                       (-1, 0, '-'), (-1, -1, '\\'))

        self.reset()

    @property
    def is_alive(self):
        return self.is_playing

    def reset(self):
        super().reset()
        self.score = 0
        self.shape = self.original_shape
        self.sync(self.shape)
        self.delta_index = 0

        # Machine gun upgrade when score reaches 50
        self.gun_ammos = self.gun_ammos_limit
        self.using_machine_gun = False
        self.enabled_machine_gun = False

        # Grenade upgrade when score reaches 100
        self.grenades = self.grenades_limit
        self.enabled_grenades = False

        if self.screen:
            self.x = self.screen.width / 2
            self.y = self.screen.height / 2
            self.screen.border.status.pop('Machine Gun Ammos', None)
            self.screen.border.status.pop('Grenades', None)

    def render(self, screen: Screen):
        super().render(screen)
        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        self.screen.border.status['killed'] = ('{} (High: {})'.format(
            self.score, self.high_score) if self.score < self.high_score else self.score)

        if (self.screen.renders % 2 == 0 or self.using_machine_gun) and self.is_alive:
            x_delta, y_delta, shape = self.deltas[self.delta_index]
            if self.using_machine_gun:
                x_delta *= 2
                y_delta *= 2
                color = screen.COLOR_YELLOW
            else:
                shape = chr(183)
                color = None
            if not self.using_machine_gun or self.gun_ammos > 0:
                projectile = Projectile(self.x, self.y, shape=shape, parent=self,
                                        x_delta=x_delta, y_delta=y_delta, color=color)

                self.kids.add(projectile)
                self.screen.add(projectile)

        if self.using_machine_gun:
            if self.gun_ammos > 0:
                self.gun_ammos -= 1
            else:
                self.using_machine_gun = False
                screen.add(Monologue(self.x, self.y - 1, texts=['Out of ammo!!!',
                                                                'Weapon has been downgraded.',
                                                                'Wait for reload before upgrading.']))
        elif self.gun_ammos < self.gun_ammos_limit:
            self.gun_ammos += 1

        if self.enabled_grenades:
            if self.grenades < self.grenades_limit and self.screen.renders % 100 == 0:
                self.grenades += 1

        if self.score > 50 and not self.enabled_machine_gun:
            self.enabled_machine_gun = True
            self.using_machine_gun = True
            screen.add(Monologue(self.x, self.y - 1, ['New weapon unlocked: MACHINE GUN!!',
                                                      'It shoots and moves twice as fast,',
                                                      'but watch out as ammos are limited.',
                                                      'Press up/down to switch your weapon']))
            self.gun_ammos = self.gun_ammos_limit

        if self.score > 100 and not self.enabled_grenades:
            self.enabled_grenades = True
            screen.add(Monologue(self.x, self.y - 1, ['New weapon unlocked: GRENADES!!',
                                                      'You got 10 of them.',
                                                      'It explodes on impact.',
                                                      'Press Space to launch a grenade']))
            self.grenades = self.grenades_limit

        if self.enabled_machine_gun:
            screen.border.status['Machine Gun Ammos'] = self.gun_ammos
        if self.enabled_grenades:
            screen.border.status['Grenades'] = self.grenades
            if self.grenades:
                self.color = screen.COLOR_RAINBOW
            else:
                self.color = None

    def got_zombified(self):
        self.is_playing = False

        self.screen.add(Explosion(self.x, self.y, size=30,
                                  on_finish=self.controller.reset_scene))
        zombie = Zombie(self.shape.x, self.shape.y, color=self.screen.COLOR_GREEN)
        self.screen.replace(self.shape, zombie)
        self.shape = zombie
        self.screen.add(Text(self.screen.width / 2, self.screen.height / 2, 'You got ZOMBIFIED!!', is_centered=True))

        # These get sync'ed to `zombie` in render()
        self.y_delta = -0.1
        self.size = zombie.size
        self.color = self.screen.COLOR_GREEN

    def left_pressed(self):
        if self.is_alive:
            if self.delta_index > 0:
                self.delta_index -= 1
            else:
                self.delta_index = len(self.deltas) - 1

    def right_pressed(self):
        if self.is_alive:
            if self.delta_index < len(self.deltas) - 1:
                self.delta_index += 1
            else:
                self.delta_index = 0

    def up_pressed(self):
        if self.enabled_machine_gun:
            self.using_machine_gun = True

    def down_pressed(self):
        self.using_machine_gun = False

    def space_pressed(self):
        if self.enabled_grenades and self.grenades > 0 and self.is_alive:
            self.grenades -= 1
            x_delta, y_delta, shape = self.deltas[self.delta_index]
            explosion = Explosion(self.x, self.y, size=max(self.screen.width, self.screen.height),
                                  parent=self)
            projectile = Projectile(self.x, self.y, shape='@', parent=self,
                                    x_delta=x_delta, y_delta=y_delta, color=self.color,
                                    explode_after_renders=10,
                                    explosion=explosion, explosions=5)
            self.kids.add(projectile)
            self.screen.add(projectile)


class Boss(ScreenObject):
    def __init__(self, name, shape: ScreenObject, player: Player = None, hp=5):
        super().__init__(shape.x, shape.y, size=shape.size, color=shape.color)
        self.shape = shape
        self.player = player
        self.size = 5
        self.y = -5
        self.y_delta = 0.1
        self.x_delta = max(random() * 0.5, 0.2)
        self.is_hit = False
        self.char = shape.char
        self.hp = hp

    def render(self, screen: Screen):
        super().render(screen)
        self.shape.sync(self)
        self.shape.render(screen)
        self.coords = self.shape.coords

        if not self.color:
            self.color = self.screen.COLOR_GREEN

        if self in screen:
            for projectile in self.kids:
                if projectile.coords & self.player.coords:
                    self.player.got_zombified()

        if self in self.screen:
            # self.screen.border.status['boss'] = str((int(self.x), int(self.y), self.size))
            if self.x > self.player.x:
                self.x_delta = -1 * abs(self.x_delta)
            else:
                self.x_delta = abs(self.x_delta)

            if self.y > self.screen.height + 2.5 and self.player.is_alive:
                self.y = -2.5

            if self.is_hit:
                self.color = self.screen.colors[self.screen.renders % len(self.screen.colors)]
                self.is_hit = False

            # else:
            #   self.screen.border.status['boss'] = 'Dead'


class Enemies(ScreenObject):
    def __init__(self, max_enemies=5, player=None):
        super().__init__(0, 0)
        self.max_enemies = max_enemies
        self.enemies = set()
        self.player = player
        self.boss = None

    def render(self, screen: Screen):
        super().render(screen)

        # Create enemies
        if len(self.enemies) < self.max_enemies + int(self.player.score / 100):
            if random() < 0.5:
                x = choice([0, screen.width])
                y = randint(0, screen.height)
            else:
                y = choice([0, screen.height])
                x = randint(0, screen.width)

            speed = random() * self.player.score / 200 + 0.2
            x_sign = 1 if x < self.player.x else -1
            y_sign = 1 if y < self.player.y else -1
            enemy = Zombie(x, y, x_delta=x_sign * speed, y_delta=y_sign * speed)
            self.enemies.add(enemy)
            self.screen.add(enemy)

        for enemy in list(self.enemies):
            # Make them go fast when player got zombified
            if not self.player.is_alive:
                enemy.y_delta *= 1.2
                enemy.x_delta *= 1.2

            # Add boss every 50 killed
            if self.player.score and self.player.score % 50 == 0 and self.boss not in screen and self.player.is_alive:
                self.boss = Boss('Max',
                                 Zombie(randint(5, screen.width - 5), -5,
                                        y_delta=0.1, color=screen.COLOR_GREEN),
                                 player=self.player,
                                 hp=self.player.score/5)
                self.enemies.add(self.boss)
                screen.add(self.boss)

            # If it is out of the screen, remove it (except for boss or player has been zombified)
            if enemy.is_out and (enemy != self.boss and self.player.is_alive):
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
                        self.screen.remove(enemy)

                        self.player.kids.remove(projectile)
                        self.screen.remove(projectile)

                        explosion_size = 25 if enemy == self.boss else enemy.size * 3
                        explosion = Explosion(enemy.x, enemy.y, size=explosion_size)
                        self.screen.add(explosion)

                        if hasattr(projectile, 'explode'):
                            projectile.explode()

                        self.player.score += 5 if enemy == self.boss else 1
                        if self.player.score > self.player.high_score:
                            self.player.high_score = self.player.score

                        break
                else:
                    if enemy.coords & self.player.coords:
                        self.player.got_zombified()
