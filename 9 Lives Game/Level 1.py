import math
import random
import sys
import time
import ctypes
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window dimensions (updated dynamically on resize)
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750
WINDOW_TITLE = b"9 Lives"

# Player state
player_pos = [0.0, 0.0, 7.4]
player_yaw = 0.0           # Character facing angle (set by movement)
camera_yaw = 0.0           # Camera orbit angle (mouse controlled)
player_pitch = 0.0
player_speed = 0.90
crouching = False
walk_cycle_phase = 0.0     # Leg-swing animation phase, advances while moving
is_walking = False
_idle_ticks_since_move = 0 # Ticks since last move; used to stop walk animation
eye_height = 1.6

# Jump physics
is_jumping = False
y_velocity = 0.0
gravity = -0.014
jump_strength = 0.28
ground_y = 0.0

first_person = False
cam_dist = 6.5
cam_height = 3.8

# Mouse look tracking
last_mouse_x = 0
last_mouse_y = 0
mouse_initialized = False
is_cursor_hidden = False

# Moving walls animation
moving_walls_offset = 0.0
moving_walls_dir = 1.0
anim_moving_walls = True

# Disappearing floor animation
platform_timer = 0
disappearing_tiles_active = [True, True, True, True, True, True]
anim_disappearing_floor = True

game_paused = False

# Hazard / life tracking
consecutive_lava_falls = 0
lava_alert_timer = 0
lava_alert_expiry = 0.0  # real-time expiry for 1-second alert
hazard_alert_text = "Fell into the lava!"
game_over = False

def trigger_hazard_alert(text):
    """Triggers hazard warning text with guaranteed 1.0-second real-time duration."""
    global hazard_alert_text, lava_alert_expiry, lava_alert_timer
    hazard_alert_text = text
    lava_alert_expiry = time.time() + 1.0
    lava_alert_timer = 60

# Moving wall crush tracking
consecutive_wall_hits = 0
wall_invincibility_timer = 0  # invincibility frames after being crushed

cheat_mode = False

# Story screen state
in_story_screen = True
story_lines = [
    "Tung Tung Tung Sahur has wandered into the Evil Cat World!",
    "Armed with 9 Lives, you must survive the traps and",
    "defeat the wicked cats trying to take over the world."
]
story_char_index = 0
story_timer = 0
total_story_len = sum(len(line) for line in story_lines)

# Color palette
COLOR_FLOOR = (0.10, 0.12, 0.15)
COLOR_FLOOR_SIDE = (0.06, 0.07, 0.09)
COLOR_WALL = (0.32, 0.33, 0.28)
COLOR_WALL_SIDE = (0.22, 0.23, 0.20)
COLOR_CEILING = (0.12, 0.13, 0.15)
COLOR_LIGHT_PANEL = (0.95, 0.95, 0.75)
COLOR_RUNNER = (0.75, 0.08, 0.12)
COLOR_GOLD_TRIM = (0.90, 0.75, 0.15)
COLOR_PILLAR = (0.16, 0.16, 0.20)
COLOR_CYAN_GLOW = (0.0, 0.85, 1.0)
COLOR_LAVA = (1.0, 0.25, 0.0)
COLOR_HAZARD_STRIPE = (0.95, 0.85, 0.1)
COLOR_LASER_RED = (1.0, 0.1, 0.2)
COLOR_LASER_CYAN = (0.0, 0.9, 1.0)
COLOR_PORTAL_CYAN = (0.0, 0.75, 1.0)

# Character palette
c_body = (222/255, 137/255, 34/255)
c_dark = (117/255, 76/255, 18/255)
c_goggle = (229/255, 230/255, 230/255)
c_white = (1.0, 1.0, 1.0)

def load_character_model():
    """Initializes character color palette."""
    global c_body, c_dark, c_goggle, c_white
    c_body = (222/255, 137/255, 34/255)
    c_dark = (117/255, 76/255, 18/255)
    c_goggle = (229/255, 230/255, 230/255)
    c_white = (1.0, 1.0, 1.0)

# -----------------------------------------------------------------------------
# 3D Primitives & 2D Text Helpers
# -----------------------------------------------------------------------------
def draw_box(sx, sy, sz, color_top=None, color_side=None):
    """Draws a solid box centered at origin with dimensions sx, sy, sz."""
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    glBegin(GL_QUADS)
    if color_top:
        glColor3f(*color_top)
    glVertex3f(-hx, hy, hz); glVertex3f(hx, hy, hz); glVertex3f(hx, hy, -hz); glVertex3f(-hx, hy, -hz)
    glVertex3f(-hx, -hy, -hz); glVertex3f(hx, -hy, -hz); glVertex3f(hx, -hy, hz); glVertex3f(-hx, -hy, hz)
    if color_side:
        glColor3f(color_side[0] * 0.9, color_side[1] * 0.9, color_side[2] * 0.9)
    glVertex3f(-hx, -hy, hz); glVertex3f(hx, -hy, hz); glVertex3f(hx, hy, hz); glVertex3f(-hx, hy, hz)
    if color_side:
        glColor3f(color_side[0] * 0.85, color_side[1] * 0.85, color_side[2] * 0.85)
    glVertex3f(-hx, hy, -hz); glVertex3f(hx, hy, -hz); glVertex3f(hx, -hy, -hz); glVertex3f(-hx, -hy, -hz)
    if color_side:
        glColor3f(color_side[0] * 0.8, color_side[1] * 0.8, color_side[2] * 0.8)
    glVertex3f(-hx, -hy, -hz); glVertex3f(-hx, -hy, hz); glVertex3f(-hx, hy, hz); glVertex3f(-hx, hy, -hz)
    if color_side:
        glColor3f(color_side[0] * 0.85, color_side[1] * 0.85, color_side[2] * 0.85)
    glVertex3f(hx, -hy, -hz); glVertex3f(hx, hy, -hz); glVertex3f(hx, hy, hz); glVertex3f(hx, -hy, hz)
    glEnd()

def draw_text(x, y, text_str, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
    """Renders 2D HUD text in orthographic overlay mode."""
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text_str:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text_bold(x, y, text_str, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
        draw_text(x + dx, y + dy, text_str, color, font)

def draw_bar_2d(x, y, w, h, fill_pct, fill_color, border_color=(0.9, 0.9, 0.9)):
    """Renders a 2D health bar with border and percentage fill."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glBegin(GL_LINES)
    glColor3f(*border_color)
    glVertex2f(x, y); glVertex2f(x + w, y)
    glVertex2f(x + w, y); glVertex2f(x + w, y + h)
    glVertex2f(x + w, y + h); glVertex2f(x, y + h)
    glVertex2f(x, y + h); glVertex2f(x, y)
    glEnd()
    fill_w = max(0.0, min(1.0, fill_pct)) * (w - 2)
    if fill_w > 0:
        glBegin(GL_QUADS)
        glColor3f(*fill_color)
        glVertex2f(x + 1, y + 1)
        glVertex2f(x + 1 + fill_w, y + 1)
        glVertex2f(x + 1 + fill_w, y + h - 1)
        glVertex2f(x + 1, y + h - 1)
        glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# -----------------------------------------------------------------------------
# Character Rendering
# -----------------------------------------------------------------------------
def draw_character(cam_x=0.0, cam_z=0.0):
    """Renders the player character model. Skipped in first-person view."""
    
    if first_person:
        return

    glPushMatrix()
    curr_y = player_pos[1]
    glTranslatef(player_pos[0], curr_y, player_pos[2])
    glRotatef(player_yaw, 0, 1, 0)

    # Align model axes: model Z (height) -> world Y, model Y (forward) -> world Z
    glRotatef(-90, 1, 0, 0)
    glRotatef(180, 0, 0, 1)

    scale_factor = 0.008
    if crouching:
        glScalef(scale_factor, scale_factor * 0.5, scale_factor)
    else:
        glScalef(scale_factor, scale_factor, scale_factor)

    glTranslatef(0, 0, 14.0)  # align soles with ground

    rad_yaw = math.radians(player_yaw)
    fwd_x = math.sin(rad_yaw)
    fwd_z = math.cos(rad_yaw)
    to_cam_x = cam_x - player_pos[0]
    to_cam_z = cam_z - player_pos[2]
    # Camera is in front when it lies in the same direction as the character's facing vector
    is_front = (fwd_x * to_cam_x + fwd_z * to_cam_z) > 0.0

    def draw_face_details():
        for eye_x in [-16, 16]:
            glPushMatrix()
            glColor3f(*c_goggle)
            glTranslatef(eye_x, 31, 160)
            glScalef(0.28, 0.08, 0.35)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_white)
            glTranslatef(eye_x, 35, 160)
            glScalef(0.18, 0.08, 0.22)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_dark)
            glTranslatef(eye_x, 39, 160)
            glScalef(0.08, 0.05, 0.1)
            glutSolidCube(100)
            glPopMatrix()

            # Eyebrow
            glPushMatrix()
            glColor3f(*c_dark)
            glTranslatef(eye_x, 32, 185)
            glScalef(0.25, 0.06, 0.06)
            glutSolidCube(100)
            glPopMatrix()

        # Nose & Smirk
        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(0, 32, 138)
        glScalef(0.06, 0.06, 0.16)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(-2, 32, 122)
        glScalef(0.38, 0.06, 0.06)
        glutSolidCube(100)
        glPopMatrix()

        # Smile upturns (left & right corners)
        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(-21, 32, 130)
        glScalef(0.06, 0.06, 0.14)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(17, 32, 128)
        glScalef(0.06, 0.06, 0.10)
        glutSolidCube(100)
        glPopMatrix()

    # Draw face before body when camera is behind (body will cover it correctly)
    if not is_front:
        draw_face_details()

    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 120)
    glScalef(0.65, 0.60, 1.8)
    glutSolidCube(100)
    glPopMatrix()

    if is_front:
        draw_face_details()

    arm_swing_amplitude = 24.0
    for side_x, phase_offset in ((-38.5, math.pi), (38.5, 0.0)):
        arm_angle = 0.0
        if is_walking:
            arm_angle = math.sin(walk_cycle_phase + phase_offset) * arm_swing_amplitude

        glPushMatrix()
        glTranslatef(side_x, 0, 135)
        glRotatef(arm_angle, 1, 0, 0)
        glTranslatef(0, 0, -40)
        glColor3f(*c_body)
        glScalef(0.12, 0.30, 0.9)
        glutSolidCube(100)
        glPopMatrix()

    leg_swing_amplitude = 28.0
    for leg_x, phase_offset in ((-14, 0.0), (14, math.pi)):
        swing_angle = 0.0
        if is_walking:
            swing_angle = math.sin(walk_cycle_phase + phase_offset) * leg_swing_amplitude

        glPushMatrix()
        glTranslatef(leg_x, 0, 18)
        glRotatef(swing_angle, 1, 0, 0)

        glPushMatrix()
        glColor3f(*c_dark)
        glScalef(0.12, 0.15, 0.6)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(0, 10, -26)
        glScalef(0.2, 0.35, 0.12)
        glutSolidCube(100)
        glPopMatrix()

        glPopMatrix()

    glPopMatrix()

# -----------------------------------------------------------------------------
# Maze Geometry: Floors, Walls, Pillars
# -----------------------------------------------------------------------------
def draw_connected_floor_pathways():
    """Draws the solid floor mesh for all maze corridors and chambers."""
    
    # Start hub floor + red carpet runner
    glPushMatrix()
    glTranslatef(0.0, -0.1, 27.0)
    draw_box(12.0, 0.2, 54.8, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.0, 0.02, 20.0)
    draw_box(3.6, 0.04, 40.0, color_top=COLOR_RUNNER, color_side=(0.4, 0.04, 0.06))
    glPopMatrix()

    glColor3f(*COLOR_GOLD_TRIM)
    glBegin(GL_LINES)
    glVertex3f(-1.8, 0.05, 0.0); glVertex3f(-1.8, 0.05, 40.0)
    glVertex3f(1.8, 0.05, 0.0); glVertex3f(1.8, 0.05, 40.0)
    glEnd()

    # Junction A floor
    glPushMatrix()
    glTranslatef(20.0, -0.1, 60.0)
    draw_box(52.0, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # (Lava pit corridor floor is rendered in draw_hazard_zones())

    # Junction B floor
    glPushMatrix()
    glTranslatef(0.0, -0.1, 120.0)
    draw_box(92.0, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # Disappearing floor entry and exit ledges
    glPushMatrix()
    glTranslatef(-40.0, -0.1, 128.0)
    draw_box(11.2, 0.2, 5.6, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-40.0, -0.1, 172.0)
    draw_box(11.2, 0.2, 5.6, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # Junction C floor
    glPushMatrix()
    glTranslatef(-10.2, -0.1, 180.0)
    draw_box(71.6, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # Laser gauntlet corridor floor
    glPushMatrix()
    glTranslatef(20.0, -0.1, 210.0)
    draw_box(11.2, 0.2, 48.8, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # Junction D floor
    glPushMatrix()
    glTranslatef(45.0, -0.1, 240.0)
    draw_box(61.2, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # Moving walls and exit chamber floor
    glPushMatrix()
    glTranslatef(70.0, -0.1, 292.8)
    draw_box(11.2, 0.2, 94.4, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

MAZE_WALL_SEGMENTS = [
    # (cx, cy, cz, sx, sy, sz)
    (0.0, 3.5, -0.4, 13.6, 7.0, 0.8),          # South Wall of Start Hub
    (-6.4, 3.5, 27.0, 0.8, 7.0, 54.8),         # Start Hub West Wall
    (6.4, 3.5, 27.0, 0.8, 7.0, 54.8),          # Start Hub East Wall
    (-6.4, 3.5, 60.0, 0.8, 7.0, 12.0),         # West end cap of Junction A
    (13.8, 3.5, 65.6, 41.2, 7.0, 0.8),         # South Wall of Junction A
    (26.0, 3.5, 54.4, 40.0, 7.0, 0.8),         # North Wall of Junction A
    (34.4, 3.5, 90.2, 0.8, 7.0, 49.2),         # West Wall of Lava Pit
    (45.6, 3.5, 87.0, 0.8, 7.0, 66.0),         # East Wall of Lava Pit
    (45.6, 3.5, 120.0, 0.8, 7.0, 12.0),        # East end cap of Junction B
    (5.8, 3.5, 125.6, 80.4, 7.0, 0.8),         # North Wall of Corridor B
    (-5.8, 3.5, 114.4, 80.4, 7.0, 0.8),        # South Wall of Corridor B
    (-45.6, 3.5, 147.5, 0.8, 7.0, 67.0),       # West Wall of Disappearing Floor
    (-34.4, 3.5, 150.0, 0.8, 7.0, 49.6),       # East Wall of Disappearing Floor
    (-45.6, 3.5, 180.0, 0.8, 7.0, 12.0),       # West end cap of Junction C
    (-15.8, 3.5, 185.6, 60.4, 7.0, 0.8),       # North Wall of Junction C
    (-4.5, 3.5, 174.4, 61.0, 7.0, 0.8),        # South Wall of Junction C
    (14.4, 3.5, 215.5, 0.8, 7.0, 61.0),        # West Wall of Laser Gauntlet
    (25.6, 3.5, 204.6, 0.8, 7.0, 60.4),        # East Wall of Laser Gauntlet
    (50.8, 3.5, 234.4, 50.4, 7.0, 0.8),        # South Wall of Junction D
    (39.8, 3.5, 245.6, 51.6, 7.0, 0.8),        # North Wall of Junction D
    (64.4, 3.5, 292.8, 0.8, 7.0, 95.2),        # West Wall of Exit Chamber
    (75.6, 3.5, 287.2, 0.8, 7.0, 106.4),       # East Wall of Exit Chamber
    (70.0, 3.5, 340.4, 12.0, 7.0, 0.8),        # North Back Wall of Exit Chamber
]

LIGHT_COORDS = [
    (0.0, 15.0), (0.0, 45.0),
    (20.0, 60.0), (40.0, 75.0), (40.0, 105.0),
    (20.0, 120.0), (-20.0, 120.0), (-40.0, 135.0), (-40.0, 165.0),
    (-10.0, 180.0), (20.0, 195.0), (20.0, 225.0),
    (45.0, 240.0), (70.0, 260.0), (70.0, 290.0), (70.0, 320.0)
]

PILLAR_COORDS = [
    (0.0, 0.0), (-5.0, 20.0), (5.0, 20.0),
    (-5.0, 55.0), (5.0, 55.0),
    (35.0, 65.0), (45.0, 65.0),
    (35.0, 115.0), (45.0, 115.0),
    (-35.0, 125.0), (-45.0, 125.0),
    (-35.0, 175.0), (-45.0, 175.0),
    (15.0, 185.0), (25.0, 185.0),
    (15.0, 235.0), (25.0, 235.0),
    (65.0, 245.0), (75.0, 245.0),
    (65.0, 335.0), (75.0, 335.0)
]

_subdivided_walls = None

def _get_subdivided_walls(max_len=3.8):
    """
    Subdivides long wall segments into small blocks (max length <= 3.8 units).
    Ensures per-segment depth calculation is accurate for the Painter's Algorithm.
    """
    global _subdivided_walls
    if _subdivided_walls is not None:
        return _subdivided_walls
    segments = []
    for cx, cy, cz, sx, sy, sz in MAZE_WALL_SEGMENTS:
        if sx > max_len and sz <= max_len:
            n = max(1, int(math.ceil(sx / max_len)))
            w = sx / float(n)
            start_x = (cx - sx / 2.0) + w / 2.0
            for i in range(n):
                sub_x = start_x + i * w
                segments.append((sub_x, cy, cz, w, sy, sz))
        elif sz > max_len and sx <= max_len:
            n = max(1, int(math.ceil(sz / max_len)))
            d = sz / float(n)
            start_z = (cz - sz / 2.0) + d / 2.0
            for i in range(n):
                sub_z = start_z + i * d
                segments.append((cx, cy, sub_z, sx, sy, d))
        else:
            segments.append((cx, cy, cz, sx, sy, sz))
    _subdivided_walls = segments
    return _subdivided_walls

def draw_connected_walls():
    """Renders maze walls and ceiling light panels."""
    for cx, cy, cz, sx, sy, sz in _get_subdivided_walls():
        glPushMatrix()
        glTranslatef(cx, cy, cz)
        draw_box(sx, sy, sz, color_top=COLOR_WALL, color_side=COLOR_WALL_SIDE)
        glPopMatrix()

    for lx, lz in LIGHT_COORDS:
        glPushMatrix()
        glTranslatef(lx, 6.9, lz)
        draw_box(3.0, 0.1, 4.0, color_top=COLOR_LIGHT_PANEL, color_side=(0.7, 0.7, 0.5))
        glPopMatrix()

def draw_pillars_and_archways():
    """Draws dark charcoal pillars with cyan glowing caps at maze turn corners."""
    
    for px, pz in PILLAR_COORDS:
        glPushMatrix()
        glTranslatef(px, 3.5, pz)
        draw_box(1.4, 7.0, 1.4, color_top=COLOR_PILLAR, color_side=(0.12, 0.12, 0.14))
        glPopMatrix()

        glPushMatrix()
        glTranslatef(px, 6.2, pz)
        draw_box(1.6, 0.4, 1.6, color_top=COLOR_CYAN_GLOW, color_side=(0.0, 0.6, 0.8))
        glPopMatrix()

# -----------------------------------------------------------------------------
# Lava Hazard Zone (Section 2)
# -----------------------------------------------------------------------------
LAVA_TILE_ROCKS = [
    # (rx, rz, sx, sz, tilt)
    (40.0,  68.0,  3.6, 4.2,  0.0),   # R1 — entry (centre)
    (38.8,  74.3,  3.6, 4.2,  6.0),   # R2 — left
    (41.2,  80.6,  3.6, 4.2, -6.0),   # R3 — right
    (38.8,  86.9,  3.6, 4.2,  5.0),   # R4 — left
    (41.2,  93.2,  3.6, 4.2, -5.0),   # R5 — right
    (38.8,  99.5,  3.6, 4.2,  6.0),   # R6 — left
    (41.2, 105.8,  3.6, 4.2, -6.0),   # R7 — right
    (40.0, 112.0,  3.6, 4.2,  0.0),   # R8 — exit (centre)
]

def draw_lava_base_only():
    """Renders the recessed lava pit base. Called before hazard rocks so depth is correct."""
    CX   = 40.0   # corridor center X
    CXHW = 5.6    # half-width (34.4 to 45.6)
    ZSTART = 65.6
    ZEND   = 114.4
    ZDEPTH = ZEND - ZSTART
    ZCZ    = (ZSTART + ZEND) / 2.0

    glPushMatrix()
    glTranslatef(CX, -2.2, ZCZ)
    draw_box(CXHW * 2, 4.4, ZDEPTH, color_top=(0.02, 0.01, 0.02), color_side=(0.06, 0.02, 0.03))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(CX, 0.0, ZCZ)
    draw_box(CXHW * 2, 0.06, ZDEPTH, color_top=(0.75, 0.04, 0.0), color_side=(0.50, 0.02, 0.0))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(CX, 0.07, ZCZ)
    draw_box(CXHW * 2 - 0.8, 0.05, ZDEPTH - 1.6,
             color_top=(1.0, 0.32, 0.0), color_side=(0.85, 0.15, 0.0))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(CX, 0.13, ZCZ)
    draw_box(CXHW * 2 - 2.5, 0.04, ZDEPTH - 4.0,
             color_top=(1.0, 0.65, 0.0), color_side=(0.95, 0.35, 0.0))
    glPopMatrix()

    # Scattered dark basalt crust tiles on the lava surface
    for z_tile in range(int(ZSTART) + 2, int(ZEND) - 2, 3):
        for x_off in [-3.8, -1.9, 0.0, 1.9, 3.8]:
            glPushMatrix()
            glTranslatef(CX + x_off, 0.15, float(z_tile))
            draw_box(1.5, 0.08, 2.2,
                     color_top=(0.14, 0.11, 0.12),
                     color_side=(0.75, 0.20, 0.0))
            glPopMatrix()

def _draw_lava_spike(x, y, z, base_w=0.35, height=1.5):
    """Draws a single 3D volcanic lava spike."""
    glPushMatrix()
    glTranslatef(x, y, z)
    c_base = (0.16, 0.12, 0.14)
    c_tip  = (1.00, 0.40, 0.00)
    glBegin(GL_TRIANGLES)
    glColor3f(*c_base); glVertex3f(-base_w, 0.0,  base_w)
    glColor3f(*c_base); glVertex3f( base_w, 0.0,  base_w)
    glColor3f(*c_tip);  glVertex3f( 0.0, height,  0.0)
    glColor3f(*c_base); glVertex3f( base_w, 0.0,  base_w)
    glColor3f(*c_base); glVertex3f( base_w, 0.0, -base_w)
    glColor3f(*c_tip);  glVertex3f( 0.0, height,  0.0)
    glColor3f(*c_base); glVertex3f( base_w, 0.0, -base_w)
    glColor3f(*c_base); glVertex3f(-base_w, 0.0, -base_w)
    glColor3f(*c_tip);  glVertex3f( 0.0, height,  0.0)
    glColor3f(*c_base); glVertex3f(-base_w, 0.0, -base_w)
    glColor3f(*c_base); glVertex3f(-base_w, 0.0,  base_w)
    glColor3f(*c_tip);  glVertex3f( 0.0, height,  0.0)
    glEnd()
    glPopMatrix()

def draw_lava_tile_rock(rx, rz, sx, sz, tilt=0.0):
    """Draws one obsidian stepping-stone island over the lava."""
    glPushMatrix()
    glTranslatef(rx, 1.0, rz)
    if tilt != 0.0:
        glRotatef(tilt, 0, 1, 0)
    draw_box(sx, 0.50, sz,
             color_top=(0.12, 0.10, 0.13),
             color_side=(0.07, 0.05, 0.08))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(rx, 0.76, rz)
    if tilt != 0.0:
        glRotatef(tilt, 0, 1, 0)
    draw_box(sx + 0.25, 0.08, sz + 0.25,
             color_top=(1.0, 0.30, 0.0),
             color_side=(0.85, 0.15, 0.0))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(rx, 1.26, rz)
    if tilt != 0.0:
        glRotatef(tilt, 0, 1, 0)
    draw_box(sx - 0.1, 0.04, sz - 0.1,
             color_top=(1.0, 0.55, 0.0),
             color_side=(0.9, 0.30, 0.0))
    glPopMatrix()

    # 2x3 grid of dark basalt tiles (magma glows in the grooves between them)
    tile_w = (sx - 0.5) / 2.0
    tile_d = (sz - 0.7) / 3.0

    for col in [-1, 1]:
        for row in [-1, 0, 1]:
            tx = rx + col * (tile_w / 2.0 + 0.08)
            tz = rz + row * (tile_d + 0.10)
            glPushMatrix()
            glTranslatef(tx, 1.30, tz)
            if tilt != 0.0:
                glRotatef(tilt, 0, 1, 0)
            draw_box(tile_w, 0.08, tile_d,
                     color_top=(0.20, 0.17, 0.20),
                     color_side=(0.10, 0.08, 0.11))
            glPopMatrix()

def draw_hazard_zones():
    """Draws the lava hazard zone: pit base and all stepping-stone rocks."""
    draw_lava_base_and_tiles()
    for rx, rz, sx, sz, tilt in LAVA_TILE_ROCKS:
        draw_lava_tile_rock(rx, rz, sx, sz, tilt)

# -----------------------------------------------------------------------------
# Disappearing Platform Chamber (Section 3)
# -----------------------------------------------------------------------------
DISAPPEARING_TILE_COORDS = [
    (-43.5, 138.0, 0), (-40.0, 138.0, 1), (-36.5, 138.0, 2),
    (-43.5, 146.0, 3), (-40.0, 146.0, 4), (-36.5, 146.0, 5),
    (-43.5, 154.0, 0), (-40.0, 154.0, 2), (-36.5, 154.0, 4),
    (-43.5, 162.0, 1), (-40.0, 162.0, 3), (-36.5, 162.0, 5)
]

TILE_COLORS = [
    (0.95, 0.45, 0.05), (0.05, 0.85, 0.95), (0.15, 0.90, 0.35),
    (0.90, 0.15, 0.90), (0.95, 0.85, 0.10), (0.10, 0.55, 0.95)
]

def draw_disappearing_platforms():
    """Draws the color-coded platform tiles over the abyss gap."""
    
    glPushMatrix()
    glTranslatef(-40.0, -4.0, 150.0)
    draw_box(17.0, 0.2, 32.0, color_top=(0.02, 0.01, 0.05), color_side=(0.01, 0.0, 0.02))
    glPopMatrix()

    for px, pz, color_idx in DISAPPEARING_TILE_COORDS:
        is_active = disappearing_tiles_active[color_idx]
        glPushMatrix()
        glTranslatef(px, 0.0, pz)
        
        if is_active:
            draw_box(2.8, 0.4, 4.0, color_top=TILE_COLORS[color_idx], color_side=(0.15, 0.15, 0.18))
            glPushMatrix()
            glTranslatef(0.0, -0.25, 0.0)
            draw_box(2.4, 0.1, 3.6, color_top=(1.0, 1.0, 1.0), color_side=(0.5, 0.5, 0.5))
            glPopMatrix()
        else:
            glColor3f(0.3, 0.3, 0.35)
            glBegin(GL_LINES)
            for dx in [-1.4, 1.4]:
                for dz in [-2.0, 2.0]:
                    glVertex3f(dx, -0.2, dz)
                    glVertex3f(dx, 0.2, dz)
            glEnd()
            
        glPopMatrix()

# -----------------------------------------------------------------------------
# Laser Gauntlet (Section 4, X: 14.4->25.6, Z: 180->240)
# -----------------------------------------------------------------------------
# (z_pos, y_height, color, description)
LASER_BEAMS = [
    (192.0, 2.2,  COLOR_LASER_RED, "High Beam - Crouch Under"),
    (202.0, 0.65, COLOR_LASER_RED, "Low Beam - Jump Over"),
    (212.0, 2.2,  COLOR_LASER_RED, "High Beam - Crouch Under"),
    (222.0, 0.65, COLOR_LASER_RED, "Low Beam - Jump Over"),
    (232.0, 1.8,  COLOR_LASER_RED, "Mid-High Beam - Crouch Dodge")
]

def draw_laser_emitters():
    """Renders laser emitter boxes and glowing beam lines for the gauntlet corridor."""
    
    for pz, py, color_rgb, desc in LASER_BEAMS:
        glPushMatrix()
        glTranslatef(14.7, py, pz)
        draw_box(0.6, 0.8, 0.8, color_top=(0.3, 0.3, 0.35), color_side=(0.2, 0.2, 0.25))
        glTranslatef(0.35, 0.0, 0.0)
        draw_box(0.1, 0.4, 0.4, color_top=color_rgb, color_side=color_rgb)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(25.3, py, pz)
        draw_box(0.6, 0.8, 0.8, color_top=(0.3, 0.3, 0.35), color_side=(0.2, 0.2, 0.25))
        glTranslatef(-0.35, 0.0, 0.0)
        draw_box(0.1, 0.4, 0.4, color_top=color_rgb, color_side=color_rgb)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(20.0, py, pz)
        draw_box(10.0, 0.08, 0.08, color_top=color_rgb, color_side=color_rgb)  # outer glow
        draw_box(10.0, 0.03, 0.03, color_top=(1.0, 1.0, 1.0), color_side=(1.0, 1.0, 1.0))  # bright core
        glPopMatrix()

# -----------------------------------------------------------------------------
# Moving Walls (Section 5, X: 64.4->75.6, Z: 240->300)
# (z_center, phase_multiplier): phase_mult=-1 means walls are inverted/opposing
# -----------------------------------------------------------------------------
MOVING_WALL_PAIRS = [
    (260.0,  1.0),
    (275.0, -1.0),  # inverted: closes when pair 1 opens
    (290.0,  1.0),
]
MOVING_WALL_CX = 70.0
MOVING_WALL_BLOCK_W = 3.0
MOVING_WALL_REST_L = 65.5
MOVING_WALL_REST_R = 74.5

def draw_moving_walls():
    """Draws the 3 shifting wall pairs with hazard stripe inner edges."""
    for wz, phase in MOVING_WALL_PAIRS:
        offset = moving_walls_offset * phase

        left_x = MOVING_WALL_REST_L + offset
        glPushMatrix()
        glTranslatef(left_x, 3.0, wz)
        draw_box(MOVING_WALL_BLOCK_W, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
        glTranslatef(MOVING_WALL_BLOCK_W / 2.0 - 0.1, 0.0, 0.0)
        draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
        glPopMatrix()

        right_x = MOVING_WALL_REST_R - offset
        glPushMatrix()
        glTranslatef(right_x, 3.0, wz)
        draw_box(MOVING_WALL_BLOCK_W, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
        glTranslatef(-(MOVING_WALL_BLOCK_W / 2.0 - 0.1), 0.0, 0.0)
        draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
        glPopMatrix()

def draw_exit_portal():
    """Draws the glowing blue exit portal gateway at the end of the maze."""
    
    portal_x, portal_z = 70.0, 330.0

    glPushMatrix()
    glTranslatef(portal_x, 3.5, portal_z + 4.0)
    draw_box(12.0, 7.0, 0.8, color_top=(0.14, 0.14, 0.18), color_side=(0.10, 0.10, 0.14))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(portal_x - 3.0, 3.0, portal_z)
    draw_box(1.2, 6.0, 1.2, color_top=(0.20, 0.22, 0.26), color_side=(0.15, 0.16, 0.20))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(portal_x + 3.0, 3.0, portal_z)
    draw_box(1.2, 6.0, 1.2, color_top=(0.20, 0.22, 0.26), color_side=(0.15, 0.16, 0.20))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(portal_x, 5.6, portal_z)
    draw_box(7.2, 1.0, 1.2, color_top=(0.20, 0.22, 0.26), color_side=(0.15, 0.16, 0.20))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(portal_x, 2.5, portal_z + 0.1)
    draw_box(4.5, 5.0, 0.1, color_top=COLOR_PORTAL_CYAN, color_side=(0.0, 0.55, 0.85))
    glPopMatrix()

    glColor3f(0.3, 0.95, 1.0)
    glBegin(GL_LINES)
    glVertex3f(portal_x - 2.4, 0.0, portal_z + 0.2); glVertex3f(portal_x - 2.4, 5.0, portal_z + 0.2)
    glVertex3f(portal_x + 2.4, 0.0, portal_z + 0.2); glVertex3f(portal_x + 2.4, 5.0, portal_z + 0.2)
    glVertex3f(portal_x - 2.4, 5.0, portal_z + 0.2); glVertex3f(portal_x + 2.4, 5.0, portal_z + 0.2)
    glEnd()

# -----------------------------------------------------------------------------
# Camera & Display
# -----------------------------------------------------------------------------
def setup_camera():
    """Configures perspective projection and camera position (1st or 3rd person)."""
    
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(WINDOW_WIDTH) / float(WINDOW_HEIGHT), 0.1, 400.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    rad_yaw = math.radians(camera_yaw)
    rad_pitch = math.radians(player_pitch)

    curr_eye_h = 0.8 if crouching else eye_height

    if first_person:
        cam_x = player_pos[0]
        cam_y = player_pos[1] + curr_eye_h
        cam_z = player_pos[2]

        center_x = cam_x + math.sin(rad_yaw) * math.cos(rad_pitch) * 100.0
        center_y = cam_y + math.sin(rad_pitch) * 100.0
        center_z = cam_z + math.cos(rad_yaw) * math.cos(rad_pitch) * 100.0

        gluLookAt(cam_x, cam_y, cam_z,
                  center_x, center_y, center_z,
                  0.0, 1.0, 0.0)
    else:
        # Spherical orbit: offset behind player using yaw + pitch
        cam_x = player_pos[0] - math.sin(rad_yaw) * cam_dist * math.cos(rad_pitch)
        cam_y = player_pos[1] + cam_height + math.sin(rad_pitch) * cam_dist
        cam_z = player_pos[2] - math.cos(rad_yaw) * cam_dist * math.cos(rad_pitch)

        center_x = player_pos[0]
        center_y = player_pos[1] + 1.2
        center_z = player_pos[2]

        gluLookAt(cam_x, cam_y, cam_z,
                  center_x, center_y, center_z,
                  0.0, 1.0, 0.0)

def draw_rect_2d(x1, y1, x2, y2, color):
    """Draws a filled 2D rectangle in orthographic mode."""
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()

def draw_rect_border_2d(x1, y1, x2, y2, color, line_width=2.0):
    """Draws a 2D rectangular border frame in orthographic mode."""
    glColor3f(*color)
    glBegin(GL_LINES)
    glVertex2f(x1, y1); glVertex2f(x2, y1)
    glVertex2f(x2, y1); glVertex2f(x2, y2)
    glVertex2f(x2, y2); glVertex2f(x1, y2)
    glVertex2f(x1, y2); glVertex2f(x1, y1)
    glEnd()

_user32 = ctypes.windll.user32

def update_window_dimensions():
    global WINDOW_WIDTH, WINDOW_HEIGHT
    try:
        hwnd = _user32.GetForegroundWindow()
        if not hwnd:
            hwnd = _user32.GetActiveWindow()
        if hwnd:
            from ctypes import wintypes
            rect = wintypes.RECT()
            if _user32.GetClientRect(hwnd, ctypes.byref(rect)):
                w = rect.right - rect.left
                h = rect.bottom - rect.top
                if w > 200 and h > 200:
                    WINDOW_WIDTH = w
                    WINDOW_HEIGHT = h
    except:
        pass

def draw_story_screen():
    """Renders the intro story screen with typewriter text and a pulsing start prompt."""
    
    update_window_dimensions()

    glClear(GL_COLOR_BUFFER_BIT)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(0.08, 0.10, 0.16)
    glBegin(GL_LINES)
    for gx in range(0, WINDOW_WIDTH, 40):
        glVertex2f(gx, 0); glVertex2f(gx, WINDOW_HEIGHT)
    for gy in range(0, WINDOW_HEIGHT, 40):
        glVertex2f(0, gy); glVertex2f(WINDOW_WIDTH, gy)
    glEnd()

    panel_w, panel_h = 680, 360
    px1 = (WINDOW_WIDTH - panel_w) // 2
    px2 = px1 + panel_w
    py1 = (WINDOW_HEIGHT - panel_h) // 2
    py2 = py1 + panel_h

    draw_rect_2d(px1, py1, px2, py2, (0.07, 0.08, 0.13))
    draw_rect_border_2d(px1, py1, px2, py2, (0.0, 0.75, 0.95), line_width=2.5)
    draw_rect_border_2d(px1 + 4, py1 + 4, px2 - 4, py2 - 4, (1.0, 0.7, 0.2), line_width=1.0)

    title_str = "9 Lives"
    t_w = len(title_str) * 9.2
    t_start_x = (WINDOW_WIDTH - t_w) // 2
    title_y = py2 - 48

    glColor3f(0.3, 0.1, 0.0)
    glRasterPos2f(t_start_x + 1, title_y - 1)
    for ch in title_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(1.0, 0.45, 0.15)
    glRasterPos2f(t_start_x, title_y)
    for ch in title_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(0.0, 0.75, 0.95)
    glBegin(GL_LINES)
    glVertex2f(px1 + 40, py2 - 62)
    glVertex2f(px2 - 40, py2 - 62)
    glEnd()

    chars_left = story_char_index
    body_center_y = py1 + 175

    line_y_offsets = [35, -5, -45]
    line_colors = [
        (1.0, 0.88, 0.35),  # Warm Gold for Line 1 ("Tung Tung Tung Sahur...")
        (0.95, 0.92, 0.85), # Soft White for Line 2 ("Armed with 9 Lives...")
        (0.95, 0.92, 0.85)  # Soft White for Line 3 ("defeat the wicked cats...")
    ]

    for i, line in enumerate(story_lines):
        if chars_left <= 0:
            break
        visible_text = line[:chars_left]
        chars_left -= len(line)

        # Center line horizontally
        l_w = len(line) * 9.2
        start_x = (WINDOW_WIDTH - l_w) // 2
        line_y = body_center_y + line_y_offsets[i]

        glColor3f(*line_colors[i])
        glRasterPos2f(start_x, line_y)
        for ch in visible_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    prompt_str = "PRESS SPACE OR ENTER TO START"
    p_w = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(ch)) for ch in prompt_str)
    p_start_x = (WINDOW_WIDTH - p_w) // 2
    prompt_y = py1 + 35
    pulse_val = 0.5 + 0.5 * math.sin(story_timer * 0.08)

    box_pad_x = 36
    box_x1 = p_start_x - box_pad_x
    box_x2 = p_start_x + p_w + box_pad_x
    box_y1 = prompt_y - 10
    box_y2 = prompt_y + 26

    draw_rect_2d(box_x1, box_y1, box_x2, box_y2, (0.05, 0.12 + 0.10 * pulse_val, 0.20 + 0.15 * pulse_val))
    draw_rect_border_2d(box_x1, box_y1, box_x2, box_y2, (0.0, 0.70 + 0.30 * pulse_val, 0.90 + 0.10 * pulse_val), line_width=2.0)
    glColor3f(0.85 + 0.15 * pulse_val, 0.95 + 0.05 * pulse_val, 1.0)
    glRasterPos2f(p_start_x, prompt_y)
    for ch in prompt_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glutSwapBuffers()

def display():
    """Main display callback. Renders the story screen or the 3D game world."""
    update_window_dimensions()

    if in_story_screen:
        draw_story_screen()
        return

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    setup_camera()

    draw_connected_floor_pathways()
    draw_lava_base_only()

    rad = math.radians(camera_yaw)
    curr_eye_h = 0.8 if crouching else eye_height

    if first_person:
        cam_x = player_pos[0]
        cam_y = player_pos[1] + curr_eye_h
        cam_z = player_pos[2]
    else:
        cam_x = player_pos[0] - math.sin(rad) * cam_dist
        cam_y = player_pos[1] + cam_height
        cam_z = player_pos[2] - math.cos(rad) * cam_dist

    # Build render list for depth-sorted (Painter's Algorithm) drawing
    render_list = []

    for w_cx, w_cy, w_cz, w_sx, w_sy, w_sz in _get_subdivided_walls():
        def _draw_w(cx=w_cx, cy=w_cy, cz=w_cz, sx=w_sx, sy=w_sy, sz=w_sz):
            glPushMatrix()
            glTranslatef(cx, cy, cz)
            draw_box(sx, sy, sz, color_top=COLOR_WALL, color_side=COLOR_WALL_SIDE)
            glPopMatrix()
        render_list.append((w_cx, w_cy, w_cz, _draw_w))

    for lx, lz in LIGHT_COORDS:
        def _draw_l(lx=lx, lz=lz):
            glPushMatrix()
            glTranslatef(lx, 6.9, lz)
            draw_box(3.0, 0.1, 4.0, color_top=COLOR_LIGHT_PANEL, color_side=(0.7, 0.7, 0.5))
            glPopMatrix()
        render_list.append((lx, 6.9, lz, _draw_l))

    for px, pz in PILLAR_COORDS:
        def _draw_p(px=px, pz=pz):
            glPushMatrix()
            glTranslatef(px, 3.5, pz)
            draw_box(1.4, 7.0, 1.4, color_top=COLOR_PILLAR, color_side=(0.12, 0.12, 0.14))
            glPopMatrix()
            glPushMatrix()
            glTranslatef(px, 6.2, pz)
            draw_box(1.6, 0.4, 1.6, color_top=COLOR_CYAN_GLOW, color_side=(0.0, 0.6, 0.8))
            glPopMatrix()
        render_list.append((px, 3.5, pz, _draw_p))

    for rx, rz, sx, sz, tilt in LAVA_TILE_ROCKS:
        def _draw_rock(rx=rx, rz=rz, sx=sx, sz=sz, tilt=tilt):
            draw_lava_tile_rock(rx, rz, sx, sz, tilt)
        render_list.append((rx, 1.0, rz, _draw_rock))

    for z_spk in range(int(65.6) + 3, int(114.4) - 3, 4):
        for sx_off, base_w, h, z_off in [(-4.2, 0.40, 1.8, 0.0), (-2.5, 0.30, 1.4, 1.5), (2.5, 0.32, 1.5, 0.8), (4.2, 0.42, 1.9, 2.2)]:
            spk_x = 40.0 + sx_off
            spk_z = float(z_spk) + z_off
            def _spk(x=spk_x, z=spk_z, bw=base_w, ht=h):
                _draw_lava_spike(x, 0.1, z, bw, ht)
            render_list.append((spk_x, 0.1 + h * 0.5, spk_z, _spk))

    for z_side in range(int(65.6), int(114.4), 6):
        for sign_x in [-1.0, 1.0]:
            ledge_x = 40.0 + sign_x * (5.6 - 0.6)
            ledge_z = float(z_side) + 3.0
            def _draw_ledge(lx=ledge_x, lz=ledge_z):
                glPushMatrix()
                glTranslatef(lx, 0.5, lz)
                draw_box(1.2, 1.2, 5.6, color_top=(0.16, 0.14, 0.16), color_side=(0.10, 0.08, 0.10))
                glPopMatrix()
                glPushMatrix()
                glTranslatef(lx, 0.1, lz)
                draw_box(1.3, 0.1, 5.6, color_top=(1.0, 0.30, 0.0), color_side=(0.8, 0.15, 0.0))
                glPopMatrix()
            render_list.append((ledge_x, 0.5, ledge_z, _draw_ledge))

    for pz in [65.8, 114.2]:
        def _draw_ws(pz=pz):
            glPushMatrix()
            glTranslatef(40.0, 0.04, pz)
            draw_box(11.2, 0.04, 0.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.6, 0.5, 0.0))
            glPopMatrix()
        render_list.append((40.0, 0.04, pz, _draw_ws))

    for px, pz, color_idx in DISAPPEARING_TILE_COORDS:
        def _draw_dt(px=px, pz=pz, c=color_idx):
            is_active = disappearing_tiles_active[c]
            glPushMatrix()
            glTranslatef(px, 0.0, pz)
            if is_active:
                draw_box(2.8, 0.4, 4.0, color_top=TILE_COLORS[c], color_side=(0.15, 0.15, 0.18))
                glPushMatrix()
                glTranslatef(0.0, -0.25, 0.0)
                draw_box(2.4, 0.1, 3.6, color_top=(1.0, 1.0, 1.0), color_side=(0.5, 0.5, 0.5))
                glPopMatrix()
            else:
                glColor3f(0.3, 0.3, 0.35)
                glBegin(GL_LINES)
                for dx in [-1.4, 1.4]:
                    for dz in [-2.0, 2.0]:
                        glVertex3f(dx, -0.2, dz)
                        glVertex3f(dx, 0.2, dz)
                glEnd()
            glPopMatrix()
        render_list.append((px, 0.0, pz, _draw_dt))

    for pz, py, color_rgb, desc in LASER_BEAMS:
        def _draw_laser(pz=pz, py=py, col=color_rgb):
            glPushMatrix()
            glTranslatef(14.7, py, pz)
            draw_box(0.6, 0.8, 0.8, color_top=(0.3, 0.3, 0.35), color_side=(0.2, 0.2, 0.25))
            glTranslatef(0.35, 0.0, 0.0)
            draw_box(0.1, 0.4, 0.4, color_top=col, color_side=col)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(25.3, py, pz)
            draw_box(0.6, 0.8, 0.8, color_top=(0.3, 0.3, 0.35), color_side=(0.2, 0.2, 0.25))
            glTranslatef(-0.35, 0.0, 0.0)
            draw_box(0.1, 0.4, 0.4, color_top=col, color_side=col)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(20.0, py, pz)
            draw_box(10.0, 0.08, 0.08, color_top=col, color_side=col)
            draw_box(10.0, 0.03, 0.03, color_top=(1.0, 1.0, 1.0), color_side=(1.0, 1.0, 1.0))
            glPopMatrix()
        render_list.append((20.0, py, pz, _draw_laser))

    for z_center, phase_mult in MOVING_WALL_PAIRS:
        offset = moving_walls_offset * phase_mult
        left_x = MOVING_WALL_REST_L + offset
        right_x = MOVING_WALL_REST_R - offset

        def _draw_mw_l(lx=left_x, wz=z_center):
            glPushMatrix()
            glTranslatef(lx, 3.0, wz)
            draw_box(MOVING_WALL_BLOCK_W, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
            glTranslatef(MOVING_WALL_BLOCK_W / 2.0 - 0.1, 0.0, 0.0)
            draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
            glPopMatrix()
        render_list.append((left_x, 3.0, z_center, _draw_mw_l))

        def _draw_mw_r(rx=right_x, wz=z_center):
            glPushMatrix()
            glTranslatef(rx, 3.0, wz)
            draw_box(MOVING_WALL_BLOCK_W, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
            glTranslatef(-(MOVING_WALL_BLOCK_W / 2.0 - 0.1), 0.0, 0.0)
            draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
            glPopMatrix()
        render_list.append((right_x, 3.0, z_center, _draw_mw_r))

    render_list.append((70.0, 2.5, 330.0, draw_exit_portal))

    if not first_person:
        def _draw_player():
            # Blink player during wall invincibility
            if wall_invincibility_timer > 0:
                if (wall_invincibility_timer // 10) % 2 == 0:
                    draw_character(cam_x, cam_z)
            else:
                draw_character(cam_x, cam_z)
        render_list.append((player_pos[0], player_pos[1] + 0.8, player_pos[2], _draw_player))

    for ex, ey, ez, fn in render_list:
        fn()

    # HUD
    remaining_lives = max(0, 9 - consecutive_lava_falls)
    player_pct = remaining_lives / 9.0

    if player_pct > 0.5:
        bar_color = (0.1, 0.9, 0.2)
    elif player_pct > 0.25:
        bar_color = (1.0, 0.8, 0.0)
    else:
        bar_color = (1.0, 0.15, 0.15)

    pw, ph = 220, 16
    px, py = 25, 45
    draw_bar_2d(px, py, pw, ph, player_pct, bar_color, border_color=(0.9, 0.9, 0.9))
    draw_text(px + pw + 12, py + 1, f"LIVES: {remaining_lives}/9", color=bar_color, font=GLUT_BITMAP_HELVETICA_18)

    draw_text(25, 68, f"Crouch: {'ON' if crouching else 'OFF'}")
    if cheat_mode:
        draw_text_bold(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 35, 'CHEAT MODE ON', color=(1.0, 0.85, 0.2), font=GLUT_BITMAP_HELVETICA_18)

    if game_over:
        msg = "GAME OVER! All 9 Lifelines lost. Press 'R' to restart."
        sw = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in msg)
        draw_text_bold((WINDOW_WIDTH - sw) // 2, WINDOW_HEIGHT // 2, msg, color=(1.0, 0.2, 0.2))
    elif game_paused:
        msg = "=== GAME PAUSED ==="
        sw = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in msg)
        draw_text_bold((WINDOW_WIDTH - sw) // 2, WINDOW_HEIGHT // 2 + 10, msg, color=(1.0, 0.9, 0.1))
        msg2 = "Press 'P' to Resume Game"
        sw2 = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in msg2)
        draw_text((WINDOW_WIDTH - sw2) // 2, WINDOW_HEIGHT // 2 - 20, msg2, color=(1.0, 1.0, 1.0))
    elif (time.time() < lava_alert_expiry) or (lava_alert_timer > 0):
        alert_str = f"ALERT: {hazard_alert_text}"
        sw = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in alert_str)
        cx = (WINDOW_WIDTH - sw) // 2
        cy = WINDOW_HEIGHT // 2 + 50
        # Dark outline shadow for readability, then bright gold text on top
        for ox in (-2, -1, 0, 1, 2):
            for oy in (-2, -1, 0, 1, 2):
                if ox != 0 or oy != 0:
                    draw_text(cx + ox, cy + oy, alert_str, color=(0.0, 0.0, 0.0), font=GLUT_BITMAP_HELVETICA_18)
        draw_text_bold(cx, cy, alert_str, color=(1.0, 0.88, 0.0), font=GLUT_BITMAP_HELVETICA_18)

    draw_text(15, 20, "WASD: Move | Mouse: Orbit Camera | Space: Jump | Ctrl/X: Crouch | V/RMB: 1st/3rd Person | P: Pause | C: God Mode | R: Reset", font=GLUT_BITMAP_HELVETICA_12)

    glutSwapBuffers()

# -----------------------------------------------------------------------------
# Physics, Collision & Animation
# -----------------------------------------------------------------------------
LAVA_PIT_X_MIN  = 34.4
LAVA_PIT_X_MAX  = 45.6
LAVA_PIT_1_ZMIN = 66.0
LAVA_PIT_1_ZMAX = 114.4

# Rock top Y aligns with 2x3 basalt tile surface
STEP_TOP_Y = 1.34

# Hitboxes matching visual rock size (3.6x4.2 -> half 1.8 x 2.1)
STEPPING_BOXES = [
    (40.0,  68.0, 1.8, 2.1),  # R1 — entry centre
    (38.8,  74.3, 1.8, 2.1),  # R2 — left
    (41.2,  80.6, 1.8, 2.1),  # R3 — right
    (38.8,  86.9, 1.8, 2.1),  # R4 — left
    (41.2,  93.2, 1.8, 2.1),  # R5 — right
    (38.8,  99.5, 1.8, 2.1),  # R6 — left
    (41.2, 105.8, 1.8, 2.1),  # R7 — right
    (40.0, 112.0, 1.8, 2.1),  # R8 — exit centre
]

def on_stepping_box():
    """Returns True if the player is horizontally over ANY rock slab."""
    px, pz = player_pos[0], player_pos[2]
    for (bx, bz, hx, hz) in STEPPING_BOXES:
        if (bx - hx) <= px <= (bx + hx) and (bz - hz) <= pz <= (bz + hz):
            return True
    return False

def in_lava_pit():
    """Returns True if the player is in the lava corridor but NOT on a rock."""
    px, pz = player_pos[0], player_pos[2]
    in_x  = LAVA_PIT_X_MIN <= px <= LAVA_PIT_X_MAX
    in_z  = LAVA_PIT_1_ZMIN <= pz <= LAVA_PIT_1_ZMAX
    return in_x and in_z and not on_stepping_box()

def check_laser_collisions():
    """Checks if the player is hit by any laser beam. Crouching or jumping safely dodges."""
    
    global player_pos, player_yaw, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over

    if cheat_mode:
        return False

    px, py, pz = player_pos[0], player_pos[1], player_pos[2]

    if not (14.4 <= px <= 25.6 and 180.0 <= pz <= 240.0):
        return False

    player_is_dodging = crouching or is_jumping or (py > ground_y + 0.15)

    for lz, ly, color_rgb, desc in LASER_BEAMS:
        if abs(pz - lz) <= 0.7:  # ±0.7 unit hit window around beam
            if not player_is_dodging:
                consecutive_lava_falls += 1
                trigger_hazard_alert("Hit by Laser! (Crouch 'CTRL' or Jump 'SPACE' to dodge)")
                if consecutive_lava_falls >= 9:
                    game_over = True
                player_pos = [20.0, 0.0, 182.0]  # respawn at gauntlet entrance
                player_yaw = 0.0
                is_jumping = False
                y_velocity = 0.0
                return True
    return False

def check_moving_wall_collisions():
    """
    Checks if the player is crushed between moving walls in Zone 5.
    Grants 60 invincibility frames after a hit. 3 consecutive hits respawn the player.
    """
    global player_pos, player_yaw, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over
    global consecutive_wall_hits, wall_invincibility_timer

    if cheat_mode:
        return False

    if wall_invincibility_timer > 0:
        return False

    px, pz = player_pos[0], player_pos[2]

    if not (64.4 <= px <= 75.6 and 240.0 <= pz <= 300.0):
        if pz > 298.0 and consecutive_wall_hits > 0:
            consecutive_wall_hits = 0
        return False

    for wz, phase in MOVING_WALL_PAIRS:
        if abs(pz - wz) < 4.0:  # within the 8-unit deep wall block
            offset = moving_walls_offset * phase
            left_inner_edge = (MOVING_WALL_REST_L + offset) + MOVING_WALL_BLOCK_W / 2.0
            right_inner_edge = (MOVING_WALL_REST_R - offset) - MOVING_WALL_BLOCK_W / 2.0

            if px <= left_inner_edge or px >= right_inner_edge:
                consecutive_wall_hits += 1
                consecutive_lava_falls += 1
                trigger_hazard_alert("Crushed by Moving Walls!")
                wall_invincibility_timer = 60  # ~1 second blink

                if consecutive_lava_falls >= 9:
                    game_over = True

                if consecutive_wall_hits >= 3:
                    player_pos = [70.0, 0.0, 245.0]  # respawn at zone 5 entry
                    player_yaw = 0.0
                    consecutive_wall_hits = 0
                else:
                    player_pos[0] = MOVING_WALL_CX  # push to corridor center

                is_jumping = False
                y_velocity = 0.0
                return True
    return False

def is_on_active_disappearing_tile(px, pz):
    """Returns True if (px, pz) is positioned over an ACTIVE disappearing tile."""
    for tile_x, tile_z, color_idx in DISAPPEARING_TILE_COORDS:
        if (tile_x - 1.4) <= px <= (tile_x + 1.4) and (tile_z - 2.0) <= pz <= (tile_z + 2.0):
            if disappearing_tiles_active[color_idx]:
                return True
    return False

def check_disappearing_floor():
    """Checks if the player falls into the void in the disappearing floor zone."""
    
    global player_pos, player_yaw, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over

    if cheat_mode:
        return False

    px, py, pz = player_pos[0], player_pos[1], player_pos[2]

    if not (-45.6 <= px <= -34.4 and 135.0 <= pz <= 165.0):
        return False

    if py > ground_y + 0.15:  # safe while airborne
        return False

    if not is_on_active_disappearing_tile(px, pz):
        consecutive_lava_falls += 1
        trigger_hazard_alert("Fell into the void!")
        if consecutive_lava_falls >= 9:
            game_over = True
        player_pos = [-40.0, 0.0, 128.0]  # respawn at entry walkway
        player_yaw = 0.0
        is_jumping = False
        y_velocity = 0.0
        return True

    return False

def update_player_physics():
    """Applies gravity/jump physics and checks all hazard collisions."""
    
    global player_pos, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over

    if is_jumping:
        player_pos[1] += y_velocity
        y_velocity += gravity

        if on_stepping_box() and y_velocity <= 0 and player_pos[1] <= STEP_TOP_Y:
            player_pos[1] = STEP_TOP_Y
            is_jumping = False
            y_velocity = 0.0
            return

        if player_pos[1] <= ground_y:
            if in_lava_pit():
                if not cheat_mode:
                    consecutive_lava_falls += 1
                    trigger_hazard_alert("Fell into the lava!")
                    if consecutive_lava_falls >= 9:
                        game_over = True
                    player_pos = [40.0, 0.0, 65.0]  # respawn at lava section entry
                    player_yaw = 0.0
                else:
                    player_pos[1] = ground_y
            else:
                player_pos[1] = ground_y
            is_jumping = False
            y_velocity = 0.0
    else:
        if on_stepping_box():
            player_pos[1] = STEP_TOP_Y
        elif in_lava_pit():
            if not cheat_mode:
                consecutive_lava_falls += 1
                trigger_hazard_alert("Fell into the lava!")
                if consecutive_lava_falls >= 9:
                    game_over = True
                player_pos = [40.0, 0.0, 65.0]
                player_yaw = 0.0
            else:
                player_pos[1] = ground_y
        else:
            player_pos[1] = ground_y

    check_disappearing_floor()
    check_laser_collisions()
    check_moving_wall_collisions()

    if lava_alert_timer > 0:
        lava_alert_timer -= 1

def idle():
    """Idle callback: advances typewriter text, physics, animations, and mouse aiming."""
    
    global story_timer, story_char_index, in_story_screen
    global moving_walls_offset, moving_walls_dir, platform_timer, disappearing_tiles_active
    global wall_invincibility_timer, game_paused, game_over
    global player_yaw, camera_yaw, player_pitch, last_mouse_x, last_mouse_y, mouse_initialized

    if in_story_screen:
        story_timer += 1
        if story_timer % 2 == 0 and story_char_index < total_story_len:  # typewriter speed
            story_char_index += 1
        glutPostRedisplay()
        return

    if game_paused or game_over:
        glutPostRedisplay()
        return

    # Continuous mouse aiming via Win32 cursor tracking
    try:
        class _POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        class _RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd:
            _pt = _POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(_pt))
            if ctypes.windll.user32.WindowFromPoint(_pt) == hwnd:
                global is_cursor_hidden
                if not is_cursor_hidden:
                    while ctypes.windll.user32.ShowCursor(False) >= 0:
                        pass
                    is_cursor_hidden = True

                _rect = _RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(_rect))
                win_cx = (_rect.left + _rect.right) // 2
                win_cy = (_rect.top + _rect.bottom) // 2
                dx = _pt.x - win_cx
                dy = _pt.y - win_cy
                if dx != 0 or dy != 0:
                    mouse_sensitivity = 0.20
                    if first_person:
                        camera_yaw = (camera_yaw - dx * mouse_sensitivity) % 360.0
                        player_pitch = max(-65.0, min(65.0, player_pitch - dy * mouse_sensitivity))
                    else:
                        camera_yaw = (camera_yaw - dx * mouse_sensitivity) % 360.0
                        player_pitch = max(-25.0, min(75.0, player_pitch + dy * mouse_sensitivity))
                    ctypes.windll.user32.SetCursorPos(win_cx, win_cy)
            else:
                if is_cursor_hidden:
                    while ctypes.windll.user32.ShowCursor(True) < 0:
                        pass
                    is_cursor_hidden = False
                last_mouse_x = _pt.x
                last_mouse_y = _pt.y
        else:
            if is_cursor_hidden:
                while ctypes.windll.user32.ShowCursor(True) < 0:
                    pass
                is_cursor_hidden = False
    except:
        pass

    update_player_physics()

    if wall_invincibility_timer > 0:
        wall_invincibility_timer -= 1

    if anim_moving_walls:
        moving_walls_offset += 0.05 * moving_walls_dir
        if moving_walls_offset > 1.8 or moving_walls_offset < 0.0:
            moving_walls_dir *= -1.0

    if anim_disappearing_floor:
        platform_timer += 1
        if platform_timer % 90 == 0:
            idx = (platform_timer // 90) % len(disappearing_tiles_active)
            disappearing_tiles_active[idx] = not disappearing_tiles_active[idx]

    # Halt walk animation a few ticks after movement keys stop firing.
    # OS key-repeat leaves small gaps, so threshold must be > that gap.
    global _idle_ticks_since_move, is_walking
    if is_walking:
        _idle_ticks_since_move += 1
        if _idle_ticks_since_move > 6:
            is_walking = False

    glutPostRedisplay()

# -----------------------------------------------------------------------------
# Input & Collision
# -----------------------------------------------------------------------------
def is_valid_walkway_position(x, z):
    """
    Returns True if (x, z) is inside any valid playable maze corridor segment.
    Prevents player from phasing through walls into outside void space.
    """
    # 1. Start Hub (X: -5.5 -> +5.5, Z: 0.0 -> 56.0)
    if -5.5 <= x <= 5.5 and 0.0 <= z <= 56.0:
        return True

    if -5.5 <= x <= 5.5 and 54.0 <= z <= 65.2:        return True  # junction A
    if 5.5 < x <= 45.0 and 54.8 <= z <= 65.2:          return True
    if 34.8 <= x <= 45.2 and 54.8 <= z <= 125.2:       return True  # lava corridor
    if -45.2 <= x <= 45.2 and 114.8 <= z <= 125.2:     return True  # junction B
    if -45.2 <= x <= -34.8 and 114.8 <= z <= 185.2:    return True  # disappearing floor
    if -45.2 <= x <= 25.2 and 174.8 <= z <= 185.2:     return True  # junction C
    if 14.8 <= x <= 25.2 and 174.8 <= z <= 245.2:      return True  # laser gauntlet
    if 14.8 <= x <= 75.2 and 234.8 <= z <= 245.2:      return True  # junction D
    if 64.8 <= x <= 75.2 and 234.8 <= z <= 339.6:      return True  # exit chamber
    return False

PLAYER_RADIUS = 0.42  # Collision radius to prevent phasing through walls
PILLAR_HALF_SIZE = 0.75  # Half-width of 1.4 unit wide square pillars

def collides_with_pillar(x, z, r=PLAYER_RADIUS):
    """Returns True if (x, z) with radius r intersects any solid pillar."""
    min_dist = PILLAR_HALF_SIZE + r
    for px, pz in PILLAR_COORDS:
        if abs(x - px) < min_dist and abs(z - pz) < min_dist:
            return True
    return False

def collides_with_wall(x, z, r=PLAYER_RADIUS):
    """Returns True if (x, z) with radius r intersects any solid maze wall segment."""
    for cx, cy, cz, sx, sy, sz in MAZE_WALL_SEGMENTS:
        hx = sx / 2.0 + r
        hz = sz / 2.0 + r
        if abs(x - cx) < hx and abs(z - cz) < hz:
            return True
    return False

BASALT_LEDGE_BOXES = [
    (40.0 + sign_x * (5.6 - 0.6), float(z_side) + 3.0, 1.3, 5.6)
    for z_side in range(int(65.6), int(114.4), 6)
    for sign_x in [-1.0, 1.0]
]

def collides_with_ledge(x, z, r=PLAYER_RADIUS):
    """Returns True if (x, z) with radius r intersects any solid basalt side ledge."""
    for lx, lz, sx, sz in BASALT_LEDGE_BOXES:
        hx = sx / 2.0 + r
        hz = sz / 2.0 + r
        if abs(x - lx) < hx and abs(z - lz) < hz:
            return True
    return False

def resolve_pillar_collision(x, z, r=PLAYER_RADIUS):
    """Pushes (x, z) outside any intersecting pillar to prevent penetration."""
    min_dist = PILLAR_HALF_SIZE + r
    for px, pz in PILLAR_COORDS:
        dx = x - px
        dz = z - pz
        if abs(dx) < min_dist and abs(dz) < min_dist:
            overlap_x = min_dist - abs(dx)
            overlap_z = min_dist - abs(dz)
            if overlap_x < overlap_z:
                x = px + math.copysign(min_dist, dx if dx != 0.0 else 1.0)
            else:
                z = pz + math.copysign(min_dist, dz if dz != 0.0 else 1.0)
    return x, z

def resolve_ledge_collision(x, z, r=PLAYER_RADIUS):
    """Pushes (x, z) outside any intersecting basalt ledge so player cannot penetrate."""
    for lx, lz, sx, sz in BASALT_LEDGE_BOXES:
        hx = sx / 2.0 + r
        hz = sz / 2.0 + r
        dx = x - lx
        dz = z - lz
        if abs(dx) < hx and abs(dz) < hz:
            overlap_x = hx - abs(dx)
            overlap_z = hz - abs(dz)
            if overlap_x < overlap_z:
                x = lx + math.copysign(hx, dx if dx != 0.0 else 1.0)
            else:
                z = lz + math.copysign(hz, dz if dz != 0.0 else 1.0)
    return x, z

def try_move_player(dx, dz):
    """Moves the player by (dx, dz) with wall/pillar sliding collision."""
    
    global walk_cycle_phase, is_walking, _idle_ticks_since_move

    new_x = player_pos[0] + dx
    new_z = player_pos[2] + dz

    moved = False
    r = PLAYER_RADIUS

    def pos_ok(x, z):
        if collides_with_pillar(x, z, r) or collides_with_wall(x, z, r) or collides_with_ledge(x, z, r):
            return False
        return (is_valid_walkway_position(x, z) and
                is_valid_walkway_position(x - r, z) and
                is_valid_walkway_position(x + r, z) and
                is_valid_walkway_position(x, z - r) and
                is_valid_walkway_position(x, z + r))

    if pos_ok(new_x, new_z):
        player_pos[0] = new_x
        player_pos[2] = new_z
        moved = True
    elif pos_ok(new_x, player_pos[2]):  # slide along X
        player_pos[0] = new_x
        moved = True
    elif pos_ok(player_pos[0], new_z):  # slide along Z
        player_pos[2] = new_z
        moved = True

    # Final push-out to prevent glitching inside pillars or ledges
    player_pos[0], player_pos[2] = resolve_pillar_collision(player_pos[0], player_pos[2], r)
    player_pos[0], player_pos[2] = resolve_ledge_collision(player_pos[0], player_pos[2], r)

    if moved:
        walk_cycle_phase += 0.35
        is_walking = True
        _idle_ticks_since_move = 0

def reset_game():
    """Resets all player, physics, and hazard state to initial level defaults."""
    
    global player_pos, player_yaw, camera_yaw, player_pitch, crouching, first_person, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text
    global consecutive_wall_hits, wall_invincibility_timer, cheat_mode, game_over, game_paused
    global moving_walls_offset, moving_walls_dir
    global walk_cycle_phase, is_walking, _idle_ticks_since_move
    global last_mouse_x, last_mouse_y, mouse_initialized

    player_pos = [0.0, 0.0, 7.4]
    player_yaw = 0.0
    camera_yaw = 0.0
    player_pitch = 0.0
    mouse_initialized = False
    crouching = False
    is_jumping = False
    y_velocity = 0.0
    consecutive_lava_falls = 0
    lava_alert_timer = 0
    lava_alert_expiry = 0.0
    hazard_alert_text = "Fell into the lava!"
    consecutive_wall_hits = 0
    wall_invincibility_timer = 0
    cheat_mode = False
    walk_cycle_phase = 0.0
    is_walking = False
    _idle_ticks_since_move = 0
    game_over = False
    game_paused = False
    moving_walls_offset = 0.0
    moving_walls_dir = 1.0

def keyboard_listener(key, x, y):
    """Keyboard input handler: WASD move, Space jump, Ctrl crouch, C cheat, P pause, V camera."""
    
    global in_story_screen, player_pos, player_yaw, camera_yaw, crouching, first_person, anim_moving_walls, anim_disappearing_floor
    global is_jumping, y_velocity, game_paused
    global consecutive_lava_falls, lava_alert_timer, game_over
    global consecutive_wall_hits, wall_invincibility_timer, cheat_mode, hazard_alert_text

    try:
        ch = key.decode('utf-8').lower()
    except:
        ch = str(key).lower()

    if in_story_screen:
        if ch in (' ', '\r', '\n') or key in (b' ', b'\r', b'\n'):
            in_story_screen = False
            glutPostRedisplay()
        return

    if ch == 'r':
        reset_game()
        glutPostRedisplay()
        return

    if ch == 'c':
        cheat_mode = not cheat_mode
        glutPostRedisplay()
        return

    if ch == 'p':
        game_paused = not game_paused
        glutPostRedisplay()
        return

    if key == b'\x1b' or ch == 'q':
        try:
            glutLeaveMainLoop()
        except:
            sys.exit(0)

    if game_paused or game_over:
        return

    rad = math.radians(camera_yaw)

    if ch == 'w':
        player_yaw = camera_yaw
        try_move_player(math.sin(rad) * player_speed, math.cos(rad) * player_speed)
    elif ch == 's':
        player_yaw = (camera_yaw + 180.0) % 360.0
        try_move_player(-math.sin(rad) * player_speed, -math.cos(rad) * player_speed)
    elif ch == 'a':
        player_yaw = (camera_yaw + 90.0) % 360.0
        try_move_player(math.sin(rad + math.pi/2.0) * player_speed, math.cos(rad + math.pi/2.0) * player_speed)
    elif ch == 'd':
        player_yaw = (camera_yaw - 90.0) % 360.0
        try_move_player(math.sin(rad - math.pi/2.0) * player_speed, math.cos(rad - math.pi/2.0) * player_speed)
    elif ch == ' ' or key == b' ':
        if not is_jumping:
            is_jumping = True
            y_velocity = jump_strength
    elif ch == 'v':
        first_person = not first_person
    elif ch in ('x', 'z') or key in (b'x', b'z'):
        crouching = not crouching
    elif ch == 'm':
        anim_moving_walls = not anim_moving_walls
    elif ch == 't':
        anim_disappearing_floor = not anim_disappearing_floor

    glutPostRedisplay()

def special_key_listener(key, x, y):
    """Special keys: Ctrl/Shift toggle crouch."""
    global crouching
    if key in (114, 115, 112, 113):  # Ctrl-L, Ctrl-R, Shift-L, Shift-R
        crouching = not crouching
        glutPostRedisplay()

def mouse_listener(button, state, x, y):
    """Mouse click: Right-click toggles camera view."""
    
    global first_person
    if state == GLUT_DOWN:
        if button == GLUT_RIGHT_BUTTON:
            first_person = not first_person
            glutPostRedisplay()

def mouse_motion(x, y):
    """Direct mouse motion handler for drag / look-at (glutMotionFunc)."""
    global camera_yaw, player_pitch, last_mouse_x, last_mouse_y, mouse_initialized
    if not mouse_initialized:
        last_mouse_x = x
        last_mouse_y = y
        mouse_initialized = True
        return
    dx = x - last_mouse_x
    dy = y - last_mouse_y
    sensitivity = 0.20
    if first_person:
        camera_yaw = (camera_yaw - dx * sensitivity) % 360.0
        player_pitch = max(-65.0, min(65.0, player_pitch - dy * sensitivity))
    else:
        camera_yaw = (camera_yaw - dx * sensitivity) % 360.0
        player_pitch = max(-25.0, min(75.0, player_pitch + dy * sensitivity))
    last_mouse_x = x
    last_mouse_y = y

def passive_motion(x, y):
    """Passive mouse movement tracking (glutPassiveMotionFunc)."""
    mouse_motion(x, y)

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(WINDOW_TITLE)

    load_character_model()

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)

    glutMainLoop()

if __name__ == "__main__":
    main()
