import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Camera / Mouse Control State
rot_x = 0.0
rot_y = 0.0
last_mouse_x = 0
last_mouse_y = 0
is_mouse_dragging = False
zoom_distance = 180.0

def draw_light_brown_larry():
    glPushMatrix()
    
    # Scaled down to be smaller than the zombie/normal enemies
    glScalef(0.40, 0.40, 0.40)
    
    # Palette definition for Light Brown Color
    c_body        = (0.76, 0.60, 0.42)     # Light brown main body/head
    c_dark_brown  = (0.45, 0.32, 0.20)     # Darker warm brown for outer ears & eyelids
    c_inner_ear   = (0.88, 0.78, 0.65)     # Cream / soft tan inner ear flat triangle
    c_eye_white   = (0.95, 0.95, 0.95)     # White sclera
    c_pupil       = (0.10, 0.07, 0.05)     # Deep dark brown eyeball/pupil
    c_nose_mouth  = (0.98, 0.95, 0.92)     # Off-white / cream nose and mouth line
    c_whisker     = (0.35, 0.24, 0.15)     # Deep brown whiskers

    # 1. Main Body / Lower Torso 
    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 45)
    glScalef(1.2, 0.6, 0.9)
    glutSolidCube(100)
    glPopMatrix()

    # 2. Rounded Head (Head center is at Z = 100)
    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 100)
    glScalef(1.2, 0.6, 0.8)
    gluSphere(gluNewQuadric(), 50, 16, 16)
    glPopMatrix()

    # 3. Pointed Ears with Flat Cream Triangle Insets
    # Left Ear Outer (Dark Brown Cone)
    glPushMatrix()
    glColor3f(*c_dark_brown)
    glTranslatef(-32, 0, 115)
    glRotatef(-8, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 20, 0, 65, 12, 12)
    glPopMatrix()

    # Left Inner Ear (Flat Cream Triangle on Front Surface)
    glPushMatrix()
    glColor3f(*c_inner_ear)
    glTranslatef(-32, 0, 115)
    glRotatef(-8, 0, 1, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(-7, 19, 8)
    glVertex3f(7, 19, 8)
    glVertex3f(0, 9, 45)
    glEnd()
    glPopMatrix()

    # Right Ear Outer (Dark Brown Cone)
    glPushMatrix()
    glColor3f(*c_dark_brown)
    glTranslatef(32, 0, 115)
    glRotatef(8, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 20, 0, 65, 12, 12)
    glPopMatrix()
    
    # Right Inner Ear (Flat Cream Triangle on Front Surface)
    glPushMatrix()
    glColor3f(*c_inner_ear)
    glTranslatef(32, 0, 115)
    glRotatef(8, 0, 1, 0)
    glBegin(GL_TRIANGLES)
    glVertex3f(-7, 19, 8)
    glVertex3f(7, 19, 8)
    glVertex3f(0, 9, 45)
    glEnd()
    glPopMatrix()
    
    # 4. Perfectly Centered Eyes (Head Center Z = 100)
    # Left Eye: Pure White Base
    glPushMatrix()
    glColor3f(*c_eye_white)
    glTranslatef(-22, 30, 100)
    glScalef(1.0, 0.2, 1.0)
    gluSphere(gluNewQuadric(), 16, 14, 14)
    glPopMatrix()

    # Left Eyeball
    glPushMatrix()
    glColor3f(*c_pupil)
    glTranslatef(-22, 32, 106)
    glScalef(0.65, 0.25, 0.9)
    gluSphere(gluNewQuadric(), 9.5, 12, 12)
    glPopMatrix()

    # Left Eyelid
    glPushMatrix()
    glColor3f(*c_dark_brown)
    glTranslatef(-22, 32, 113)
    glScalef(0.38, 0.15, 0.12)
    glutSolidCube(100)
    glPopMatrix()

    # Right Eye: Pure White Base
    glPushMatrix()
    glColor3f(*c_eye_white)
    glTranslatef(22, 30, 100)
    glScalef(1.0, 0.2, 1.0)
    gluSphere(gluNewQuadric(), 16, 14, 14)
    glPopMatrix()

    # Right Eyeball
    glPushMatrix()
    glColor3f(*c_pupil)
    glTranslatef(22, 32, 106)
    glScalef(0.65, 0.25, 0.9)
    gluSphere(gluNewQuadric(), 9.5, 12, 12)
    glPopMatrix()

    # Right Eyelid
    glPushMatrix()
    glColor3f(*c_dark_brown)
    glTranslatef(22, 32, 113)
    glScalef(0.38, 0.15, 0.12)
    glutSolidCube(100)
    glPopMatrix()

    # 5. Nose & Mouth
    # Rounded Nose
    glPushMatrix()
    glColor3f(*c_nose_mouth)
    glTranslatef(0, 31, 88)
    glScalef(1.0, 0.3, 0.8)
    gluSphere(gluNewQuadric(), 3.8, 8, 8)
    glPopMatrix()

    # Vertical Philtrum Line
    glPushMatrix()
    glColor3f(*c_nose_mouth)
    glTranslatef(0, 31, 80)
    glScalef(0.02, 0.02, 0.12)
    glutSolidCube(100)
    glPopMatrix()

    # Inverted-V Mouth
    glPushMatrix()
    glColor3f(*c_nose_mouth)
    glTranslatef(-3, 31, 74)
    glRotatef(35, 0, 1, 0)
    glScalef(0.08, 0.02, 0.02)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_nose_mouth)
    glTranslatef(3, 31, 74)
    glRotatef(-35, 0, 1, 0)
    glScalef(0.08, 0.02, 0.02)
    glutSolidCube(100)
    glPopMatrix()

    # 6. Whiskers
    glLineWidth(2.5)
    glColor3f(*c_whisker)
    glBegin(GL_LINES)
    # Left Whiskers
    glVertex3f(-45, 10, 104)
    glVertex3f(-95, 10, 108)
    glVertex3f(-45, 10, 96)
    glVertex3f(-98, 10, 96)
    glVertex3f(-45, 10, 88)
    glVertex3f(-95, 10, 84)

    # Right Whiskers
    glVertex3f(45, 10, 104)
    glVertex3f(95, 10, 108)
    glVertex3f(45, 10, 96)
    glVertex3f(98, 10, 96)
    glVertex3f(45, 10, 88)
    glVertex3f(95, 10, 84)
    glEnd()

    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Camera centered on the smaller character
    gluLookAt(0, zoom_distance, 40,
              0, 0, 40,
              0, 0, 1)
    
    # Apply Interactive Rotations around the character's scaled center
    glPushMatrix()
    glTranslatef(0, 0, 40)
    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 0, 1)
    glTranslatef(0, 0, -40)
    
    draw_light_brown_larry()
    glPopMatrix()
    
    glutSwapBuffers()

def mouse(button, state, x, y):
    global is_mouse_dragging, last_mouse_x, last_mouse_y, zoom_distance
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            is_mouse_dragging = True
            last_mouse_x = x
            last_mouse_y = y
        elif state == GLUT_UP:
            is_mouse_dragging = False
            
    # Mouse Wheel Zooming
    elif button == 3 and state == GLUT_DOWN:  # Scroll Up -> Zoom In
        zoom_distance = max(60.0, zoom_distance - 15.0)
        glutPostRedisplay()
    elif button == 4 and state == GLUT_DOWN:  # Scroll Down -> Zoom Out
        zoom_distance = min(500.0, zoom_distance + 15.0)
        glutPostRedisplay()

def motion(x, y):
    global rot_x, rot_y, last_mouse_x, last_mouse_y
    if is_mouse_dragging:
        dx = x - last_mouse_x
        dy = y - last_mouse_y
        
        rot_y += dx * 0.5
        rot_x += dy * 0.5
        
        last_mouse_x = x
        last_mouse_y = y
        glutPostRedisplay()

def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, w / float(h), 1.0, 2000.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Light Brown Larry 3D Interactive Viewer")
    
    glClearColor(0.88, 0.88, 0.90, 1.0)
    glEnable(GL_DEPTH_TEST)
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutMainLoop()

if __name__ == "__main__":
    main()