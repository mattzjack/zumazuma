class Path(object):
    def __init__(self, game_width, game_height):
        self.index = -1
        self.p0path = []
        self.p1path = []
        self.game_width = game_width
        self.game_height = game_height

    def __eq__(self, other):
        return ((isinstance(other, Path)) and
                ((self.p0path == other.p0path) and
                 (self.p1path == other.p1path)))

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
