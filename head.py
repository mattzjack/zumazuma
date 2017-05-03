import pygame, math, random

from ball import Ball

class Head(pygame.sprite.Sprite):
    @staticmethod
    def load_images():
        # image from roblox
        Head.images = list()
        for i in '01':
            img = pygame.image.load('./imgs/frog%s.png' % i).convert_alpha()
            w = h = 100
            scaled_img = pygame.transform.scale(img, (w, h))
            Head.images.append(scaled_img)

    def __init__(self, index, path, game_width, game_height, stranger):
        super().__init__()
        self.path = path
        self.index = index
        self.game_width = game_width
        self.game_height = game_height
        self.stranger = stranger
        self.pos = 0
        self.cx, self.cy = path[self.pos]
        self.base_image = Head.images[self.index]
        self.image = self.base_image.copy()
        self.w, self.h = self.image.get_size()
        self.update_rect()
        self.angle = -math.pi / 2
        self.pos_speed = 1
        self.ball_group = pygame.sprite.Group()
        self.num_balls = 15
        self.ball_list = list()
        for i in range(self.num_balls):
            ball_color = random.randint(0, 3)
            self.ball_list.append(ball_color)
        self.update_ball_group(self.ball_list)

    def update_rect(self):
        self.x0 = self.cx - self.w / 2
        self.y0 = self.cy - self.h / 2
        self.rect = pygame.Rect(self.x0, self.y0, self.w, self.h)

    def move(self):
        self.pos += self.pos_speed
        self.cx, self.cy = self.path[self.pos]
        self.update_rect()

    def rotate(self, pos):
        x1, y1 = pos
        dx = x1 - self.cx
        dy = self.cy - y1
        self.angle = math.atan2(dy, dx)
        degs = self.angle * 180 / math.pi + 90
        rotated_img = pygame.transform.rotate(self.base_image, degs)
        rw, rh = rotated_img.get_size()
        # UnkwnTech
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA, 32)
        self.image.blit(rotated_img, (0, 0), ((rw - self.w) / 2, (rh - self.h) / 2, self.w, self.h))
        self.w, self.h = self.image.get_size()
        self.x0 = self.cx - self.w / 2
        self.y0 = self.cy - self.h / 2
        self.rect = pygame.Rect(self.x0, self.y0, self.w, self.h)

    def shoot(self, pos, dest_group):
        if len(self.ball_group) > 0:
            for ball in self.ball_group:
                if ball.index == 0:
                    ball.is_bound = False
                    ball.angle = self.angle
                    dest_group.add(ball)
                    self.ball_group.remove(ball)
                else:
                    ball.index -= 1
                    ball.update_pos()
                    ball.update_coords()
                    ball.update_rect()

    def update_ball_group(self, L):
        self.ball_list = L.copy()
        N = len(self.ball_list)
        self.ball_group.empty()
        for i in range(N):
            this_color = self.ball_list[i]
            self.ball_group.add(Ball(self, i, this_color, self.game_width, self.game_height))

    def update_ball_list(self):
        self.ball_list = list()
        while len(self.ball_list) < len(self.ball_group):
            target = len(self.ball_list)
            for ball in self.ball_group:
                if ball.index == target:
                    self.ball_list.append(ball.color)

    def update(self):
        self.update_ball_list()
