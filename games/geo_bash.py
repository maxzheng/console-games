from random import randint, random

from games.controller import Controller
from games.objects import (Square, Circle, Projectile, Explosion, Text, Monologue, Triangle,
                           Diamond, Choice, Bar)


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        def bash():
            self.start = True

        def intro():
            self.start = False
            self.intro = Monologue(self.player.x, self.player.y - 2, on_finish=bash,
                                   texts=["Hi, I am {}!".format(self.player.name),
                                          "Most people don't like geometry, but not me.",
                                          "I LOVE to bash them!! :D",
                                          "Move me using arrow keys.",
                                          "Ready? Let's BASH!!"])
            self.screen.add(self.intro)

        self.intro = None
        self.max_enemies = 5
        self.player_choices = [
            Triangle(self.screen.width / 2, self.screen.height - 3, size=3,
                     color=self.screen.COLOR_BLUE, name='Kate'),
            Circle(self.screen.width / 2, self.screen.height - 3, size=3,
                   color=self.screen.COLOR_RED, name='Nina'),
            Diamond(self.screen.width / 2, self.screen.height - 3, size=3,
                    color=self.screen.COLOR_YELLOW, name='Jon')
        ]
        for player in self.player_choices:  # Hack it until you make it
            player.high_score = 0
        self.player_choice = Choice(self.screen.width / 2, self.screen.height / 2,
                                    choices=self.player_choices, color=self.screen.COLOR_CYAN,
                                    on_select=intro)
        self.boss = Square(self.screen.width / 2, -5, size=5,
                           color=self.screen.COLOR_GREEN, name='Max', y_delta=0.1, solid=True)
        self.player = None

        self.reset()

        # After reset actions
        self.screen.add(self.player_choice)

    def reset(self):
        self.boss.size = 5
        self.boss.y_delta = 0.1
        self.boss.kids = set()
        self.boss.is_hit = False
        self.enemies = set()
        self.screen.reset()
        self.score = 0
        self.start = True

        if self.player:
            self.screen.add(self.player)
            self.player.is_visible = True

    def process(self):
        super().process()

        if self.boss in self.screen.objects:
            for projectile in self.boss.kids:
                if projectile.coords & self.player.coords:
                    self.player.is_visible = False
                    self.screen.add(Explosion(self.player.x, self.player.y, size=20,
                                              on_finish=lambda: self.reset()))
                    self.screen.add(Text((self.screen.width - 10) / 2,
                                         self.screen.height / 2, 'You got BASHED!!'))

        for enemy in list(self.enemies):
            if not self.player.is_visible:
                enemy.y_delta += 0.5

            if enemy.is_out and (enemy != self.boss or self.player.is_visible):
                self.enemies.remove(enemy)
                self.screen.remove(enemy)
            else:
                for projectile in list(self.player.kids):
                    if projectile.coords & enemy.coords:
                        if enemy == self.boss and self.boss.size > 2.05:
                            self.boss.size -= 0.05
                            self.boss.is_hit = True
                            break

                        self.enemies.remove(enemy)
                        self.screen.remove(enemy)

                        self.player.kids.remove(projectile)
                        self.screen.remove(projectile)

                        explosion_size = 25 if enemy == self.boss else enemy.size * 3
                        self.screen.add(Explosion(enemy.x, enemy.y, size=explosion_size))

                        self.score += 5 if enemy == self.boss else 1
                        if self.score > self.player.high_score:
                            self.player.high_score = self.score

                        break
                else:
                    if enemy.coords & self.player.coords:
                        self.player.is_visible = False
                        self.screen.add(Explosion(self.player.x, self.player.y, size=20,
                                                  on_finish=lambda: self.reset()))
                        self.screen.add(Text((self.screen.width - 10) / 2,
                                             self.screen.height / 2, 'You got BASHED!!'))

        if self.start and self.player and self.player.is_visible:
            if self.boss in self.screen.objects:
                # self.screen.border.status['boss'] = str((int(self.boss.x), int(self.boss.y), self.boss.size))
                if self.boss.x > self.player.x:
                    self.boss.x_delta = -1 * abs(self.boss.x_delta)
                else:
                    self.boss.x_delta = abs(self.boss.x_delta)
                if self.boss.y > self.screen.height + 2.5:
                    self.boss.y = -2.5

                if self.boss.is_hit:
                    self.boss.color = self.screen.colors[self.screen.renders % len(self.screen.colors)]
                    if self.screen.renders % 10 == 0:
                        if self.boss.size >= 4:
                            self.boss.color = self.screen.COLOR_GREEN
                        elif self.boss.size >= 3:
                            self.boss.color = self.screen.COLOR_YELLOW
                        else:
                            self.boss.color = self.screen.COLOR_RED
                        self.boss.is_hit = False

            # else:
            #    self.screen.border.status['boss'] = 'Dead'

            if self.score and self.score % 50 == 0 and self.boss not in self.screen.objects:
                self.boss.x = randint(5, self.screen.width - 5)
                self.boss.y = -5
                self.boss.x_delta = max(random() * 0.7, 0.3)
                self.boss.char = '$'
                self.boss.size = 5
                self.boss.kids = set()
                self.boss.is_hit = False
                self.boss.color = self.screen.COLOR_GREEN

                self.enemies.add(self.boss)
                self.screen.add(self.boss)

            if len(self.enemies) < self.max_enemies:
                enemy = Square(randint(3, self.screen.width-3), -3, size=randint(2, 4),
                               y_delta=random() * self.score / 200 + 0.2)
                self.enemies.add(enemy)
                self.screen.add(enemy)

            if self.screen.renders % 2 == 0:
                if self.player.char == '!':
                    color = self.screen.colors[int(self.screen.renders / 2) % len(self.screen.colors)]
                else:
                    color = self.player.color

                projectile = Projectile(self.player.x, self.player.y-1, shape=self.player.char,
                                        parent=self.player, color=color)
                self.player.kids.add(projectile)
                self.screen.add(projectile)

                if self.screen.renders % 30 == 0 and self.boss in self.screen.objects:
                    projectile = Bar(self.boss.x, self.boss.y+self.boss.size/2, size=self.boss.size,
                                     parent=self.boss, color=self.boss.color, y_delta=0.5,
                                     char=self.boss.char)
                    self.boss.kids.add(projectile)
                    self.screen.add(projectile)

        player = self.player or self.player_choices[self.player_choice.current_choice]
        self.screen.border.status['bashed'] = ('{} (High: {})'.format(
            self.score, player.high_score) if self.score < player.high_score else self.score)

    def key_pressed(self, key):
        if self.player and self.intro in self.screen.objects:
            self.start = True
            self.screen.remove(self.intro)

    def left_pressed(self):
        if self.player:
            if self.player.x > 3:
                self.player.x -= 2

        else:
            if self.player_choice.current_choice > 0:
                self.player_choice.current_choice -= 1
                self.player_choice.bar.x -= self.player_choice.bar.size

    def right_pressed(self):
        if self.player:
            if self.player.x < self.screen.width - 2:
                self.player.x += 2

        else:
            if self.player_choice.current_choice < len(self.player_choice.choices) - 1:
                self.player_choice.current_choice += 1
                self.player_choice.bar.x += self.player_choice.bar.size

    def up_pressed(self):
        if self.player:
            if self.player.y > 2:
                self.player.y -= 1

    def down_pressed(self):
        if self.player:
            if self.player.y < self.screen.height - 3:
                self.player.y += 1

    def space_pressed(self):
        self.enter_pressed()

    def enter_pressed(self):
        if not self.player:
            self.player = self.player_choice.choices[self.player_choice.current_choice]
            self.player.x = self.screen.width / 2
            self.player.y = self.screen.height - self.player.size
            self.screen.add(self.player)
            self.screen.remove(self.player_choice)
            if self.player_choice.on_select:
                self.player_choice.on_select()

    def escape_pressed(self):
        if self.player:
            self.player.is_visible = True
            self.player = None
            self.reset()
            self.player_choice.bar = None
            self.screen.add(self.player_choice)
        else:
            exit()
