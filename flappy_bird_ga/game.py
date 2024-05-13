import pygame
import numpy as np
import random

from flappy_bird_ga.neat import NeatAlgorithm
from flappy_bird_ga.state import Bird, Barrier

class SpriteSheet:

    def __init__(self, filename):
        """Load the sheet."""
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)


    def image_at(self, rectangle, colorkey = None):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class PlayableBird(Bird):

    def __init__(self, start_x, start_y, sheet):
        super().__init__(start_x, start_y, sheet)

    def tick(self):
        if not self.alive: return
        self.d += 1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.v += 1
        self.v -= self.g
        self.y -= self.v

class PlayableAlgorithm:

    def spawn(self, start_x, start_y, sheet):
        return [PlayableBird(start_x, start_y, sheet)]
    
    def learn(self, birds):
        pass
    
    def render(self, screen):
        pass

class Game:

    def __init__(self, human = False):
        self.sheet = SpriteSheet("sprites.png")
        self.background_sprite = pygame.transform.scale2x(self.sheet.image_at((0,0,144,256)))
        self.score = -1
        if human:
            self.algo = PlayableAlgorithm()
        else:
            self.algo = NeatAlgorithm()

        self.reset()

    def reset(self):
        print(self.score+1)
        self.scroll_loc = 0
        self.score = -1
        self.birds = self.algo.spawn(288, 256-17, self.sheet)
        self.barriers = [Barrier(i, random.randint(512-320-40,320), self.sheet) for i in [288*2, 288*3, 288*4]]

    def render(self, screen):
        bg_mod = self.scroll_loc % 288
        screen.blit(self.background_sprite, pygame.Rect((-bg_mod,0,288,512)))
        screen.blit(self.background_sprite, pygame.Rect((288-bg_mod,0,288,512)))
        screen.blit(self.background_sprite, pygame.Rect((288*2-bg_mod,0,288,512)))
        screen.blit(self.background_sprite, pygame.Rect((288*3-bg_mod,0,288,512)))
        for bird in self.birds:
            bird.render(screen)
        for barrier in self.barriers:
            barrier.render(screen)
        # optional
        self.algo.render(screen)
    
    def tick(self, impulse):

        # check collisions
        for bird in self.birds:
            bird.collide(0, 512, self.barriers)

        all_birds_dead = True
        printed_features = False
        for bird in self.birds:
            if bird.alive:
                # if not printed_features:
                #     features = np.array([bird.v, bird.cb_x/288, bird.cb_y/512])
                #     print(features)
                #     printed_features = True
                all_birds_dead = False
                break
        
        if (all_birds_dead):
            self.algo.learn(self.birds)
            self.reset()
            return

        self.scroll_loc += 1
        for bird in self.birds:
            if impulse:
                bird.tick()
            bird.update()

        self.scroll_loc += 1
        update_barriers = False
        for barrier in self.barriers:
            barrier.tick()
            if (barrier.x + 52 < 0):
                update_barriers = True
        if update_barriers:
            self.barriers = self.barriers[1:]
            self.barriers.append(Barrier(288*3, random.randint(512-320-40, 320), self.sheet))
            self.score += 1

    def get_score(self):
        return self.score+1

# pygame setup
def run_game():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((864, 512))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    game = Game(human=False)

    ctr = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        impulse = (ctr % 10 == 0)
        game.tick(impulse)

        game.render(screen)

        pygame.display.flip()

        dt = clock.tick(600) / 1000

    pygame.quit()
