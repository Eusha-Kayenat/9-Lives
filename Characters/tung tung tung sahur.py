from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys

# Camera rotation angles
rot_x = 15.0
rot_y = -30.0
last_x, last_y = 0, 0
mouse_down = False

def drawCharacter():
    glPushMatrix()
    
    # Base palette from pixel art
    c_body = (222/255, 137/255, 34/255)
    c_dark = (117/255, 76/255, 18/255)
    c_goggle = (229/255, 230/255, 230/255)
    c_white = (1.0, 1.0, 1.0)

    # 1. Main Body
    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 120)
    glScalef(0.65, 0.4, 1.8)
    glutSolidCube(100)
    glPopMatrix()

    # 2. Left Eye / Goggle
    glPushMatrix()
    glColor3f(*c_goggle)
    glTranslatef(-16, 21, 160)
    glScalef(0.28, 0.08, 0.35)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_white)
    glTranslatef(-16, 25, 160)
    glScalef(0.18, 0.08, 0.22)
    glutSolidCube(100)
    glPopMatrix()

    # Pupil (Left)
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(-16, 29, 160)
    glScalef(0.08, 0.05, 0.1)
    glutSolidCube(100)
    glPopMatrix()

    # 3. Right Eye / Goggle
    glPushMatrix()
    glColor3f(*c_goggle)
    glTranslatef(16, 21, 160)
    glScalef(0.28, 0.08, 0.35)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_white)
    glTranslatef(16, 25, 160)
    glScalef(0.18, 0.08, 0.22)
    glutSolidCube(100)
    glPopMatrix()

    # Pupil (Right)
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(16, 29, 160)
    glScalef(0.08, 0.05, 0.1)
    glutSolidCube(100)
    glPopMatrix()

    # Eyebrows
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(-16, 22, 185)
    glScalef(0.25, 0.06, 0.06)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(16, 22, 185)
    glScalef(0.25, 0.06, 0.06)
    glutSolidCube(100)
    glPopMatrix()

    # 4. Nose & Smirking Line
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(0, 22, 138)
    glScalef(0.06, 0.06, 0.16)
    glutSolidCube(100)
    glPopMatrix()

    # Smile Horizontal Line
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(-2, 22, 122)
    glScalef(0.38, 0.06, 0.06)
    glutSolidCube(100)
    glPopMatrix()

    # Left Upturn
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(-21, 22, 130)
    glScalef(0.06, 0.06, 0.14)
    glutSolidCube(100)
    glPopMatrix()

    # Right Upturn
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(17, 22, 128)
    glScalef(0.06, 0.06, 0.10)
    glutSolidCube(100)
    glPopMatrix()

    # 5. Arms
    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(-38.5, 0, 95)
    glScalef(0.12, 0.2, 0.9)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(38.5, 0, 95)
    glScalef(0.12, 0.2, 0.9)
    glutSolidCube(100)
    glPopMatrix()

    # 6. Legs
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(-14, 0, 18)
    glScalef(0.12, 0.15, 0.6)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(14, 0, 18)
    glScalef(0.12, 0.15, 0.6)
    glutSolidCube(100)
    glPopMatrix()

    # Feet
    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(-14, 10, -8)
    glScalef(0.2, 0.35, 0.12)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_dark)
    glTranslatef(14, 10, -8)
    glScalef(0.2, 0.35, 0.12)
    glutSolidCube(100)
    glPopMatrix()

    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Set camera view pointing towards character center
    gluLookAt(0, 450, 120,   0, 0, 120,   0, 0, 1)

    # Interactive 3D rotations
    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 0, 1)

    drawCharacter()
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
    glutCreateWindow(b"3D Character Viewer")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.12, 0.12, 0.15, 1.0)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)

    glutMainLoop()

if __name__ == '__main__':
    main()