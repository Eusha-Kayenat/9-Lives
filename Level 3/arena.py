import sys
import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# =============================================================================
#  BOSS FIGHT ARENA  -  single file
#  Only GL functions from LAB 01, LAB 1.2, LAB 02, LAB 03.
#
#  COORDINATE RULE for pillars (applies after glRotatef(-90, 1,0,0)):
#    local +Z  -->  world +Y  (UP)
#  gluCylinder draws along +Z, so it is automatically correct.
#  All manual glVertex3f inside a rotated pillar context:
#    arg1 = local X, arg2 = local Y, arg3 = local Z (= height)
# =============================================================================

ARENA_RADIUS  = 550.0
WALL_HEIGHT   = 110.0

# Inner ring  -  SMALL plain ash-colored cylinder pillars
INNER_RING_R  = 200.0
INNER_COUNT   = 8
INNER_BASE_R  = 8.0
INNER_TOP_R   = 8.0     # uniform radius = straight cylinder
INNER_HEIGHT  = 48.0

# Outer ring  -  LARGE imposing decorated pillars
OUTER_RING_R  = 400.0
OUTER_COUNT   = 8
OUTER_BASE_R  = 16.0
OUTER_TOP_R   = 12.0
OUTER_HEIGHT  = 100.0

WIN_W, WIN_H  = 900, 900

# =============================================================================
#  CAMERA
# =============================================================================
cam_h    =  20.0
cam_v    =  12.0
cam_dist = 480.0
look_y   =  22.0
dragging = False
last_mx  = 0
last_my  = 0

_Q = None
def Q():
    global _Q
    if _Q is None:
        _Q = gluNewQuadric()
    return _Q

def camera_position():
    """World-space camera position, used both for the view matrix and for
    painter's-algorithm (back-to-front) depth sorting, since depth testing
    is not available without glEnable."""
    rh = math.radians(cam_h); rv = math.radians(cam_v)
    ex = cam_dist*math.cos(rv)*math.sin(rh)
    ey = cam_dist*math.sin(rv)
    ez = cam_dist*math.cos(rv)*math.cos(rh)
    return ex, ey, ez

def _dist_sq(px, py, pz, cx, cy, cz):
    dx = px-cx; dy = py-cy; dz = pz-cz
    return dx*dx + dy*dy + dz*dz

# =============================================================================
#  FLOOR  -  lava base disc + cracked magma plates
# =============================================================================
_floor_cache = None

def _build_floor():
    global _floor_cache
    _floor_cache = {'lava': [], 'plates': []}
    S = 60
    for i in range(S):
        t1 = 2*math.pi*i/S;  t2 = 2*math.pi*(i+1)/S
        _floor_cache['lava'].append((
            (0, 0, 0),
            (ARENA_RADIUS*math.cos(t1), 0, ARENA_RADIUS*math.sin(t1)),
            (ARENA_RADIUS*math.cos(t2), 0, ARENA_RADIUS*math.sin(t2)),
        ))
    rng    = random.Random(7)
    step   = 22.0
    half   = int(ARENA_RADIUS/step) + 2
    shrink = 0.80
    verts  = {}
    for i in range(-half, half+1):
        for j in range(-half, half+1):
            x = i*step + rng.uniform(-step*0.38, step*0.38)
            z = j*step + rng.uniform(-step*0.38, step*0.38)
            verts[(i,j)] = (x, z)
    for i in range(-half, half):
        for j in range(-half, half):
            v1=verts[(i,j)];    v2=verts[(i+1,j)]
            v3=verts[(i+1,j+1)]; v4=verts[(i,j+1)]
            cx = (v1[0]+v2[0]+v3[0]+v4[0]) / 4
            cz = (v1[1]+v2[1]+v3[1]+v4[1]) / 4
            if cx*cx + cz*cz > ARENA_RADIUS*ARENA_RADIUS: continue
            def s(v, cx=cx, cz=cz):
                return (cx+(v[0]-cx)*shrink, cz+(v[1]-cz)*shrink)
            w1=s(v1); w2=s(v2); w3=s(v3); w4=s(v4)
            _floor_cache['plates'].extend([
                (w1[0],0.18,w1[1]),(w2[0],0.18,w2[1]),
                (w3[0],0.18,w3[1]),(w4[0],0.18,w4[1]),
            ])

def draw_floor():
    if _floor_cache is None: _build_floor()
    glBegin(GL_TRIANGLES)
    for tri in _floor_cache['lava']:
        glColor3f(0.80,0.26,0.0); glVertex3f(*tri[0])
        glColor3f(0.52,0.08,0.0); glVertex3f(*tri[1]); glVertex3f(*tri[2])
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.07,0.02,0.02)
    for v in _floor_cache['plates']: glVertex3f(*v)
    glEnd()

def draw_floor_occluder():
    """Large near-black disc just below y=0 hides geometry undersides."""
    glBegin(GL_TRIANGLES)
    glColor3f(0.02, 0.01, 0.01)
    S = 48; R = ARENA_RADIUS + 250.0
    for i in range(S):
        t1=2*math.pi*i/S; t2=2*math.pi*(i+1)/S
        glVertex3f(0, -2, 0)
        glVertex3f(R*math.cos(t1), -2, R*math.sin(t1))
        glVertex3f(R*math.cos(t2), -2, R*math.sin(t2))
    glEnd()

# =============================================================================
#  BOUNDARY WALL
# =============================================================================
_wall_cache = None

WALL_COLORS = {'out': (0.13,0.045,0.04), 'inn': (0.13,0.045,0.04), 'top': (0.13,0.045,0.04)}

def _build_wall():
    global _wall_cache
    # Each entry is (representative_point, [(color, quad), (color, quad), (color, quad)])
    # Grouping all 3 faces of a segment together (instead of sorting every quad
    # independently) stops faces from *different* segments interleaving with
    # each other when their individual centers happen to tie in distance -
    # that interleaving was what made the far rim look broken/see-through.
    segments = []
    S=72; thick=20.0; Ro=ARENA_RADIUS; Ri=ARENA_RADIUS-thick
    for i in range(S):
        a1=2*math.pi*i/S; a2=2*math.pi*(i+1)/S
        ox1,oz1 = Ro*math.cos(a1), Ro*math.sin(a1)
        ox2,oz2 = Ro*math.cos(a2), Ro*math.sin(a2)
        ix1,iz1 = Ri*math.cos(a1), Ri*math.sin(a1)
        ix2,iz2 = Ri*math.cos(a2), Ri*math.sin(a2)
        out_q = ((ox1,0,oz1),(ox2,0,oz2),(ox2,WALL_HEIGHT,oz2),(ox1,WALL_HEIGHT,oz1))
        inn_q = ((ix2,0,iz2),(ix1,0,iz1),(ix1,WALL_HEIGHT,iz1),(ix2,WALL_HEIGHT,iz2))
        top_q = ((ix1,WALL_HEIGHT,iz1),(ix2,WALL_HEIGHT,iz2),(ox2,WALL_HEIGHT,oz2),(ox1,WALL_HEIGHT,oz1))
        mid_a = (a1+a2)/2.0
        rep_point = (Ro*math.cos(mid_a), WALL_HEIGHT*0.5, Ro*math.sin(mid_a))
        segments.append((rep_point, [
            (WALL_COLORS['out'], out_q),
            (WALL_COLORS['inn'], inn_q),
            (WALL_COLORS['top'], top_q),
        ]))
    _wall_cache = segments

def draw_wall_rim_accent():
    """Thin decorative line ring near the base of the wall - drawn separately
    since it's a non-occluding accent, not a solid surface."""
    Ri = ARENA_RADIUS - 20.0
    glBegin(GL_LINES)
    glColor3f(0.92,0.32,0.0)
    for i in range(72):
        a1=2*math.pi*i/72; a2=2*math.pi*(i+1)/72
        glVertex3f(Ri*math.cos(a1),0.8,Ri*math.sin(a1))
        glVertex3f(Ri*math.cos(a2),0.8,Ri*math.sin(a2))
    glEnd()

# =============================================================================
#  CEILING RIM  (open ring - no solid dome so view is never blocked)
# =============================================================================
def draw_ceiling_rim():
    for r_off, col in [(0,(0.50,0.05,0.05)),(10,(0.35,0.03,0.03)),(20,(0.22,0.02,0.02))]:
        r = ARENA_RADIUS - r_off
        glBegin(GL_LINES)
        glColor3f(*col)
        for i in range(80):
            a1=2*math.pi*i/80; a2=2*math.pi*(i+1)/80
            glVertex3f(r*math.cos(a1), WALL_HEIGHT, r*math.sin(a1))
            glVertex3f(r*math.cos(a2), WALL_HEIGHT, r*math.sin(a2))
        glEnd()

# =============================================================================
#  SMALL PILLAR  -  plain ash-colored cylinder, no decorations
#  Called inside glRotatef(-90,1,0,0) so local +Z = world +Y (up)
# =============================================================================
def draw_small_pillar():
    segs = 20

    # Side surface (ash grey)
    glColor3f(0.55, 0.54, 0.51)
    gluCylinder(Q(), INNER_BASE_R, INNER_TOP_R, INNER_HEIGHT, segs, 1)

    # gluCylinder never draws its end caps, so without this the top of the
    # pillar is an open ring - fill it with a manual triangle fan.
    glBegin(GL_TRIANGLES)
    glColor3f(0.55, 0.54, 0.51)
    for i in range(segs):
        a1 = 2*math.pi*i/segs; a2 = 2*math.pi*(i+1)/segs
        glVertex3f(0, 0, INNER_HEIGHT)
        glVertex3f(INNER_TOP_R*math.cos(a1), INNER_TOP_R*math.sin(a1), INNER_HEIGHT)
        glVertex3f(INNER_TOP_R*math.cos(a2), INNER_TOP_R*math.sin(a2), INNER_HEIGHT)
    glEnd()


def draw_large_pillar():
    segs = 20
    H    = OUTER_HEIGHT
    Rb   = OUTER_BASE_R
    Rt   = OUTER_TOP_R

    # 1. Square base plinth  (local Z = height)
    plinth_h = 9.0
    pw = Rb * 1.55
    glBegin(GL_QUADS)
    glColor3f(0.15, 0.05, 0.05)
    for dx,dy,ex,ey in [(-pw,-pw,pw,-pw),(pw,-pw,pw,pw),(pw,pw,-pw,pw),(-pw,pw,-pw,-pw)]:
        glVertex3f(dx, dy, 0)
        glVertex3f(ex, ey, 0)
        glVertex3f(ex, ey, plinth_h)
        glVertex3f(dx, dy, plinth_h)
    glColor3f(0.22, 0.08, 0.06)
    glVertex3f(-pw,-pw,plinth_h); glVertex3f(pw,-pw,plinth_h)
    glVertex3f( pw, pw,plinth_h); glVertex3f(-pw, pw,plinth_h)
    glEnd()

    glPushMatrix()
    glTranslatef(0, 0, plinth_h)         # move up by plinth (local Z = up)
    body_h = H - plinth_h - 12.0

    # 2. Main dark stone cylinder
    glColor3f(0.14, 0.045, 0.04)
    gluCylinder(Q(), Rb, Rt, body_h, segs, 1)

    # 3. Decorative stone band rings
    for frac in [0.0, 0.33, 0.66, 1.0]:
        bp = frac * body_h
        br = Rb + (Rt-Rb)*frac + 2.8
        bh = 6.0
        glPushMatrix()
        glTranslatef(0, 0, bp)           # move to band height (local Z)
        glColor3f(0.10, 0.03, 0.03)
        gluCylinder(Q(), br, br, bh, segs, 1)
        glBegin(GL_TRIANGLES)
        glColor3f(0.20, 0.07, 0.05)
        for i in range(segs):
            a1=2*math.pi*i/segs; a2=2*math.pi*(i+1)/segs
            glVertex3f(0, 0, bh)
            glVertex3f(br*math.cos(a2), br*math.sin(a2), bh)
            glVertex3f(br*math.cos(a1), br*math.sin(a1), bh)
        glEnd()
        glPopMatrix()

    glPopMatrix()

    # 5. Capital block at top  (local Z = cap_z)
    cap_z = H - 12.0; cap_w = Rt*1.80; cap_h = 12.0
    glBegin(GL_QUADS)
    glColor3f(0.13, 0.04, 0.04)
    for dx,dy,ex,ey in [(-cap_w,-cap_w,cap_w,-cap_w),(cap_w,-cap_w,cap_w,cap_w),
                         (cap_w,cap_w,-cap_w,cap_w),(-cap_w,cap_w,-cap_w,-cap_w)]:
        glVertex3f(dx, dy, cap_z)
        glVertex3f(ex, ey, cap_z)
        glVertex3f(ex, ey, cap_z+cap_h)
        glVertex3f(dx, dy, cap_z+cap_h)
    glColor3f(0.24, 0.09, 0.07)
    glVertex3f(-cap_w,-cap_w,cap_z+cap_h); glVertex3f(cap_w,-cap_w,cap_z+cap_h)
    glVertex3f( cap_w, cap_w,cap_z+cap_h); glVertex3f(-cap_w, cap_w,cap_z+cap_h)
    glEnd()

# =============================================================================
#  PLACE ALL PILLARS
# =============================================================================
def _pillar_layout():
    """(world_x, world_z, kind) for every pillar, inner and outer combined."""
    layout = []
    for k in range(INNER_COUNT):
        angle = 2*math.pi * k / INNER_COUNT
        layout.append((INNER_RING_R*math.cos(angle), INNER_RING_R*math.sin(angle), 'small'))
    for k in range(OUTER_COUNT):
        angle = 2*math.pi * k / OUTER_COUNT
        layout.append((OUTER_RING_R*math.cos(angle), OUTER_RING_R*math.sin(angle), 'large'))
    return layout

def draw_wall_and_pillars():
    """Depth-sort the wall segments and the pillars TOGETHER in a single
    back-to-front pass.

    Previously the wall was drawn entirely first and pillars entirely after,
    unconditionally - so a pillar sitting behind a near wall segment would
    still get painted on top of it, making the wall look transparent from
    certain angles. Merging both into one combined sort (the only option
    without glEnable(GL_DEPTH_TEST)) means whichever object is actually
    closer to the camera - wall segment or pillar - is always drawn last.
    """
    if _wall_cache is None: _build_wall()
    cx, cy, cz = camera_position()

    jobs = []  # (dist_sq, 'wall'|'small'|'large', payload)
    for rep_point, quads in _wall_cache:
        d = _dist_sq(rep_point[0], rep_point[1], rep_point[2], cx, cy, cz)
        jobs.append((d, 'wall', quads))
    for x, z, kind in _pillar_layout():
        mid_h = (INNER_HEIGHT if kind == 'small' else OUTER_HEIGHT) * 0.5
        d = _dist_sq(x, mid_h, z, cx, cy, cz)
        jobs.append((d, kind, (x, z)))

    jobs.sort(key=lambda j: -j[0])

    for _, kind, payload in jobs:
        if kind == 'wall':
            for color, q in payload:
                glBegin(GL_QUADS)
                glColor3f(*color)
                for v in q: glVertex3f(*v)
                glEnd()
        else:
            x, z = payload
            glPushMatrix()
            glTranslatef(x, 0.0, z)
            glRotatef(-90.0, 1.0, 0.0, 0.0)   # local +Z now = world +Y
            if kind == 'small':
                draw_small_pillar()
            else:
                draw_large_pillar()
            glPopMatrix()

# =============================================================================
#  CAMERA
# =============================================================================
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55.0, WIN_W/float(WIN_H), 1.0, 4000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    ex, ey, ez = camera_position()
    gluLookAt(ex, ey, ez,  0, look_y, 0,  0, 1, 0)

# =============================================================================
#  DISPLAY
# =============================================================================
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_camera()
    draw_floor_occluder()
    draw_floor()
    draw_wall_rim_accent()
    draw_ceiling_rim()
    draw_wall_and_pillars()
    glutSwapBuffers()

# =============================================================================
#  INPUT
# =============================================================================
def keyboard(key, x, y):
    global cam_dist
    if key in (b'q', b'\x1b'): sys.exit(0)
    if key in (b'+', b'='): cam_dist = max(80,   cam_dist - 30)
    if key == b'-':          cam_dist = min(1800, cam_dist + 30)
    glutPostRedisplay()

def special(key, x, y):
    global cam_h, cam_v
    if   key == GLUT_KEY_LEFT:  cam_h -= 4
    elif key == GLUT_KEY_RIGHT: cam_h += 4
    elif key == GLUT_KEY_UP:    cam_v = min(85, cam_v + 3)
    elif key == GLUT_KEY_DOWN:  cam_v = max(4,  cam_v - 3)
    glutPostRedisplay()

def mouse_btn(btn, state, x, y):
    global dragging, last_mx, last_my, cam_dist
    if btn == GLUT_LEFT_BUTTON:
        dragging = (state == GLUT_DOWN)
        last_mx, last_my = x, y
    if btn == 3 and state == GLUT_DOWN: cam_dist=max(80,   cam_dist-20); glutPostRedisplay()
    if btn == 4 and state == GLUT_DOWN: cam_dist=min(1800, cam_dist+20); glutPostRedisplay()

def mouse_move(x, y):
    global cam_h, cam_v, last_mx, last_my
    if not dragging: return
    cam_h += (x-last_mx)*0.45
    cam_v  = max(4, min(85, cam_v-(y-last_my)*0.45))
    last_mx, last_my = x, y
    glutPostRedisplay()

# =============================================================================
#  MAIN
# =============================================================================
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(80, 60)
    glutCreateWindow(b"Boss Fight Arena")
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutMouseFunc(mouse_btn)
    glutMotionFunc(mouse_move)
    glutMainLoop()

if __name__ == "__main__":
    main()
