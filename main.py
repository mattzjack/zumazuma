import pygame, math, random, numbers, socket
from _thread import *
from queue import Queue

class Ball(pygame.sprite.Sprite):
    SPEED = 20

    @staticmethod
    def load_images():
        Ball.images = list()
        for filename in ['red', 'blue', 'green']:
            img = pygame.image.load('./imgs/%s.png' % filename).convert_alpha()
            w = h = 50
            scaled_img = pygame.transform.scale(img, (w, h))
            Ball.images.append(scaled_img)

    def __init__(self, owner, index):
        super().__init__()
        self.owner = owner
        self.image = random.choice(Ball.images)
        self.w, self.h = self.image.get_size()
        self.index = index
        if self.index == 0:
            self.cx = self.owner.cx
        else:
            self.cx = self.owner.cx - self.owner.w / 2 - (self.index - .5) * self.w
        self.cy = self.owner.cy
        self.is_bound = True
        self.x0 = self.cx - self.w / 2
        self.y0 = self.cy - self.h / 2
        self.rect = pygame.Rect(self.x0, self.y0, self.w, self.h)
        self.angle = 0

    def move(self):
        if self.is_bound:
            pass
        else:
            vx = Ball.SPEED * math.cos(self.angle)
            vy = -Ball.SPEED * math.sin(self.angle)
            self.cx += vx
            self.cy += vy
            self.update_rect()

    def update_rect(self):
        self.x0 = self.cx - self.w / 2
        self.y0 = self.cy - self.h / 2
        self.rect = pygame.Rect(self.x0, self.y0, self.w, self.h)

class Head(pygame.sprite.Sprite):
    @staticmethod
    def load_images():
        Head.images = list()
        for i in '01':
            img = pygame.image.load('./imgs/frog%s.png' % i).convert_alpha()
            w = h = 100
            scaled_img = pygame.transform.scale(img, (w, h))
            Head.images.append(scaled_img)

    def __init__(self, index, cx, cy):
        super().__init__()
        self.index = index
        self.base_image = Head.images[self.index]
        self.image = self.base_image.copy()
        self.cx = cx
        self.cy = cy
        self.w, self.h = self.image.get_size()
        self.x0 = self.cx - self.w / 2
        self.y0 = self.cy - self.h / 2
        self.rect = pygame.Rect(self.x0, self.y0, self.w, self.h)
        self.angle = -math.pi / 2
        self.ball_group = pygame.sprite.Group()
        self.num_balls = 10
        for i in range(self.num_balls):
            self.ball_group.add(Ball(self, i))

    def rotate(self, pos):
        x1, y1 = pos
        dx = x1 - self.cx
        dy = self.cy - y1
        self.angle = math.atan2(dy, dx)
        degs = self.angle * 180 / math.pi + 90
        self.image = pygame.transform.rotate(self.base_image, degs)
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
                    if ball.index == 0:
                        ball.cx = ball.owner.cx
                    else:
                        ball.cx = ball.owner.cx - ball.owner.w / 2 - (ball.index - .5) * ball.w
                    ball.x0 = ball.cx - ball.w / 2
                    ball.y0 = ball.cy - ball.h / 2
                    ball.rect = pygame.Rect(ball.x0, ball.y0, ball.w, ball.h)

class Game(object):
    def __init__(self):
        pygame.init()
        self.width = 400
        self.height = 300
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        Head.load_images()
        Ball.load_images()

        self.GAME_SPLASH = 'game'

        self.FPS = 50
        self.is_playing = True

        self.head_group = pygame.sprite.Group()

        self.splash = self.GAME_SPLASH
        self.id = None

        self.free_ball_group = pygame.sprite.Group()

    def game_mouse_motion(self, pos, rel, buttons):
        self.my_head.rotate(pos)
        msg = (('moved' + ' %d' * 7 + '\n') %
        (pos[0], pos[1], rel[0], rel[1], buttons[0], buttons[1], buttons[2]))
        print('sending msg to server:', repr(msg))
        server.send(msg.encode())

    def mouse_motion(self, pos, rel, buttons):
        if self.splash == self.GAME_SPLASH:
            self.game_mouse_motion(pos, rel, buttons)

    def game_mouse_button_down(self, pos, button):
        if button == 1:
            self.my_head.shoot(pos, self.free_ball_group)
            msg = 'clicked %d %d %d\n' % (pos[0], pos[1], button)
            print('sending msg to server:', repr(msg))
            server.send(msg.encode())

    def mouse_button_down(self, pos, button):
        if self.splash == self.GAME_SPLASH:
            self.game_mouse_button_down(pos, button)

    def timer_fired(self):
        if serverMsg.qsize() > 0:
            msg = serverMsg.get(False)
            print('msg recv:', repr(msg))
            if msg.startswith('id'):
                msg = msg.split()
                self.id = int(msg[1])
                if self.id == 0:
                    self.my_head = Head(self.id, self.width / 3, self.height / 3)
                elif self.id == 1:
                    self.my_head = Head(self.id, self.width * 2 / 3, self.height * 2 / 3)
                self.head_group.add(self.my_head)
            elif msg.startswith('new_player'):
                msg = msg.split()
                self.his_id = int(msg[1])
                if self.his_id == 0:
                    self.his_head = Head(self.his_id, self.width / 3, self.height / 3)
                elif self.his_id == 1:
                    self.his_head = Head(self.his_id, self.width * 2 / 3, self.height * 2 / 3)
                self.head_group.add(self.his_head)
            elif msg.startswith('clicked'):
                msg = msg.split()
                x = int(msg[1])
                y = int(msg[2])
                pos = (x, y)
                button = int(msg[3])
                if button == 1:
                    self.his_head.shoot(pos, self.free_ball_group)
            elif msg.startswith('moved'):
                msg = msg.split()
                posx = int(msg[1])
                posy = int(msg[2])
                pos = (posx, posy)
                relx = int(msg[3])
                rely = int(msg[4])
                rel = (relx, rely)
                button1 = int(msg[5])
                button2 = int(msg[6])
                button3 = int(msg[7])
                buttons = (button1, button2, button3)
                self.his_head.rotate(pos)
            serverMsg.task_done()
        for head in self.head_group:
            for ball in head.ball_group:
                ball.move()
        for ball in self.free_ball_group:
            ball.move()

    def redraw_all(self):
        self.head_group.draw(self.screen)
        for head in self.head_group:
            head.ball_group.draw(self.screen)
        self.free_ball_group.draw(self.screen)

    def run(self):
        while self.is_playing:
            self.clock.tick(self.FPS)
            self.timer_fired()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_playing = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_motion(event.pos, event.rel, event.buttons)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_button_down(event.pos, event.button)
            self.screen.fill((255, 255, 255))
            self.redraw_all()
            pygame.display.flip()
        pygame.quit()

HOST = '128.237.171.233'
PORT = 50014

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))
print("connected to server")

serverMsg = Queue(100)

def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")

start_new_thread(handleServerMsg, (server, serverMsg))

game = Game()
game.run()
