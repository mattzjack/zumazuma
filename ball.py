import pygame, math

class Ball(pygame.sprite.Sprite):
    SPEED = 50

    @staticmethod
    def load_images():
        Ball.images = list()
        for filename in ['red', 'blue', 'green', 'purple']:
            img = pygame.image.load('./imgs/%s.png' % filename).convert_alpha()
            w = h = 50
            scaled_img = pygame.transform.scale(img, (w, h))
            Ball.images.append(scaled_img)

    def __init__(self, owner, index, color, game_width, game_height):
        super().__init__()

        self.owner = owner
        self.index = index
        self.color = color
        self.game_width = game_width
        self.game_height = game_height

        self.image = Ball.images[color]
        self.w, self.h = self.image.get_size()
        self.r = max(self.w, self.h) / 2
        self.update_pos()
        self.update_coords()
        self.is_bound = True
        self.update_rect()
        self.angle = 0
        self.pos_speed = self.owner.pos_speed
        self.was_colliding = False

    def move(self):
        if self.is_bound:
            self.update_pos()
            self.update_coords()
            self.update_rect()
        else:
            if (self.cy < -self.r or self.cy > self.game_height + self.r or
                self.cx < -self.r or self.cx > self.game_width + self.r):
                self.is_bound = True
                self.owner = self.owner.stranger
                self.index = len(self.owner.ball_group)
                self.kill()
                self.owner.ball_group.add(self)
                return
            vx = Ball.SPEED * math.cos(self.angle)
            vy = -Ball.SPEED * math.sin(self.angle)
            self.cx += vx
            self.cy += vy
            self.update_rect()

    def update_pos(self):
        self.pos = int(self.owner.pos - max(self.owner.w, self.owner.h) / 2 - (self.index - .5) * 2 * self.r)

    def update_coords(self):
        if self.index == 0:
            self.cx, self.cy = self.owner.cx, self.owner.cy
        else:
            if self.pos >= 0:
                self.cx, self.cy = self.owner.path[self.pos]
            else:
                self.cx, self.cy = -50, -50

    def update_rect(self):
        self.x0 = self.cx - self.w / 2
        self.y0 = self.cy - self.h / 2
        self.rect = pygame.Rect(self.x0, self.y0, self.w, self.h)

    def update_ball_list(self):
        self.ball_list = list()
        while len(self.ball_list) < len(self.ball_group):
            found = False
            for ball in self.ball_group:
                if ball.index == len(self.ball_list):
                    found = True
                    self.ball_list.append(ball.color)
            if not found:
                raise Exception('ball with index %d not found' % len(self.ball_list))

    def update(self):
        pass
        # self.update_ball_list()
