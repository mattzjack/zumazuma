import pygame, math, random, numbers, socket, pickle, time
from _thread import *
from queue import Queue

def ball_collide(ball0, ball1):
    dist = ((ball0.cx - ball1.cx) ** 2 + (ball0.cy - ball1.cy) ** 2) ** .5
    return dist < ball0.r + ball1.r

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

    def __init__(self, owner, index, color):
        super().__init__()
        self.owner = owner
        self.image = Ball.images[color]
        self.color = color
        self.w, self.h = self.image.get_size()
        self.r = max(self.w, self.h) / 2
        self.index = index
        self.update_pos()
        self.update_coords()
        self.is_bound = True
        self.update_rect()
        self.angle = 0
        self.pos_speed = self.owner.pos_speed

    def move(self):
        if self.is_bound:
            self.update_pos()
            self.update_coords()
            self.update_rect()
        else:
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

class Head(pygame.sprite.Sprite):
    @staticmethod
    def load_images():
        Head.images = list()
        for i in '01':
            img = pygame.image.load('./imgs/frog%s.png' % i).convert_alpha()
            w = h = 100
            scaled_img = pygame.transform.scale(img, (w, h))
            Head.images.append(scaled_img)

    def __init__(self, index, path):
        super().__init__()
        self.path = path
        self.index = index
        self.pos = 0
        self.cx, self.cy = path[self.pos]
        self.base_image = Head.images[self.index]
        self.image = self.base_image.copy()
        self.w, self.h = self.image.get_size()
        self.update_rect()
        self.angle = -math.pi / 2
        self.pos_speed = 2
        self.ball_group = pygame.sprite.Group()
        self.num_balls = 10
        self.ball_list = list()
        for i in range(self.num_balls):
            ball_color = random.randint(0, 2)
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
                    ball.update_pos()
                    ball.update_coords()
                    ball.update_rect()

    def update_ball_group(self, L):
        self.ball_list = L.copy()
        N = len(self.ball_list)
        self.ball_group.empty()
        for i in range(N):
            this_color = self.ball_list[i]
            self.ball_group.add(Ball(self, i, this_color))

class Button(pygame.sprite.Sprite):
    def __init__(self, x0, y0, w, h, text, color):
        self.x0 = x0
        self.y0 = y0
        self.w = w
        self.h = h
        self.text = text
        self.color = color

class Path(object):
    def __init__(self, game_width, game_height):
        self.index = -1
        self.p0path = []
        self.p1path = []
        self.game_width = game_width
        self.game_height = game_height

    def load_path0(self):
        # this is a rectangular path
        # player 0 starts at bottom left, goes up, and keeps turning right
        # player 1 starts at top right, goes down, and keeps turning right
        self.index = 0

        # p0: up
        x = self.game_width // 10
        for y in range(self.game_height * 11 // 10, self.game_height // 10, -1):
            self.p0path.append((x, y))
        # p0: right
        y = self.game_height // 10
        for x in range(self.game_width // 10, self.game_width * 4 // 5):
            self.p0path.append((x, y))
        # p0: down
        x = self.game_width * 4 // 5
        for y in range(self.game_height // 10, self.game_height * 4 // 5):
            self.p0path.append((x, y))
        # p0: left
        y = self.game_height * 4 // 5
        for x in range(self.game_width * 4 // 5, self.game_width * 3 // 10, -1):
            self.p0path.append((x, y))
        # p0: up
        x = self.game_width * 3 // 10
        for y in range(self.game_height * 4 // 5, self.game_height // 2, -1):
            self.p0path.append((x, y))
        # p0: right
        y = self.game_height // 2
        for x in range(self.game_width * 3 // 10, self.game_width // 2):
            self.p0path.append((x, y))

        # p1: down
        x = self.game_width * 9 // 10
        for y in range(-self.game_height // 10, self.game_height * 9 // 10):
            self.p1path.append((x, y))
        # p1: left
        y = self.game_height * 9 // 10
        for x in range(self.game_width * 9 // 10, self.game_width // 5, -1):
            self.p1path.append((x, y))
        # p1: up
        x = self.game_width // 5
        for y in range(self.game_height * 9 // 10, self.game_height // 5, -1):
            self.p1path.append((x, y))
        # p1: right
        y = self.game_height // 5
        for x in range(self.game_width // 5, self.game_width * 7 // 10):
            self.p1path.append((x, y))
        # p1: down
        x = self.game_width * 7 // 10
        for y in range(self.game_height // 5, self.game_height // 2):
            self.p1path.append((x, y))
        # p1: left
        y = self.game_height // 2
        for x in range(self.game_width * 7 // 10, self.game_width // 2, -1):
            self.p1path.append((x, y))


class Game(object):
    paths = []

    @staticmethod
    def load_path0(game_width, game_height):
        this_path = Path(game_width, game_height)
        this_path.load_path0()
        Game.paths.append(this_path)

    @staticmethod
    def load_paths(game_width, game_height):
        Game.load_path0(game_width, game_height)

    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        Game.load_paths(self.width, self.height)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        Head.load_images()
        Ball.load_images()

        self.INTRO_SPLASH = 'intro'
        self.GAME_SPLASH = 'game'

        self.FPS = 50
        self.is_playing = True

        self.head_group = pygame.sprite.Group()

        self.splash = self.GAME_SPLASH
        self.id = None

        self.free_ball_group = pygame.sprite.Group()

        self.my_head = self.his_head = None

        self.game_path = random.choice(Game.paths)

        self.can_start = False

    def game_mouse_motion(self, pos, rel, buttons):
        self.my_head.rotate(pos)
        msg = (('moved' + ' %d' * 7 + '\n') %
        (pos[0], pos[1], rel[0], rel[1], buttons[0], buttons[1], buttons[2]))
        if not self.can_start: return
        self.send_msg(msg)

    def mouse_motion(self, pos, rel, buttons):
        if self.splash == self.GAME_SPLASH:
            self.game_mouse_motion(pos, rel, buttons)

    def game_mouse_button_down(self, pos, button):
        if button == 1:
            self.my_head.shoot(pos, self.free_ball_group)
            msg = 'clicked %d %d %d\n' % (pos[0], pos[1], button)
            self.send_msg(msg)

    def mouse_button_down(self, pos, button):
        if self.splash == self.GAME_SPLASH:
            self.game_mouse_button_down(pos, button)

    def send_msg(self, msg):
        server.send(msg.encode())

    def handle_id_msg(self, msg):
        self.id = int(msg[1])
        if self.id == 0:
            self.my_head = Head(self.id, self.game_path.p0path)
        elif self.id == 1:
            self.my_head = Head(self.id, self.game_path.p1path)
        self.head_group.add(self.my_head)
        msg_out = 'balls ' + ' '.join(str(self.my_head.ball_list[i]) for i in range(len(self.my_head.ball_list))) + '\n'
        self.send_msg(msg_out)

    def handle_new_player_msg(self, msg):
        self.his_id = int(msg[1])
        if self.his_id == 0:
            self.his_head = Head(self.his_id, self.game_path.p0path)
        elif self.his_id == 1:
            self.his_head = Head(self.his_id, self.game_path.p1path)
        self.head_group.add(self.his_head)

    def handle_balls_msg(self, msg):
        ball_list = msg[1:]
        for i in range(len(ball_list)):
            ball_list[i] = int(ball_list[i])
        self.his_head.update_ball_group(ball_list)

    def handle_clicked_msg(self, msg):
        x = int(msg[1])
        y = int(msg[2])
        pos = (x, y)
        button = int(msg[3])
        if button == 1:
            self.his_head.shoot(pos, self.free_ball_group)

    def handle_moved_msg(self, msg):
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

    def handle_msg(self):
        if serverMsg.qsize() > 0:
            msg = serverMsg.get(False)
            if msg == '': return
            msg = msg.split()
            if msg[0] == 'start':
                self.can_start = True
            elif msg[0] == 'id':
                self.handle_id_msg(msg)
            elif msg[0] == 'new_player':
                self.handle_new_player_msg(msg)
                msg = 'ready\n\n'
                self.send_msg(msg)
            elif msg[0] == 'balls':
                self.handle_balls_msg(msg)
            elif msg[0] == 'clicked':
                self.handle_clicked_msg(msg)
            elif msg[0] == 'moved':
                self.handle_moved_msg(msg)
            serverMsg.task_done()

    def insert_ball_after_index(self, ball, head, index):
        ball.remove(self.free_ball_group)
        ball.index = index + 1
        ball.owner = head
        ball.is_bound = True
        for other_ball in head.ball_group:
            if other_ball.index > index:
                other_ball.index += 1
        head.ball_group.add(ball)
        for every_ball in head.ball_group:
            every_ball.update_pos()
            every_ball.update_coords()
            every_ball.update_rect()

    def handle_ball_collision(self, head):
        group = head.ball_group
        collided_balls = pygame.sprite.groupcollide(self.free_ball_group,
                                                    group, False, False,
                                                    ball_collide)
        for ball in collided_balls:
            other_balls = collided_balls[ball]
            if len(other_balls) == 2:
                first_ball = other_balls[0]
                second_ball = other_balls[1]
                if abs(first_ball.index - second_ball.index) == 1:
                    if ball.color == first_ball.color == second_ball.color:
                        ball.kill()
                        first_ball.kill()
                        second_ball.kill()
                        for ball in group:
                            if ball.index > second_ball.index:
                                ball.index -= 2
                        for ball in group:
                            ball.update_pos()
                            ball.update_coords()
                            ball.update_rect()
                    else:
                        self.insert_ball_after_index(ball, head, min(first_ball.index, second_ball.index))

    def timer_fired(self):
        self.handle_msg()
        if not self.can_start: return
        for head in self.head_group:
            head.move()
            for ball in head.ball_group:
                ball.move()
        for ball in self.free_ball_group:
            ball.move()
        if self.my_head != None:
            self.handle_ball_collision(self.my_head)
        if self.his_head != None:
            self.handle_ball_collision(self.his_head)

    def draw_path(self):
        for path in Game.paths:
            for pixel in path.p0path:
                x, y = pixel
                pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 1)
            for pixel in path.p1path:
                x, y = pixel
                pygame.draw.circle(self.screen, (255, 0, 0), (x, y), 1)

    def game_redraw_all(self):
        self.head_group.draw(self.screen)
        for head in self.head_group:
            head.ball_group.draw(self.screen)
        self.free_ball_group.draw(self.screen)
        self.draw_path()

    def intro_redraw_all(self):
        self.play_button.draw(self.screen)

    def redraw_all(self):
        if self.splash == self.GAME_SPLASH:
            self.game_redraw_all()
        elif self.splash == self.INTRO_SPLASH:
            self.intro_redraw_all()

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

HOST = ''
PORT = 50014

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect((HOST,PORT))

serverMsg = Queue(100)

def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ''
    command = ''
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
