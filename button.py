import pygame

class Button(pygame.sprite.Sprite):
    @staticmethod
    def load_images():
        # images from AndroidGunso
        Button.images = dict()
        for file in ['green', 'play', 'back', 'red']:
            Button.images[file] = pygame.image.load('./imgs/%s_button.png' % file)

    def __init__(self, x0, y0, w, h, font, text, color):
        super().__init__()
        self.x0 = x0
        self.y0 = y0
        self.w = w
        self.h = h
        self.font = font
        self.text = text
        self.color = color

        self.base_image = pygame.transform.scale(Button.images[self.color], (self.w, self.h))
        self.rect = pygame.Rect(self.x0, self.y0, self.w, self.h)
        # veiset
        # BEGIN
        self.label = self.font.render(self.text, 1, (205, 250, 195))
        pos = (((self.rect.w-self.label.get_size()[0]) / 2), ((self.rect.h - self.label.get_size()[1]) / 2))
        self.base_image.blit(self.label, pos)
        # END

        # generate hover img
        self.base_string = pygame.image.tostring(self.base_image, 'RGBA')
        self.hover_string = b''
        for i in range(0, len(self.base_string), 4):
            r = min(255, self.base_string[i] + 20)
            g = min(255, self.base_string[i + 1] + 20)
            b = min(255, self.base_string[i + 2] + 20)
            a = self.base_string[i + 3]
            for elem in [r, g, b, a]:
                self.hover_string += elem.to_bytes(1, 'big')
        self.hover_image = pygame.image.fromstring(self.hover_string, (self.w, self.h), 'RGBA')

        # generate clicked img
        self.clicked_str = b''
        for i in range(0, len(self.base_string), 4):
            r = max(0, self.base_string[i] - 20)
            g = max(0, self.base_string[i+1] - 50)
            b = max(0, self.base_string[i+2] - 50)
            a = self.base_string[i+3]
            for elem in [r, g, b, a]:
                self.clicked_str += elem.to_bytes(1, 'big')
        self.clicked_img = pygame.image.fromstring(self.clicked_str, (self.w, self.h), 'RGBA')

        self.image = self.base_image.copy()

        self.prev_is_hover = False
        self.is_hover = False
        self.is_toggled = False

    def update(self):
        self.update_img()

    def update_img(self):
        self.prev_is_hover = self.is_hover
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.is_hover = True
        else:
            self.is_hover = False
        if self.prev_is_hover != self.is_hover:
            if self.is_hover:
                self.image = self.hover_image.copy()
            else:
                if self.is_toggled:
                    self.image = self.clicked_img
                else:
                    self.image = self.base_image.copy()

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
