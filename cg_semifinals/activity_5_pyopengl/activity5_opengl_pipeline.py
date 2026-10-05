
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption('Activity 5: Hardware Pipeline with PyOpenGL')
clock = pygame.time.Clock()


glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)
glEnable(GL_DEPTH_TEST)
glClearColor(0.08, 0.09, 0.13, 1)


vertices = [
    ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), (-1, -1, -1),
    ( 1, -1,  1), ( 1,  1,  1), (-1, -1,  1), (-1,  1,  1)
]
colors = [
    (1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1), (0,1,1), (1,1,1), (0.5,0.5,0.5)
]
surfaces = [
    (0,1,2,3), (3,2,7,6), (6,7,5,4), (4,5,1,0), (1,5,7,2), (4,0,3,6)
]



def draw_colored_cube():
    glBegin(GL_QUADS)
    for surface in surfaces:
        for vertex_idx in surface:
            glColor3fv(colors[vertex_idx])
            glVertex3fv(vertices[vertex_idx])
    glEnd()


def draw_box(width, height, depth, color):
    glPushMatrix()
    glScalef(width / 2, height / 2, depth / 2)
    glColor3fv(color)
    glBegin(GL_QUADS)
    for surface in surfaces:
        for vertex_idx in surface:
            glVertex3fv(vertices[vertex_idx])
    glEnd()
    glPopMatrix()



def draw_arm(shoulder, elbow):
    glPushMatrix()
    glTranslatef(0, -2, 0)
    draw_box(1.2, 0.4, 1.2, (0.5, 0.5, 0.6))      # base

    glRotatef(shoulder, 0, 0, 1)                  # shoulder joint
    glTranslatef(0, 1, 0)
    draw_box(0.4, 2, 0.4, (0.9, 0.5, 0.2))        # upper arm

    glTranslatef(0, 1, 0)                         # move to the end of the upper arm
    glRotatef(elbow, 0, 0, 1)                     # elbow joint (follows the shoulder)
    glTranslatef(0, 0.75, 0)
    draw_box(0.3, 1.5, 0.3, (0.2, 0.6, 0.9))      # forearm
    glPopMatrix()



def draw_squares(transparent):
    alpha = 0.5 if transparent else 1.0
    if transparent:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # I = a1*I1 + (1 - a1)*I2
        glDepthMask(GL_FALSE)   
    squares = [(-0.6, 0.4, -1, (1, 0, 0)),     # red   (back)
               ( 0.0, 0.0,  0, (0, 1, 0)),     # green
               ( 0.6, -0.4, 1, (0, 0, 1))]     # blue  (front) -> drawn back to front
    for x, y, z, (r, g, b) in squares:
        glColor4f(r, g, b, alpha)
        glBegin(GL_QUADS)
        glVertex3f(x - 1, y - 1, z)
        glVertex3f(x + 1, y - 1, z)
        glVertex3f(x + 1, y + 1, z)
        glVertex3f(x - 1, y + 1, z)
        glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)


angle = 0
shoulder, elbow = -30, -45
paused = False
blending = True
depth_test = True

while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            quit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE: paused = not paused
            if event.key == K_b: blending = not blending
            if event.key == K_z: depth_test = not depth_test
            if event.key == K_F12:
                pixels = glReadPixels(0, 0, display[0], display[1], GL_RGB, GL_UNSIGNED_BYTE)
                pygame.image.save(pygame.image.fromstring(pixels, display, 'RGB', True), 'screenshot.png')

    keys = pygame.key.get_pressed()
    if keys[K_1]: shoulder += 1
    if keys[K_2]: shoulder -= 1
    if keys[K_3]: elbow += 1
    if keys[K_4]: elbow -= 1
    if not paused:
        angle += 1

    if depth_test:
        glEnable(GL_DEPTH_TEST)
    else:
        glDisable(GL_DEPTH_TEST)


    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -12)      # move the camera back
    glRotatef(15, 1, 0, 0)           # look slightly down


    glPushMatrix()
    glTranslatef(-3.5, 0, 0)
    glRotatef(angle, 1, 1, 0)
    draw_colored_cube()
    glPopMatrix()


    draw_arm(shoulder, elbow)


    glPushMatrix()
    glTranslatef(3.5, 0, 0)
    glRotatef(-30, 0, 1, 0)
    draw_squares(blending)
    glPopMatrix()

    pygame.display.set_caption('Activity 5 | blending %s | depth test %s | 1-4 move arm, B, Z, SPACE'
                               % ('ON' if blending else 'OFF', 'ON' if depth_test else 'OFF'))
    pygame.display.flip()
    clock.tick(60)
