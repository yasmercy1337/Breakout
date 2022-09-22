from __future__ import annotations
from tkinter import *
from itertools import product
from math import cos, sin, atan
from time import perf_counter

""" TODO

Ball slows down over time
Accelerates on collision (?)
fix wall clipping
Add player controlled platform
"""


class Square:
    WIDTH = 100
    HEIGHT = 50
    GRID_THICKNESS = 3

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.id = 0

    def create(self, canvas: Canvas):
        w = Square.WIDTH
        h = Square.HEIGHT
        x = self.x
        y = self.y
        self.id = canvas.create_rectangle(x, y, x + w, y + h, width=Square.GRID_THICKNESS)
        return self

    def collision(self, ball: Ball) -> tuple[bool, int]:
        cx = self.x + Square.WIDTH / 2
        cy = self.y + Square.HEIGHT / 2
        angle = atan((ball.y - cy) / (ball.x - cx))

        bx = ball.x + cos(angle) * ball.RADIUS
        by = ball.y + sin(angle) * ball.RADIUS

        collided = abs(bx - cx) < Square.WIDTH and abs(by - cy) < Square.HEIGHT
        if collided:
            # 1 for vertical collision, 0 for horizontal
            return collided, int(abs(bx - cx) > Square.WIDTH)
        return False, -1

    def clear(self, canvas: Canvas):
        canvas.delete(self.id)


class Ball:
    RADIUS = 25
    SPEED = 10
    FRAME_INTERVAL = 25

    def __init__(self, x: int, y: int, angle: float = -1.0):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = angle
        self.id = 0

        self.vx = cos(angle) * Ball.SPEED
        self.vy = sin(angle) * Ball.SPEED

    def update_position(self, canvas: Canvas):
        self.x += self.vx
        self.y += self.vy
        canvas.move(self.id, self.vx, self.vy)

    def horizontal_collision(self):
        self.vy *= -1

    def vertical_collision(self):
        self.vx *= -1

    def draw(self, canvas: Canvas):
        r = Ball.RADIUS
        x, y = self.x, self.y
        self.id = canvas.create_oval(x - r, y - r, x + r, y + r)
        return self

    def display(self, canvas: Canvas):
        self.update_position(canvas)


class Platform:
    WIDTH = 250
    HEIGHT = 20
    MAX_TRAVEl = 1

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.id = 0

    def draw(self, canvas):
        x, y = self.x, self.y
        self.id = canvas.create_rectangle(x, y, x + Platform.WIDTH, y + Platform.HEIGHT)
        return self

    def update(self, canvas, mouseX, left, right):
        dx = min(mouseX - self.x, Platform.MAX_TRAVEl)
        if left < self.x + dx < right:
            self.x += dx
            canvas.move(self.id, dx, 0)

    def collision(self, ball: Ball) -> bool:
        bx, by = ball.x, ball.y + Ball.RADIUS
        cx, cy = self.x + Platform.WIDTH / 2, self.y + Platform.HEIGHT

        return abs(bx - cx) < (Platform.WIDTH / 2) and abs(by - cy) < (Platform.HEIGHT / 2)


class Breakout(Tk):
    INITIAL_OPEN_HEIGHT = 500
    MARGINS = 100
    BORDER_THICKNESS = 5

    def __init__(self, rows: int = 2, cols: int = 10):
        super().__init__()

        # setup instance variables
        self.width = cols * Square.WIDTH + 2 * Breakout.MARGINS
        self.height = rows * Square.HEIGHT * 2 + Breakout.INITIAL_OPEN_HEIGHT + 2 * Breakout.MARGINS
        self.rows = rows
        self.cols = cols
        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()

        # self.geometry(f"{self.width}x{self.height}")
        self.draw_borders()
        self.squares = self.create_squares()
        self.ball = Ball(self.width // 2, self.height // 2).draw(self.canvas)
        self.platform = Platform(300, self.height - Breakout.MARGINS - 50).draw(self.canvas)

        self.bind("<Motion>", self.mouseMove)

    def draw_borders(self) -> None:
        margin = self.MARGINS
        width = self.width
        height = self.height

        self.canvas.create_line(margin, margin, width - margin, margin, width=Breakout.BORDER_THICKNESS)
        self.canvas.create_line(margin, margin, margin, height - margin, width=Breakout.BORDER_THICKNESS)
        self.canvas.create_line(width - margin, margin, width - margin, height - margin,
                                width=Breakout.BORDER_THICKNESS)
        self.canvas.create_line(margin, height - margin, width - margin, height - margin,
                                width=Breakout.BORDER_THICKNESS)

    def create_squares(self) -> list[Square]:
        out = []
        for (r, c) in product(range(self.rows), range(self.cols)):
            x = c * Square.WIDTH + Breakout.MARGINS
            y = r * Square.HEIGHT + Breakout.MARGINS
            out.append(Square(x, y).create(self.canvas))

        return out

    def platform_collision(self):
        if self.platform.collision(self.ball):
            self.ball.horizontal_collision()

    def square_collision(self):
        for index, square in enumerate(self.squares):
            collided, value = square.collision(self.ball)
            if not collided:
                continue
            square.clear(self.canvas)
            self.squares.pop(index)
            [self.ball.horizontal_collision, self.ball.vertical_collision][value]()
            break

    def border_collision(self):
        ball = self.ball
        radius = Ball.RADIUS

        r, l, b, t = self.ball.x + radius, self.ball.x - radius, self.ball.y + radius, self.ball.y - radius

        if l < self.MARGINS or r + self.MARGINS > self.width:
            ball.vertical_collision()
        elif t < self.MARGINS or b + self.MARGINS > self.height:
            ball.horizontal_collision()

    def collisions(self):
        self.platform_collision()
        self.square_collision()
        self.border_collision()

    def display(self):
        try:
            last_tick = perf_counter()
            while self.state():
                # print(perf_counter() - last_tick)
                self.update()
                self.update_idletasks()

                cur_time = perf_counter()
                if cur_time - last_tick > Ball.FRAME_INTERVAL / 1000:
                    self.collisions()
                    self.ball.display(self.canvas)
                    last_tick = cur_time

        except TclError:
            pass

    def mouseMove(self, event):
        self.platform.update(self.canvas, event.x, self.MARGINS, self.width - self.MARGINS - Platform.WIDTH)
