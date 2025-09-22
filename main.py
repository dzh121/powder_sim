# pip install pygame
import pygame
import sys

WIDTH, HEIGHT = 640, 480
FPS = 60

class Particle:
    def __init__(self, x, y, radius=3):
        self.x = x
        self.y = y
        self.vy = 0.0
        self.radius = radius

    def update(self, dt):
      pass

    def draw(self, surface):
        pygame.draw.circle(surface, (218, 186, 128), (int(self.x), int(self.y)), self.radius)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Powder Sim – Starter")
    clock = pygame.time.Clock()

    # one powder-like particle
    particle = Particle(WIDTH // 2, 50)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds since last frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # update
        particle.update(dt)

        # draw
        screen.fill((20, 20, 25))
        particle.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
