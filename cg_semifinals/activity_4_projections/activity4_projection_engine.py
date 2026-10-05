# Activity 4: Software 3D Projection Pipeline in Pygame
# Keys: 1 = Orthographic, 2 = Cavalier, 3 = Cabinet, 4 = Perspective
#       W/S rotate X, A/D rotate Y, Q/E rotate Z, R = reset, F12 = screenshot, ESC = quit
import pygame, math, sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Activity 4: Software 3D Projection Pipeline')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# 3D Cube Definition: 8 Vertices (x, y, z) centered at origin
cube_vertices = [
    [-100, -100, -100], [100, -100, -100], [100, 100, -100], [-100, 100, -100],
    [-100, -100, 100], [100, -100, 100], [100, 100, 100], [-100, 100, 100]
]
# 12 Edges connecting vertices
cube_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)
]


# ---------- Projections ----------
def project_orthographic(x, y, z):
    return int(x + 400), int(y + 300)

def project_oblique(x, y, z, mode='cavalier', phi_deg=30):
    phi = math.radians(phi_deg)
    L1 = 1.0 if mode == 'cavalier' else 0.5  # 1.0 for Cavalier (45 deg), 0.5 for Cabinet (63.4 deg)
    xp = x + z * L1 * math.cos(phi)
    yp = y + z * L1 * math.sin(phi)
    return int(xp + 400), int(yp + 300)

def project_perspective(x, y, z, D=400):
    distance = z + D
    if distance == 0: distance = 0.001
    xp = (x * D) / distance
    yp = (y * D) / distance
    return int(xp + 400), int(yp + 300)


# ---------- Task 4.2: Rotation (applied BEFORE projection) ----------
def rotate(point, ax, ay, az):
    x, y, z = point
    # rotate around X
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    # rotate around Y
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    # rotate around Z
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return x, y, z


mode = 1
names = {1: 'Orthographic', 2: 'Cavalier Oblique (L1 = 1.0)',
         3: 'Cabinet Oblique (L1 = 0.5)', 4: 'One-Point Perspective (D = 400)'}
ax = ay = az = 0.0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                mode = event.key - pygame.K_0          # Task 4.3: switch projection
            elif event.key == pygame.K_r:
                ax = ay = az = 0.0
            elif event.key == pygame.K_F12:
                pygame.image.save(screen, 'screenshot_mode%d.png' % mode)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: ax += 0.03
    if keys[pygame.K_s]: ax -= 0.03
    if keys[pygame.K_a]: ay += 0.03
    if keys[pygame.K_d]: ay -= 0.03
    if keys[pygame.K_q]: az += 0.03
    if keys[pygame.K_e]: az -= 0.03

    # Task 4.1: rotate -> project every vertex
    points = []
    for v in cube_vertices:
        x, y, z = rotate(v, ax, ay, az)
        if mode == 1:
            points.append(project_orthographic(x, y, z))
        elif mode == 2:
            points.append(project_oblique(x, y, z, 'cavalier'))
        elif mode == 3:
            points.append(project_oblique(x, y, z, 'cabinet'))
        else:
            points.append(project_perspective(x, y, z))

    screen.fill((20, 24, 35))

    # Task 4.4: in perspective, extend the 4 edges that run along z to the vanishing point.
    # With no rotation they all meet at the centre of projection (400, 300).
    if mode == 4 and ax == ay == az == 0:
        for a, b in cube_edges[8:]:
            pygame.draw.line(screen, (255, 90, 140), points[a], (400, 300), 1)
        pygame.draw.circle(screen, (255, 90, 140), (400, 300), 5)
        screen.blit(font.render('vanishing point', True, (255, 90, 140)), (410, 305))

    # draw back face (blue), receding edges (green), then front face (orange) on top
    colors = [(255, 180, 70)] * 4 + [(90, 160, 255)] * 4 + [(120, 220, 150)] * 4
    for i in [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3]:
        a, b = cube_edges[i]
        pygame.draw.line(screen, colors[i], points[a], points[b], 3)

    screen.blit(font.render('%d: %s' % (mode, names[mode]), True, (255, 255, 255)), (15, 15))
    screen.blit(font.render('1-4 change mode   WASD/QE rotate   R reset', True, (150, 150, 170)), (15, 45))
    pygame.display.flip()
    clock.tick(60)
