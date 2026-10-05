# Activity 2: Object-Oriented Sprite Architecture and Collision
# Arrow keys = move, collect red targets, avoid grey obstacles. R = restart, F12 = screenshot, ESC = quit
import pygame, random, sys

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Activity 2: Sprite System & Collision Arena')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (44, 94, 138), (20, 20), 20)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 5

    def update(self):
        # Task 2.2: continuous steering + boundary clamping
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT: self.rect.y += self.speed


class Target(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((220, 50, 50))
        self.rect = self.image.get_rect(topleft=(random.randint(50, 750), random.randint(50, 550)))


class Obstacle(pygame.sprite.Sprite):
    # Task 2.1: roaming obstacle that bounces off the screen edges
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((150, 150, 160))
        self.rect = self.image.get_rect(topleft=(random.choice([20, 740]), random.randint(20, 540)))
        self.vx = random.choice([-3, 3])
        self.vy = random.choice([-3, 3])

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.vx = -self.vx
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.vy = -self.vy


class Particle(pygame.sprite.Sprite):
    # Task 2.4: translucent particle that fades out
    def __init__(self, pos, color):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)
        self.x, self.y = pos
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.alpha = 255

    def update(self):
        # only change state here - the alpha is applied when drawing
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.alpha -= 8
        if self.alpha <= 0:
            self.kill()   # remove from all groups


def new_game():
    global player, players, targets, obstacles, particles, score, health, lives
    player = Player()
    players = pygame.sprite.Group(player)
    targets = pygame.sprite.Group(Target() for _ in range(3))
    obstacles = pygame.sprite.Group(Obstacle() for _ in range(4))
    particles = pygame.sprite.Group()
    score, health, lives = 0, 100, 3


def explode(pos, color):
    for _ in range(20):
        particles.add(Particle(pos, color))


new_game()
hit_cooldown = 0

while True:
    # ----- 1. Process input -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            new_game()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
            pygame.image.save(screen, 'screenshot.png')

    # ----- 2. Update game state -----
    game_over = lives <= 0
    if not game_over:
        players.update()
        obstacles.update()

        # Task 2.3: collect targets (+10) and respawn a new one
        for target in pygame.sprite.spritecollide(player, targets, True):
            score += 10
            explode(target.rect.center, (255, 200, 60))
            targets.add(Target())

        # Task 2.3: hitting an obstacle costs health (with a short cooldown)
        if hit_cooldown > 0:
            hit_cooldown -= 1
        elif pygame.sprite.spritecollide(player, obstacles, False):
            health -= 25
            hit_cooldown = 60
            explode(player.rect.center, (255, 80, 80))
            if health <= 0:
                lives -= 1
                health = 100
    particles.update()

    # ----- 3. Render -----
    screen.fill((20, 24, 35))
    targets.draw(screen)
    obstacles.draw(screen)
    if not game_over:
        players.draw(screen)
    for p in particles:
        p.image.set_alpha(p.alpha)
        screen.blit(p.image, p.rect)

    hud = 'Score: %d   Health: %d   Lives: %d   FPS: %d' % (score, health, lives, clock.get_fps())
    screen.blit(font.render(hud, True, (255, 255, 255)), (10, 10))
    if game_over:
        text = font.render('GAME OVER - press R to restart', True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

    pygame.display.flip()
    # ----- 4. Regulate FPS -----
    clock.tick(60)
