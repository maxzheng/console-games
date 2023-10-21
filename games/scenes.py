from games.objects import (Square, Circle, Projectile, Explosion, Text, Monologue, Triangle,
                           Diamond, Choice, Bar, Player, KeyListener)


class Scene(KeyListener):
    def __init__(self, screen, controller):
        self.screen = screen
        self.controller = controller
        self.init()

    def init(self):
        """ Initialize the scene """

    def start(self):
        """ Start the scene """

    def next(self):
        self.done = True

    def reset(self):
        self.done = False


class ChoosePlayer(Scene):
    def init(self):
        choices = [
            Player('Kate', Triangle(self.screen.width / 2, self.screen.height - 3, size=3,
                                    color=self.screen.COLOR_BLUE),
            Player('Nina', Circle(self.screen.width / 2, self.screen.height - 3, size=3,
                                  color=self.screen.COLOR_RED),
            Player('Jon', Diamond(self.screen.width / 2, self.screen.height - 3, size=3,
                                  color=self.screen.COLOR_YELLOW)
        ]
        self.choice = Choice(self.screen.width / 2, self.screen.height / 2,
                             choices=choices, color=self.screen.COLOR_CYAN,
                             on_select=self.next)

    def start(self):
        self.screen.add(self.choice)

    def next(self, chosen: Player):
        super().next()
        self.controller.player = chosen

    def reset(self):
        super().reset()
        self.choice.reset()


class Intro(Scene):
    def init(self):
        self.intro = Monologue(self.controller.player.x, self.controller.player.y - 2,
                               on_finish=self.next,
                               texts=["Hi, I am {}!".format(self.controller.player.name),
                                      "Most people don't like geometry, but not me.",
                                      "I LOVE to bash them!! :D",
                                      "Move me using arrow keys.",
                                      "Ready? Let's BASH!!"])

    def start(self):
        self.screen.add(intro, self.controller.player)


class Bash(Scene):
    def init(self):
        self.max_enemies = 5
        self.boss = Boss('Max', Square(self.screen.width / 2, -5, size=5,
                                       color=self.screen.COLOR_GREEN, y_delta=0.1, solid=True))
    def start(self):
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

    def play(self):
        super().play()
        if self.boss in self.screen:
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
            if self.boss in self.screen:
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

            if self.score and self.score % 50 == 0 and self.boss not in self.screen:
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

                if self.screen.renders % 30 == 0 and self.boss in self.screen:
                    projectile = Bar(self.boss.x, self.boss.y+self.boss.size/2, size=self.boss.size,
                                     parent=self.boss, color=self.boss.color, y_delta=0.5,
                                     char=self.boss.char)
                    self.boss.kids.add(projectile)
                    self.screen.add(projectile)

        player = self.player or self.player_choices[self.player_choice.current_choice]
        self.screen.border.status['bashed'] = ('{} (High: {})'.format(
            self.score, player.high_score) if self.score < player.high_score else self.score)

    def key_pressed(self, key):
        if self.player and self.intro in self.screen:
            self.start = True
            self.screen.remove(self.intro)

    def left_pressed(self):
        if self.player:
            if self.player.x > 3:
                self.player.x -= 2


    def right_pressed(self):
        if self.player:
            if self.player.x < self.screen.width - 2:
                self.player.x += 2


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

    def escape_pressed(self):
        if self.player:
            self.player.is_visible = True
            self.player = None
            self.reset()
            self.screen.add(self.player_choice)
        else:
            exit()
