from games.controller import Controller
from games.objects import Square, Circle, Projectile


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        self.square = Square(self.screen.width / 2, self.screen.height - 2, size=3)
        self.projectile = 'o'
        self.player = Circle(self.screen.width / 2, self.screen.height - 3, size=3, color=self.screen.COLOR_RED)
        self.screen.add(self.player)

    def left_pressed(self):
        if self.player.x > 3:
            self.player.x -= 1

    def right_pressed(self):
        if self.player.x < self.screen.width - 2:
            self.player.x += 1

    def up_pressed(self):
        if self.player.y > 2:
            self.player.y -= 1

    def down_pressed(self):
        if self.player.y < self.screen.height - 3:
            self.player.y += 1

    def space_pressed(self):
        self.screen.add(Projectile(self.player.x, self.player.y, shape=self.projectile))

    def escape_pressed(self):
        exit()
