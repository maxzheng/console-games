from games.controller import Controller
from games.objects import Square, Projectile


class GeoBash(Controller):
    name = "Geometry Bash"

    def init(self):
        self.square = Square(self.screen.width / 2, self.screen.height - 2, size=3)
        self.screen.add(self.square)

    def left_pressed(self):
        if self.square.x > 3:
            self.square.x -= 1

    def right_pressed(self):
        if self.square.x < self.screen.width - 2:
            self.square.x += 1

    def up_pressed(self):
        if self.square.y > 2:
            self.square.y -= 1

    def down_pressed(self):
        if self.square.y < self.screen.height - 2:
            self.square.y += 1

    def space_pressed(self):
        self.screen.add(Projectile(self.square.x, self.square.y, shape='#'))

    def escape_pressed(self):
        exit()
