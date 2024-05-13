import pygame

class Barrier:

    def __init__(self, x, y, sheet, gap=60):
        self.bot_sprite = pygame.transform.scale2x(sheet.image_at((84,323,26,160)))
        self.top_sprite = pygame.transform.scale2x(sheet.image_at((56,323,26,160)))
        self.x = x
        self.y = y
        self.w = 26*2
        self.gap = gap

    def render(self, screen):
        screen.blit(self.top_sprite, pygame.Rect((self.x, self.y-320, 52, 320)))
        screen.blit(self.bot_sprite, pygame.Rect((self.x, self.y+self.gap, 52, 320)))

    def tick(self):
        self.x -= 2;

class Bird:

    def __init__(self, start_x, start_y, sheet):
        self.x = start_x
        self.y = start_y
        self.sprite = pygame.transform.scale2x(sheet.image_at((31,491,17,12)))
        self.v = 0
        self.d = 0
        self.g = 0.5
        self.alive = True

    def tick(self):
        pass

    def update(self):
        if not self.alive: return
        self.d += 1

    def collide(self, bot, top, barriers: list[Barrier]):
        if not self.alive: return True
        if (self.y < bot or self.y > top-24):
            self.alive = False
            return True

        coll_barrier = None
        for i in [0, 1]:
            if (barriers[i].x > self.x-52 and barriers[i].x < self.x+34):
                coll_barrier = barriers[i]

        if (coll_barrier):
            if self.y < coll_barrier.y or self.y+24 > coll_barrier.y + coll_barrier.gap:
                self.alive = False
                return True

        return False

    def render(self, screen):
        if not self.alive: return
        screen.blit(self.sprite, pygame.Rect((self.x, self.y, 34, 24)))

