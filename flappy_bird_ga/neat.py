import numpy as np
import pygame
from neatpy.options import Options
from neatpy.population import Population
from flappy_bird_ga.state import Bird, Barrier

# Implements the NEAT algorithm (https://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf)

D_IN = 3
D_OUT = 1

class NeatBird(Bird):

    def __init__(self, start_x, start_y, screen, nn):
        super().__init__(start_x, start_y, screen)
        self.nn = nn
        self.cb_x = 0
        self.cb_y = 0
        self.cb_gap = 0

    def tick(self):
        features = np.array([self.v, self.cb_x/288, self.cb_y/512])
        a = self.nn.predict(features)
        if (a[0] > 0.5): self.v += 1

    def update(self):
        if not self.alive: return
        self.d += 1
        self.nn.fitness += 1/288
        self.v -= self.g
        self.y -= self.v

    def collide(self, bot, top, barriers: list[Barrier]):
        if not self.alive: return True
        if (self.y < bot or self.y > top-24):
            self.alive = False
            return True

        coll_barrier = barriers[0]
        if (coll_barrier.x + 52 < self.x):
            coll_barrier = barriers[1]

        self.cb_x = coll_barrier.x - self.x + 52
        self.cb_y = self.y - coll_barrier.y
        self.cb_gap = coll_barrier.gap
        if (coll_barrier.x < self.x + 34 and coll_barrier.x + 52 > self.x) and \
           (self.y < coll_barrier.y or self.y+24 > coll_barrier.y + coll_barrier.gap):
            self.alive = False
            return True

        return False

class NeatAlgorithm:

    def __init__(self):
        self.opt = Options.set_options(D_IN, D_OUT, 100)
        self.pop = Population()

    def spawn(self, sx, sy, screen, n=50):
        birds = []
        for nn in self.pop.pool:
            birds.append(NeatBird(sx, sy, screen, nn))
        return birds

    def learn(self, birds):
        self.pop.epoch()

    def render(self, screen):
        pass
