# Activity 1: Tweening, Morphing, and Dynamics Engine in Pygame
# Keys: 1 = Tweening, 2 = Morphing, 3 = Dynamics, E = toggle easing, F12 = screenshot, ESC = quit
import pygame, math, sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Activity 1: 2D Animation, Tweening & Morphing Engine')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 26)
FPS = 60


# ---------- Interpolation helpers ----------
def lerp_point(p1, p2, t):
    # P(t) = (1 - t) * P_start + t * P_end
    return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)

def ease_in_out(t):
    # slow at the start and end, fast in the middle
    return t * t * (3 - 2 * t)


# ---------- Task 1.1: Tweening along a multi-point path ----------
path = [(100, 450), (250, 150), (400, 400), (550, 150), (700, 450)]
DURATION = 4.0        # seconds for the whole path -> 4 * 60 = 240 frames
tween_frame = 0

def tween_position(t):
    # split t (0..1) into a path segment and a local t inside that segment
    segments = len(path) - 1
    seg = min(int(t * segments), segments - 1)
    local_t = t * segments - seg
    return lerp_point(path[seg], path[seg + 1], local_t)


# ---------- Task 1.2: Morphing a triangle into a quadrilateral ----------
# The triangle gets a 4th (duplicate) vertex on its edge so both shapes have 4 vertices.
# (250, 200) is the midpoint of the edge (200, 100) -> (300, 300).
poly_start = [(200, 100), (250, 200), (300, 300), (100, 300)]  # triangle
poly_end   = [(150, 100), (350, 120), (320, 320), (120, 300)]  # quadrilateral
OFFSET = (200, 100)   # move both shapes to the middle of the screen
morph_frame = 0


# ---------- Task 1.3: Bouncing ball ----------
ball_x, ball_y = 100.0, 100.0
ball_vel_x, ball_vel_y = 4.0, 0.0
gravity = 0.5
restitution = 0.78
floor_y = 500
radius = 20

def reset_ball():
    global ball_x, ball_y, ball_vel_x, ball_vel_y
    ball_x, ball_y = 100.0, 100.0
    ball_vel_x, ball_vel_y = 4.0, 0.0

def update_ball():
    global ball_x, ball_y, ball_vel_x, ball_vel_y
    dt = 1
    # Euler integration: y = y + v*dt,  v = v + g*dt
    ball_x += ball_vel_x * dt
    ball_y += ball_vel_y * dt
    ball_vel_y += gravity * dt

    # floor collision: v_rebound = -e * v_impact
    if ball_y + radius >= floor_y:
        ball_y = floor_y - radius
        if abs(ball_vel_y) < 4:     # bounce too small -> ball rests
            ball_vel_y = 0
        else:
            ball_vel_y = -restitution * ball_vel_y
        ball_vel_x *= 0.9           # friction slows the ball on each bounce

    # walls
    if ball_x - radius < 0 or ball_x + radius > 800:
        ball_vel_x = -ball_vel_x
        ball_x = max(radius, min(800 - radius, ball_x))


# ---------- Drawing ----------
def draw_text(lines):
    y = 15
    for line in lines:
        screen.blit(font.render(line, True, (255, 255, 255)), (15, y))
        y += 25

def draw_tweening():
    t = min(tween_frame / (DURATION * FPS), 1.0)
    if use_easing:
        t = ease_in_out(t)
    pygame.draw.lines(screen, (80, 80, 100), False, path, 2)
    for p in path:
        pygame.draw.rect(screen, (255, 180, 70), (p[0] - 6, p[1] - 6, 12, 12), 2)
    x, y = tween_position(t)
    pygame.draw.circle(screen, (255, 100, 150), (int(x), int(y)), 15)
    draw_text(['Mode 1: Tweening   (E = easing: %s)' % ('ON' if use_easing else 'OFF'),
               'frame %d / %d   t = %.2f' % (tween_frame, DURATION * FPS, t)])

def draw_morphing():
    # ping-pong: 0 -> 1 -> 0 over 4 seconds
    t = (morph_frame % 240) / 120
    if t > 1:
        t = 2 - t
    if use_easing:
        t = ease_in_out(t)
    shape = [lerp_point(a, b, t) for a, b in zip(poly_start, poly_end)]
    shape = [(x + OFFSET[0], y + OFFSET[1]) for x, y in shape]
    pygame.draw.polygon(screen, (90, 200, 250), shape)
    for i, (x, y) in enumerate(shape):
        pygame.draw.circle(screen, (255, 180, 70), (int(x), int(y)), 5)
        screen.blit(font.render('V%d' % i, True, (255, 180, 70)), (x + 8, y))
    draw_text(['Mode 2: Morphing triangle -> quadrilateral',
               't = %.2f   V(t) = (1 - t) * V_A + t * V_B' % t])

def draw_dynamics():
    pygame.draw.line(screen, (200, 200, 200), (0, floor_y), (800, floor_y), 3)
    pygame.draw.circle(screen, (255, 180, 70), (int(ball_x), int(ball_y)), radius)
    draw_text(['Mode 3: Bouncing ball   (R = drop again)',
               'g = %.1f   e = %.2f' % (gravity, restitution),
               'vx = %.2f   vy = %.2f' % (ball_vel_x, ball_vel_y)])


# ---------- Task 1.4: Main loop with mode switching ----------
mode = 1
use_easing = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                mode, tween_frame = 1, 0
            elif event.key == pygame.K_2:
                mode, morph_frame = 2, 0
            elif event.key == pygame.K_3:
                mode = 3
                reset_ball()
            elif event.key == pygame.K_e:
                use_easing = not use_easing
            elif event.key == pygame.K_r:
                reset_ball()
            elif event.key == pygame.K_F12:
                pygame.image.save(screen, 'screenshot_mode%d.png' % mode)

    # update
    if mode == 1:
        tween_frame = (tween_frame + 1) % int(DURATION * FPS + 30)   # loop with a short pause
    elif mode == 2:
        morph_frame += 1
    else:
        update_ball()

    # draw
    screen.fill((20, 24, 35))
    if mode == 1:
        draw_tweening()
    elif mode == 2:
        draw_morphing()
    else:
        draw_dynamics()
    pygame.display.flip()
    clock.tick(FPS)
