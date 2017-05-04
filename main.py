import pygame, math, random, numbers, socket, pickle, time
from _thread import *
from queue import Queue

from ball import Ball
from head import Head
from button import Button
from path import Path

# pygame framework inspired by optional lecture by Lukas Peraza
# socket framework inspired by optional lecture by Rohan Varma

def ball_collide(ball0, ball1):
    dist = ((ball0.cx - ball1.cx) ** 2 + (ball0.cy - ball1.cy) ** 2) ** .5
    return dist < ball0.r + ball1.r

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
        # set game params
        self.width = 800
        self.height = 600
        self.FPS = 50
        self.frame_count = 0
        self.INTRO_SPLASH = 'intro'
        self.GAME_SPLASH = 'game'
        self.WIN_SPLASH = 'win'
        self.LOSE_SPLASH = 'lose'
        self.EDIT_SPLASH = 'edit'
        self.MENU_SPLASH = 'menu'
        self.SETTINGS_SPLASH = 'settings'
        self.sfx_vol = .75

        # init pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # load fonts
        # veiset
        self.font = pygame.font.Font('./fonts/Courier.dfont', 30)
        self.papyrus = pygame.font.Font('./fonts/Papyrus.ttc', 30)

        # load class attrs
        Button.load_images()
        Game.load_paths(self.width, self.height)
        Head.load_images()
        Ball.load_images()
        Ball.load_sounds()
        Ball.kill_sound.set_volume(self.sfx_vol)
        Ball.collide_sound.set_volume(self.sfx_vol)

        # buttons
        self.play_button = Button(592, 118, 150, 60, self.font, '', 'play')
        self.edit_button = Button(568, 215, 175, 60,
                                  self.font, 'Edit Maps', 'green')
        self.intro_quit_button = Button(650, 410, 100, 100,
                                        self.font, 'Quit', 'red')
        self.intro_settings_button = Button(555, 310, 185, 55,
                                            self.font, 'Settings', 'purple')

        self.edit_p0path_button = Button(self.width - 120, self.height - 100,
                                         120, 50, self.font, 'Path 0', 'green')
        self.edit_p1path_button = Button(self.width - 120, self.height - 50,
                                         120, 50, self.font, 'Path 1', 'red')
        self.edit_save_button = Button(0, self.height - 100,
                                       150, 50, self.font, 'Save', 'green')
        self.edit_abandon_button = Button(0, self.height - 50,
                                          150, 50, self.font, 'Abandon', 'red')

        self.game_menu_button = Button(self.width - 130, 0, 100, 40,
                                       self.font, '', 'menu')

        self.menu_main_button = Button(self.width / 2 - 100,
                                       self.height / 2 - 50,
                                       200, 50, self.font, 'Main Menu', 'green')
        self.menu_settings_button = Button(self.width / 2 - 100,
                                           self.height / 2,
                                           200, 50, self.font, 'Settings',
                                           'purple')
        self.menu_back_button = Button(self.width / 2 - 100,
                                       self.height / 2 + 100,
                                       200, 50, self.font, '', 'back')

        self.settings_bgm_button = Button(self.width / 5, self.height / 2 - 50,
                                          100, 50, self.font, 'BGM', 'green')
        self.settings_sfx_button = Button(self.width / 5, self.height / 2,
                                          100, 50, self.font, 'SFX', 'green')
        self.settings_back_button = Button(self.width / 2 - 75,
                                           self.height * 4 / 5,
                                           150, 50, self.font, '', 'back')

        self.quit_button = Button(self.width / 2 - 75,
                                  self.height * 2 / 3 - 75,
                                  150, 150, self.font, 'Quit', 'red')
        self.quit_single = pygame.sprite.GroupSingle(self.quit_button)

        # load bg imgs
        self.intro_bg = pygame.transform.scale(
            pygame.image.load('./imgs/intro.png'), (self.width, self.height))
        self.bg = pygame.transform.scale(
            pygame.image.load('./imgs/bg.png'), (self.width, self.height))
        self.purple_bg = pygame.transform.scale(
            pygame.image.load('./imgs/purple_bg.png'),
            (self.width, self.height))

        # game groups
        self.head_group = pygame.sprite.Group()
        self.free_ball_group = pygame.sprite.Group()

        # button groups
        self.intro_button_group = pygame.sprite.Group(
                                                     self.play_button,
                                                     self.edit_button,
                                                     self.intro_quit_button,
                                                     self.intro_settings_button)
        self.game_buttons_group = pygame.sprite.Group(self.game_menu_button)
        self.edit_buttons_group = pygame.sprite.Group(self.edit_save_button,
                                                      self.edit_abandon_button,
                                                      self.edit_p0path_button,
                                                      self.edit_p1path_button)
        self.menu_button_group = pygame.sprite.Group(self.menu_back_button,
                                                     self.menu_main_button,
                                                     self.menu_settings_button)
        self.settings_button_group = pygame.sprite.Group(
                                                      self.settings_bgm_button,
                                                      self.settings_sfx_button,
                                                      self.settings_back_button)

        # load and play bgm
        pygame.mixer.music.load('./sounds/bgm.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(.75)

        # setting vars
        self.is_playing = True
        self.is_paused = False
        self.is_game_over = False
        self.curr_path_img = None
        self.custom_path = None
        self.is_editing_p0path = True
        self.can_start = False
        self.is_initiated = False
        self.id = None
        self.splash = self.INTRO_SPLASH
        self.prev_splash = self.INTRO_SPLASH
        self.from_splash = self.INTRO_SPLASH
        self.game_path = random.choice(Game.paths)
        self.my_head = self.his_head = None

    def game_mouse_motion(self, pos, rel, buttons):
        for button in self.game_buttons_group:
            button.update_img()
        self.my_head.rotate(pos)
        msg = (('moved' + ' %d' * 7 + '\n') %
        (pos[0], pos[1], rel[0], rel[1], buttons[0], buttons[1], buttons[2]))
        if not self.can_start: return
        self.send_msg(msg)

    def edit_drag1(self, pos, rel):
        if self.is_editing_p0path:
            self.custom_path.p0path.append(pos)
        else:
            self.custom_path.p1path.append(pos)

    def edit_motion(self, pos, rel, buttons):
        if buttons == (1, 0, 0):
            if self.custom_path == None:
                self.custom_path = Path(self.width, self.height)
            self.edit_drag1(pos, rel)

    def intro_motion(self, pos, rel, buttons):
        if buttons == (0, 0, 0):
            for button in self.intro_button_group:
                button.update_img()

    def menu_motion(self, pos, rel, buttons):
        if buttons == (0, 0, 0):
            for button in self.menu_button_group:
                button.update_img()

    def settings_motion(self, pos, rel, buttons):
        if buttons == (0, 0, 0):
            for button in self.settings_button_group:
                button.update_img()

    def win_motion(self, pos, rel, buttons):
        if buttons == (0, 0, 0):
            self.quit_button.update_img()

    def lose_motion(self, pos, rel, buttons):
        if buttons == (0, 0, 0):
            self.quit_button.update_img()

    def mouse_motion(self, pos, rel, buttons):
        if self.splash == self.GAME_SPLASH:
            self.game_mouse_motion(pos, rel, buttons)
        elif self.splash == self.EDIT_SPLASH:
            self.edit_motion(pos, rel, buttons)
        elif self.splash == self.INTRO_SPLASH:
            self.intro_motion(pos, rel, buttons)
        elif self.splash == self.MENU_SPLASH:
            self.menu_motion(pos, rel, buttons)
        elif self.splash == self.SETTINGS_SPLASH:
            self.settings_motion(pos, rel, buttons)
        elif self.splash == self.WIN_SPLASH:
            self.win_motion(pos, rel, buttons)
        elif self.splash == self.LOSE_SPLASH:
            self.lose_motion(pos, rel, buttons)

    def game_menu_clicked(self):
        self.splash = self.MENU_SPLASH
        self.prev_splash = self.GAME_SPLASH
        self.is_paused = True

    def game_mouse_button_down(self, pos, button):
        if button == 1:
            if self.game_menu_button.is_clicked(pos):
                self.game_menu_clicked()
            else:
                self.my_head.shoot(pos, self.free_ball_group)
                msg = 'clicked %d %d %d\n' % (pos[0], pos[1], button)
                self.send_msg(msg)

    def intro_mouse_button_down(self, pos, button):
        if button == 1:
            if self.play_button.rect.collidepoint(pos):
                self.splash = self.GAME_SPLASH
                msg = 'ready\n\n'
                self.send_msg(msg)
            elif self.edit_button.rect.collidepoint(pos):
                self.splash = self.EDIT_SPLASH
                self.custom_path = None
            elif self.intro_quit_button.is_clicked(pos):
                self.is_playing = False
            elif self.intro_settings_button.is_clicked(pos):
                self.settings_bgm_button.is_toggled = False
                self.settings_sfx_button.is_toggled = False
                self.settings_bgm_button.image = (
                                            self.settings_bgm_button.base_image)
                self.settings_sfx_button.image = (
                                            self.settings_sfx_button.base_image)
                self.from_splash = self.INTRO_SPLASH
                self.splash = self.SETTINGS_SPLASH

    def update_game_path(self):
        self.game_path = self.custom_path
        if self.my_head != None:
            if self.id == 0:
                self.my_head.path = self.game_path.p0path
            elif self.id == 1:
                self.my_head.path = self.game_path.p1path
            else:
                print('err: id %d' % self.id)
        msg0 = ('p0path ' + ' '.join((str(self.game_path.p0path[i][0]) + ' ' +
str(self.game_path.p0path[i][1])) for i in range(len(self.game_path.p0path))) +
'\n')
        self.send_msg(msg0)
        msg1 = ('p1path ' + ' '.join((str(self.game_path.p1path[i][0]) + ' ' +
str(self.game_path.p1path[i][1])) for i in range(len(self.game_path.p1path))) +
'\n')
        self.send_msg(msg1)

    def edit_save_clicked(self):
        self.update_game_path()
        self.splash = self.INTRO_SPLASH

    def edit_abandon_clicked(self):
        self.splash = self.INTRO_SPLASH

    def edit_p0path_clicked(self):
        self.is_editing_p0path = True
        self.edit_p0path_button.is_toggled = True
        self.edit_p1path_button.is_toggled = False
        self.edit_p0path_button.image = self.edit_p0path_button.clicked_img
        self.edit_p1path_button.image = self.edit_p1path_button.base_image

    def edit_p1path_clicked(self):
        self.is_editing_p0path = False
        self.edit_p0path_button.is_toggled = False
        self.edit_p1path_button.is_toggled = True
        self.edit_p0path_button.image = self.edit_p0path_button.base_image
        self.edit_p1path_button.image = self.edit_p1path_button.clicked_img

    def edit_button1down(self, pos):
        if self.edit_save_button.is_clicked(pos):
            self.edit_save_clicked()
        elif self.edit_abandon_button.is_clicked(pos):
            self.edit_abandon_clicked()
        elif self.edit_p0path_button.is_clicked(pos):
            self.edit_p0path_clicked()
        elif self.edit_p1path_button.is_clicked(pos):
            self.edit_p1path_clicked()

    def edit_mouse_button_down(self, pos, button):
        if button == 1:
            self.edit_button1down(pos)

    def menu_button1down(self, pos):
        if self.menu_back_button.is_clicked(pos):
            self.splash, self.prev_splash = self.prev_splash, self.splash
        elif self.menu_main_button.is_clicked(pos):
            self.splash = self.INTRO_SPLASH
        elif self.menu_settings_button.is_clicked(pos):
            self.settings_bgm_button.is_toggled = False
            self.settings_sfx_button.is_toggled = False
            self.settings_bgm_button.image = self.settings_bgm_button.base_image
            self.settings_sfx_button.image = self.settings_sfx_button.base_image
            self.splash = self.SETTINGS_SPLASH
            self.from_splash = self.MENU_SPLASH

    def menu_mouse_button_down(self, pos, button):
        if button == 1:
            self.menu_button1down(pos)

    def settings_down(self, pos, button):
        if button == 1:
            if self.settings_back_button.is_clicked(pos):
                self.splash = self.from_splash
            elif self.settings_bgm_button.is_clicked(pos):
                self.settings_bgm_button.is_toggled = True
                self.settings_sfx_button.is_toggled = False
                self.settings_bgm_button.image = (
                    self.settings_bgm_button.clicked_img)
                self.settings_sfx_button.image = (
                    self.settings_sfx_button.base_image)
            elif self.settings_sfx_button.is_clicked(pos):
                self.settings_bgm_button.is_toggled = False
                self.settings_sfx_button.is_toggled = True
                self.settings_bgm_button.image = (
                    self.settings_bgm_button.base_image)
                self.settings_sfx_button.image = (
                    self.settings_sfx_button.clicked_img)

    def win_down(self, pos, button):
        if button == 1:
            if self.quit_button.is_clicked(pos):
                self.is_playing = False

    def lose_down(self, pos, button):
        if button == 1:
            if self.quit_button.is_clicked(pos):
                self.is_playing = False

    def mouse_button_down(self, pos, button):
        if self.splash == self.GAME_SPLASH:
            self.game_mouse_button_down(pos, button)
        elif self.splash == self.INTRO_SPLASH:
            self.intro_mouse_button_down(pos, button)
        elif self.splash == self.EDIT_SPLASH:
            self.edit_mouse_button_down(pos, button)
        elif self.splash == self.MENU_SPLASH:
            self.menu_mouse_button_down(pos, button)
        elif self.splash == self.SETTINGS_SPLASH:
            self.settings_down(pos, button)
        elif self.splash == self.WIN_SPLASH:
            self.win_down(pos, button)
        elif self.splash == self.LOSE_SPLASH:
            self.lose_down(pos, button)

    def settings_key(self, unicode, key, mod):
        if key == 273:
            dV = .05
        elif key == 274:
            dV = -.05
        else:
            return

        if (self.settings_bgm_button.is_toggled and
            not self.settings_sfx_button.is_toggled):
            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + dV)
        elif (not self.settings_bgm_button.is_toggled and
              self.settings_sfx_button.is_toggled):
            self.sfx_vol += dV
            if self.sfx_vol > 1:
                self.sfx_vol = 1
            elif self.sfx_vol < .0390625:
                self.sfx_vol = .0390625
            Ball.kill_sound.set_volume(self.sfx_vol)
            Ball.collide_sound.set_volume(self.sfx_vol)

    def key(self, unicode, key, mod):
        if self.splash == self.SETTINGS_SPLASH:
            self.settings_key(unicode, key, mod)

    def send_msg(self, msg):
        server.send(msg.encode())

    def update_head_path(self):
        if self.id == 0:
            self.my_head.path = self.game_path.p0path
        else:
            self.my_head.path = self.game_path.p1path
        if self.his_id == 0:
            self.his_head.path = self.game_path.p0path
        else:
            self.his_head.path = self.game.path.p1path

    def handle_id_msg(self, msg):
        self.id = int(msg[1])
        if self.id == 0:
            self.my_head = Head(self.id, self.game_path.p0path,
                                self.width, self.height, self.his_head)
        elif self.id == 1:
            self.my_head = Head(self.id, self.game_path.p1path,
                                self.width, self.height, self.his_head)
        self.head_group.add(self.my_head)
        msg_out = ('balls ' + ' '.join(str(self.my_head.ball_list[i])
            for i in range(len(self.my_head.ball_list))) + '\n')
        self.send_msg(msg_out)

    def handle_new_player_msg(self, msg):
        self.his_id = int(msg[1])
        if self.his_id == 0:
            self.his_head = Head(self.his_id, self.game_path.p0path,
                                 self.width, self.height, self.my_head)
        elif self.his_id == 1:
            self.his_head = Head(self.his_id, self.game_path.p1path,
                                 self.width, self.height, self.my_head)
        self.my_head.stranger = self.his_head
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

    def handle_new_ball_msg(self, msg):
        color_index = int(msg[1])
        if self.his_head == None:
            serverMsg.put(' '.join(msg))
        else:
            self.his_head.ball_group.add(Ball(self.his_head, 0, color_index,
                self.width, self.height))

    def handle_p0path_msg(self, msg):
        p0path = []
        msg = msg[1:]
        for i in range(0, len(msg), 2):
            x = int(msg[i])
            y = int(msg[i+1])
            pos = (x, y)
            p0path.append(pos)
        self.game_path.p0path = p0path
        self.update_head_path()

    def handle_p1path_msg(self, msg):
        p1path = []
        msg = msg[1:]
        for i in range(0, len(msg), 2):
            x = int(msg[i])
            y = int(msg[i+1])
            pos = (x, y)
            p1path.append(pos)
        self.game_path.p1path = p1path
        self.update_head_path()

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
            elif msg[0] == 'balls':
                self.handle_balls_msg(msg)
                self.is_initiated = True
            elif msg[0] == 'clicked':
                self.handle_clicked_msg(msg)
            elif msg[0] == 'moved':
                self.handle_moved_msg(msg)
            elif msg[0] == 'new_ball':
                self.handle_new_ball_msg(msg)
            elif msg[0] == 'p0path':
                self.handle_p0path_msg(msg)
            elif msg[0] == 'p1path':
                self.handle_p1path_msg(msg)
            else:
                print('what is this?', repr(msg))
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
            ball.was_colliding = True
            other_balls = collided_balls[ball]
            if len(other_balls) > 0:
                Ball.collide_sound.play()
                him = other_balls[0]
                for other_ball in other_balls:
                    if other_ball.index < him.index:
                        him = other_ball
                skip = False
                if him.owner == ball.owner and him.index == 0:
                    skip = True
                if not skip:
                    self.insert_ball_after_index(ball, head, him.index)

                    # kill string of balls of the same color, within which this
                    # ball is involved
                    indices_to_kill = [ball.index]

                    # looking forward
                    prev_index = ball.index
                    for head_ball in head.ball_group:
                        if ((head_ball.color == ball.color) and
                            (head_ball.index == prev_index + 1)):
                            indices_to_kill.append(head_ball.index)
                            prev_index += 1

                    # looking backward
                    prev_index = ball.index
                    for head_ball in head.ball_group:
                        if ((head_ball.color == ball.color) and
                            (head_ball.index == prev_index - 1)):
                            indices_to_kill.append(head_ball.index)
                            prev_index -= 1

                    # killing balls
                    if len(indices_to_kill) > 2:
                        Ball.kill_sound.play()
                        for i in indices_to_kill:
                            for head_ball in head.ball_group:
                                if head_ball.index == i:
                                    head_ball.kill()

                        # updating indices and pos'es
                        shift = len(indices_to_kill)
                        largest_killed_index = max(indices_to_kill)
                        for head_ball in head.ball_group:
                            if head_ball.index > largest_killed_index:
                                head_ball.index -= shift

                        for head_ball in head.ball_group:
                            head_ball.update_pos()
                            head_ball.update_coords()
                            head_ball.update_rect()

    def game_timer_fired(self):
        if not self.can_start: return
        self.frame_count += 1
        if pygame.sprite.collide_circle(self.my_head, self.his_head):
            self.is_game_over = True
            self.splash = self.LOSE_SPLASH
        if self.is_game_over: return
        self.is_game_over = True
        for head in self.head_group:
            if len(head.ball_group) > 2:
                self.is_game_over = False
            head.move()
            for ball in head.ball_group:
                ball.move()
        if len(self.free_ball_group) > 0:
            self.is_game_over = False

        if self.is_game_over:
            self.splash = self.WIN_SPLASH
        if self.is_initiated and len(self.my_head.ball_group) == 0:
            color_index = random.randint(0, 2)
            self.my_head.ball_group.add(Ball(self.my_head, 0, color_index,
                self.width, self.height))
            msg = 'new_ball %d\n' % color_index
            self.send_msg(msg)
        for ball in self.free_ball_group:
            ball.move()
        if self.my_head != None:
            self.handle_ball_collision(self.my_head)
        if self.his_head != None:
            self.handle_ball_collision(self.his_head)

    def edit_timer_fired(self):
        self.edit_buttons_group.update()

    def menu_timer(self):
        if self.prev_splash == self.GAME_SPLASH:
            self.game_timer_fired()

    def settings_timer(self):
        if self.prev_splash == self.GAME_SPLASH:
            self.game_timer_fired()

    def timer_fired(self):
        self.handle_msg()
        if self.splash == self.GAME_SPLASH:
            self.game_timer_fired()
        elif self.splash == self.EDIT_SPLASH:
            self.edit_timer_fired()
        elif self.splash == self.MENU_SPLASH:
            self.menu_timer()
        elif self.splash == self.SETTINGS_SPLASH:
            self.settings_timer()

    def generate_curr_path_img(self):
        # UnkwnTech
        self.curr_path_img = pygame.Surface((self.width, self.height),
            pygame.SRCALPHA, 32)
        path = self.game_path
        for pixel in path.p0path:
            x, y = pixel
            pygame.draw.circle(self.curr_path_img, (165, 42, 42), (x, y), 10)
        for pixel in path.p1path:
            x, y = pixel
            pygame.draw.circle(self.curr_path_img, (165, 42, 42), (x, y), 10)

    def draw_curr_path_img(self):
        self.screen.blit(self.curr_path_img, (0, 0))

    def draw_path(self):
        if self.curr_path_img == None:
            self.generate_curr_path_img()
        self.draw_curr_path_img()

    def draw_bg(self):
        self.screen.blit(self.bg, (0, 0))

    def game_redraw_all(self):
        self.draw_bg()
        self.draw_path()
        self.head_group.draw(self.screen)
        for head in self.head_group:
            head.ball_group.draw(self.screen)
        self.free_ball_group.draw(self.screen)
        self.game_buttons_group.draw(self.screen)

    def intro_redraw_all(self):
        self.screen.blit(self.intro_bg, (0, 0))
        self.intro_button_group.draw(self.screen)

    def draw_transparent_rect(self, surface, color, rect):
        # Giráldez
        x0, y0, w, h = rect
        s = pygame.Surface((w, h))
        r, g, b, a = color
        s.set_alpha(a)
        s.fill((r, g, b))
        surface.blit(s, (x0, y0))

    def win_redraw_all(self):
        self.game_redraw_all()
        self.draw_transparent_rect(self.screen, (255, 255, 255, 128),
            (0, 0, self.width, self.height))
        win_surface = self.font.render('YOU WIN!', 1, (0, 0, 0))
        w, h = win_surface.get_size()
        self.screen.blit(win_surface, ((self.width - w) / 2,
                                       (self.height - h) / 2))
        self.quit_single.draw(self.screen)

    def lose_redraw_all(self):
        self.game_redraw_all()
        self.draw_transparent_rect(self.screen, (0, 0, 0, 128),
            (0, 0, self.width, self.height))
        lose_surface = self.font.render('you lose…', 1, (255, 255, 255))
        w, h = lose_surface.get_size()
        self.screen.blit(lose_surface, ((self.width - w) / 2,
            (self.height - h) / 2))
        self.quit_single.draw(self.screen)

    def edit_draw_title(self):
        title = self.font.render('CUSTOM MAP', 1, (0, 0, 0))
        self.screen.blit(title, ((self.width - title.get_width()) / 2, 0))

    def edit_draw_buttons(self):
        self.edit_buttons_group.draw(self.screen)

    def edit_draw_custom_path(self):
        for pos in self.custom_path.p0path:
            pygame.draw.circle(self.screen, (0, 200, 0), pos, 10)
        for pos in self.custom_path.p1path:
            pygame.draw.circle(self.screen, (200, 0, 0), pos, 10)

    def edit_redraw_all(self):
        self.draw_bg()
        self.edit_draw_title()
        self.edit_draw_buttons()
        if self.custom_path != None:
            self.edit_draw_custom_path()

    def menu_redraw(self):
        if self.prev_splash == self.GAME_SPLASH:
            self.game_redraw_all()
        self.draw_transparent_rect(self.screen, (0, 0, 0, 128),
            (0, 0, self.width, self.height))
        self.menu_button_group.draw(self.screen)

    def settings_redraw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.purple_bg, (0, 0))

        title = self.font.render('Settings', 1, (255, 255, 255))
        title_w, title_h = title.get_size()
        self.screen.blit(title, ((self.width - title_w) / 2, title_h * 1.5))

        self.settings_button_group.draw(self.screen)

        pygame.draw.line(self.screen, (20, 20, 20),
                         (self.width * 2 / 5, (self.height - 25) / 2),
                         (self.width * 4 / 5, (self.height - 25) / 2), 3)
        pygame.draw.line(self.screen, (20, 20, 20),
                         (self.width * 2 / 5, (self.height + 25) / 2),
                         (self.width * 4 / 5, (self.height + 25) / 2), 3)

        pygame.draw.circle(self.screen,
                           (200, 200, 200),
                           (int(self.width * .4 *
                                (1 + pygame.mixer.music.get_volume())),
                            (self.height - 25) // 2),
                           10)
        pygame.draw.circle(self.screen,
                           (200, 200, 200),
                           (int(self.width * .4 * (1 + self.sfx_vol)),
                            int((self.height + 25) / 2)),
                           10)

    def redraw_all(self):
        if self.splash == self.GAME_SPLASH:
            self.game_redraw_all()
        elif self.splash == self.INTRO_SPLASH:
            self.intro_redraw_all()
        elif self.splash == self.WIN_SPLASH:
            self.win_redraw_all()
        elif self.splash == self.LOSE_SPLASH:
            self.lose_redraw_all()
        elif self.splash == self.EDIT_SPLASH:
            self.edit_redraw_all()
        elif self.splash == self.MENU_SPLASH:
            self.menu_redraw()
        elif self.splash == self.SETTINGS_SPLASH:
            self.settings_redraw()

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
                elif event.type == pygame.KEYDOWN:
                    self.key(event.unicode, event.key, event.mod)
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

# Works Cited #
# AndroidGunso. YouTube. https://i.ytimg.com/vi/hDR6N3EdG34/maxresdefault.jpg.
# NimfaDora. Fan Pop. http://www.fanpop.com/clubs/zuma-deluxe/images/10840317/t\
    # itle/zuma-photo.
# Giráldez, Gustavo. Answer on "Draw a transparent rectangle in pygame."
    # StackOverflow. http://stackoverflow.com/questions/6339057/draw-a-transpar\
        # ent-rectangle-in-pygame.
# roblox. https://www.roblox.com/library/79538736/Zuma-Frog.
# sloth. Answer on "Detect mouseover an image in Pygame." StackOverflow. http:/\
        # /stackoverflow.com/questions/11846032/detect-mouseover-an-image-in-py\
        # game.
# UnkwnTech. Answer on "How to make a surface with a transparent background in
    # pygame." StackOverflow. http://stackoverflow.com/questions/328061/how-to-\
        # make-a-surface-with-a-transparent-background-in-pygame.
# veiset. StackOverflow. http://stackoverflow.com/questions/10077644/python-dis\
        # play-text-w-font-color.
# VGM For The Soul. YouTube. https://www.youtube.com/watch?v=HltKz0mLHig
# Zuma Game Awesome Stuff. Pinterest. https://s-media-cache-ak0.pinimg.com/orig\
        # inals/4a/37/a5/4a37a5314f51ba7398005a26ac1a4496.jpg.
# Zuma Sound Bites. http://www.soundboard.com/sb/zuma_game_sounds

# Bibliography
# DeGlopper, Peter. Answer on "Bytes to int - Python 3." StackOverflow. http://\
        # stackoverflow.com/questions/34009653/bytes-to-int-python-3/
# Pieters, Martijn. Answer on "How to split a byte string into separate bytes in
    # python." StackOverflow. http://stackoverflow.com/questions/20024490/how-t\
            # o-split-a-byte-string-into-separate-bytes-in-python.
# Peraza, Lukas. Pygame tutorial. http://blog.lukasperaza.com/getting-started-w\
        # ith-pygame/.
# ---. Pygame Example on Github. https://github.com/LBPeraza/Pygame-Asteroids.
# ---, and Lisa Liu. Pygame optional lectures.
# Pygame documentation. https://www.pygame.org/docs/.
# Python 3 documentation. https://docs.python.org/3/.
# Varma, Rohan. Socket optional lecture.
