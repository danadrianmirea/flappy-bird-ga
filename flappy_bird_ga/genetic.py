import numpy as np
import pygame
from flappy_bird_ga.state import Bird, Barrier

# simple 2-layer mlp with 4 neurons per hidden layer

D0 = 3
D1 = 2
D2 = 1

class GeneticBird(Bird):

    def __init__(self, start_x, start_y, screen, m1, b1, m2, b2):
        super().__init__(start_x, start_y, screen)
        # 4 -> 2 -> 1
        self.m1 = m1
        self.b1 = b1
        self.m2 = m2
        self.b2 = b2
        self.cb_x = 0
        self.cb_y = 0
        self.cb_gap = 0

    def tick(self):
        if not self.alive: return
        self.d += 1
        features = np.array([self.v, self.cb_x/288, self.cb_y/512])
        a = np.maximum((features @ self.m1) + self.b1, 0)
        a = (a @ self.m2) + self.b2
        if (a.item() > 0): self.v += 1
        self.v -= self.g
        self.y -= self.v

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
            self.cb_x = coll_barrier.x
            self.cb_y = coll_barrier.y
            self.cb_gap = coll_barrier.gap
            if self.y < coll_barrier.y or self.y+24 > coll_barrier.y + coll_barrier.gap:
                self.alive = False
                return True

        return False

class GeneticAlgorithm:

    def __init__(self):
        self.font = pygame.font.SysFont('Menlo', 18)
        self.iteration = 0
        self.prev_gen_birds = []

    def reproduce(self, sx, sy, screen, parent_1: GeneticBird, parent_2: GeneticBird):

        fitness_ratio = parent_1.d/(parent_1.d + parent_2.d)
        mask_m1 = np.random.binomial(1, fitness_ratio, size=(D0,D1))
        mask_b1 = np.random.binomial(1, fitness_ratio, size=(D1))
        mask_m2 = np.random.binomial(1, fitness_ratio, size=(D1,D2))
        mask_b2 = np.random.binomial(1, fitness_ratio, size=(D2))

        m1 = mask_m1 * parent_1.m1 + (1-mask_m1) * parent_2.m1
        b1 = mask_b1 * parent_1.b1 + (1-mask_b1) * parent_2.b1
        m2 = mask_m2 * parent_1.m2 + (1-mask_m2) * parent_2.m2
        b2 = mask_b2 * parent_1.b2 + (1-mask_b2) * parent_2.b2

        mut_ratio = 0.1
        mut_m1 = np.random.binomial(1, mut_ratio, size=(D0,D1))
        mut_b1 = np.random.binomial(1, mut_ratio, size=(D1))
        mut_m2 = np.random.binomial(1, mut_ratio, size=(D1,D2))
        mut_b2 = np.random.binomial(1, mut_ratio, size=(D2))

        m1 = mut_m1 * m1 + (1-mut_m1) * np.random.normal(0, 1, (D0, D1))
        b1 = mut_b1 * b1 + (1-mut_b1) * np.random.normal(0, 1, (D1))
        m2 = mut_m2 * m2 + (1-mut_m2) * np.random.normal(0, 1, (D1, D2))
        b2 = mut_b2 * b2 + (1-mut_b2) * np.random.normal(0, 1, (D2))

        return GeneticBird(sx, sy, screen, m1, b1, m2, b2)

    def spawn(self, sx, sy, screen, n=50):
        birds = []
        if not self.prev_gen_birds:
            for _ in range(n):
                m1 = np.random.normal(0, 1, (D0, D1))
                b1 = np.zeros(D1)
                m2 = np.random.normal(0, 1, (D1, D2))
                b2 = np.zeros(D2)
                birds.append(GeneticBird(sx, sy, screen, m1, b1, m2, b2))
        else:
            # crossover + mutate
            probs = np.array([b.d for b in self.prev_gen_birds], dtype=np.float64)
            probs /= probs.sum()
            for _ in range(n):
                b1, b2 = np.random.choice(self.prev_gen_birds, 2, p=probs)
                child = self.reproduce(sx, sy, screen, b1, b2)
                birds.append(child)
        return birds

    def learn(self, birds):
        self.iteration += 1
        birds.sort(key=lambda b: -b.d)
        self.prev_gen_birds =  birds #[:len(birds)//10]

    def render(self, screen):
        pass
        # centres = [[20, 50, 80, 110, 140, 170], [50, 80, 110, 140], [50, 80, 110, 140], [95]]
        # axes = [700, 750, 800, 850]
        # for (i, mat) in enumerate([self.m_M1, self.m_M2, self.m_M3]):
        #     for (j, row) in enumerate(mat.T):
        #         tot_wt = np.sum(np.abs(row))
        #         for (k, wt) in enumerate(row):
        #             spos = pygame.Vector2(axes[i], centres[i][k])
        #             epos = pygame.Vector2(axes[i+1], centres[i+1][j])
        #             color = "white"
        #             if (tot_wt > 0):
        #                 color = pygame.color.Color(255-int(max(0,255*wt/tot_wt)), 255, 255-int(max(0,-255*wt/tot_wt)))
        #             pygame.draw.line(screen, color, spos, epos, width=2)

        # for axis, neurons in zip(axes, centres):
        #     for neuron in neurons:
        #         pygame.draw.circle(screen, "white", pygame.Vector2(axis, neuron), 10)
        #         pygame.draw.circle(screen, "black", pygame.Vector2(axis, neuron), 10, width=2)

        # screen.blit(self.font.render(f"Gen: {self.iteration}", False, (0, 0, 0)), (10, 10))

