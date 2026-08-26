from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys

rot_x = 15.0
rot_y = -30.0
last_x, last_y = 0, 0
mouse_down = False

def draw_zombie_enemy():
    glPushMatrix()
    
    # Palette
    c_skin = (112/255, 168/255, 59/255)
    c_hair = (46/255, 94/255, 33/255)
    c_eye_nose = (18/255, 18/255, 18/255)
    c_shirt = (0/255, 168/255, 222/255)
    c_pants = (36/255, 68/255, 184/255)
    c_shoes = (64/255, 64/255, 64/255)

    # 1. Head
    glPushMatrix()
    glColor3f(*c_skin)
    glTranslatef(0, 0, 140)
    glScalef(0.6, 0.6, 0.6)
    glutSolidCube(100)
    glPopMatrix()

    # Hair / Trim
    glPushMatrix()
    glColor3f(*c_hair)
    glTranslatef(0, 0, 162)
    glScalef(0.64, 0.64, 0.2)
    glutSolidCube(100)
    glPopMatrix()

    # Left Eye
    glPushMatrix()
    glColor3f(*c_eye_nose)
    glTranslatef(-14, 31, 142)
    glScalef(0.18, 0.04, 0.08)
    glutSolidCube(100)
    glPopMatrix()

    # Right Eye
    glPushMatrix()
    glColor3f(*c_eye_nose)
    glTranslatef(14, 31, 142)
    glScalef(0.18, 0.04, 0.08)
    glutSolidCube(100)
    glPopMatrix()

    # Nose Block
    glPushMatrix()
    glColor3f(*c_hair)
    glTranslatef(0, 31, 134)
    glScalef(0.14, 0.04, 0.08)
    glutSolidCube(100)
    glPopMatrix()

    # 2. Torso
    glPushMatrix()
    glColor3f(*c_shirt)
    glTranslatef(0, 0, 80)
    glScalef(0.6, 0.3, 0.6)
    glutSolidCube(100)
    glPopMatrix()

    # 3. Arms (Cyan short sleeves at the base, green forearms reaching forward)
    # Left Arm - Green Forearm & Hand
    glPushMatrix()
    glColor3f(*c_skin)
    glTranslatef(-39.8, 28, 92)
    glScalef(0.2, 0.45, 0.24)
    glutSolidCube(100)
    glPopMatrix()

    # Left Arm - Cyan Sleeve
    glPushMatrix()
    glColor3f(*c_shirt)
    glTranslatef(-39.8, 5, 92)
    glScalef(0.21, 0.4, 0.25)
    glutSolidCube(100)
    glPopMatrix()

    # Right Arm - Green Forearm & Hand
    glPushMatrix()
    glColor3f(*c_skin)
    glTranslatef(39.8, 28, 92)
    glScalef(0.2, 0.45, 0.24)
    glutSolidCube(100)
    glPopMatrix()

    # Right Arm - Cyan Sleeve
    glPushMatrix()
    glColor3f(*c_shirt)
    glTranslatef(39.8, 5, 92)
    glScalef(0.21, 0.4, 0.25)
    glutSolidCube(100)
    glPopMatrix()

    # 4. Legs
    glPushMatrix()
    glColor3f(*c_pants)
    glTranslatef(-16, 0, 30)
    glScalef(0.26, 0.26, 0.4)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_pants)
    glTranslatef(16, 0, 30)
    glScalef(0.26, 0.26, 0.4)
    glutSolidCube(100)
    glPopMatrix()

    # 5. Feet
    glPushMatrix()
    glColor3f(*c_shoes)
    glTranslatef(-16, 2, 5)
    glScalef(0.26, 0.3, 0.1)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_shoes)
    glTranslatef(16, 2, 5)
    glScalef(0.26, 0.3, 0.1)
    glutSolidCube(100)
    glPopMatrix()

    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(0, 450, 90,   0, 0, 90,   0, 0, 1)

    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 0, 1)

    draw_zombie_enemy()
    glutSwapBuffers()

def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, w / float(h), 1.0, 2000.0)
    glMatrixMode(GL_MODELVIEW)

def mouse(button, state, x, y):
    global mouse_down, last_x, last_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_down = True
            last_x, last_y = x, y
        elif state == GLUT_UP:
            mouse_down = False

def motion(x, y):
    global rot_x, rot_y, last_x, last_y
    if mouse_down:
        rot_y += (x - last_x) * 0.5
        rot_x += (y - last_y) * 0.5
        last_x, last_y = x, y
        glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"3D Zombie Enemy Viewer")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.12, 0.12, 0.15, 1.0)

    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)

    glutMainLoop()

if __name__ == '__main__':
    main()