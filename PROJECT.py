######################################################LEVEL 1 FILE######################################
import math
import random
import sys
import ctypes
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750
WINDOW_TITLE = b"9 Lives - Level 1: Connected Backrooms Maze Arena ('tung tung tung sahur')"


player_pos = [0.0, 1.0, 7.4]     
player_yaw = 0.0                 
player_pitch = 0.0                
player_speed = 0.90        
crouching = False                
walk_cycle_phase = 0.0            
is_walking = False                
_idle_ticks_since_move = 0       
eye_height = 1.6                 


is_jumping = False
y_velocity = 0.0
gravity = -0.014
jump_strength = 0.28
ground_y = 1.0                    

first_person = False              
cam_dist = 6.5                    
cam_height = 3.8                  

last_mouse_x = 0
last_mouse_y = 0
mouse_initialized = False


moving_walls_offset = 0.0         
moving_walls_dir = 1.0
anim_moving_walls = True

platform_timer = 0
disappearing_tiles_active = [True, True, True, True, True, True]
anim_disappearing_floor = True


game_paused = False


consecutive_lava_falls = 0
lava_alert_timer = 0           
hazard_alert_text = "Fell into the lava!"
game_over = False


consecutive_wall_hits = 0
wall_invincibility_timer = 0   

cheat_mode = False


in_story_screen = True
story_lines = [
    "Tung Tung Tung Sahur has wandered into the Evil Cat World!",
    "Armed with 9 Lives, you must survive the traps and",
    "defeat the wicked cats trying to take over the world."
]
story_char_index = 0
story_timer = 0
total_story_len = sum(len(line) for line in story_lines)


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


c_body = (222/255, 137/255, 34/255)
c_dark = (117/255, 76/255, 18/255)
c_goggle = (229/255, 230/255, 230/255)
c_white = (1.0, 1.0, 1.0)

def load_character_model():
    global c_body, c_dark, c_goggle, c_white
    c_body = (222/255, 137/255, 34/255)
    c_dark = (117/255, 76/255, 18/255)
    c_goggle = (229/255, 230/255, 230/255)
    c_white = (1.0, 1.0, 1.0)


def draw_box(sx, sy, sz, color_top=None, color_side=None):
   
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

def draw_bar_2d(x, y, w, h, fill_pct, fill_color, border_color=(0.9, 0.9, 0.9)):
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


def draw_character(cam_x=0.0, cam_z=0.0):
    if first_person:
        return

    glPushMatrix()
    curr_y = player_pos[1]
    glTranslatef(player_pos[0], curr_y, player_pos[2])
    glRotatef(player_yaw + 180.0, 0, 1, 0)

    glRotatef(-90, 1, 0, 0)
    glRotatef(180, 0, 0, 1)

    scale_factor = 0.008
    if crouching:
        glScalef(scale_factor, scale_factor * 0.5, scale_factor)
    else:
        glScalef(scale_factor, scale_factor, scale_factor)

    glTranslatef(0, 0, 14.0)

    rad_yaw = math.radians(player_yaw)
    fwd_x = math.sin(rad_yaw)
    fwd_z = math.cos(rad_yaw)
    to_cam_x = cam_x - player_pos[0]
    to_cam_z = cam_z - player_pos[2]
    is_front = (fwd_x * to_cam_x + fwd_z * to_cam_z) > 0.0

    def draw_face_details():
        for eye_x in [-16, 16]:
            glPushMatrix()
            glColor3f(*c_goggle)
            glTranslatef(eye_x, 21, 160)
            glScalef(0.28, 0.08, 0.35)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_white)
            glTranslatef(eye_x, 25, 160)
            glScalef(0.18, 0.08, 0.22)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_dark)
            glTranslatef(eye_x, 29, 160)
            glScalef(0.08, 0.05, 0.1)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_dark)
            glTranslatef(eye_x, 22, 185)
            glScalef(0.25, 0.06, 0.06)
            glutSolidCube(100)
            glPopMatrix()

       
        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(0, 22, 138)
        glScalef(0.06, 0.06, 0.16)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(-2, 22, 122)
        glScalef(0.38, 0.06, 0.06)
        glutSolidCube(100)
        glPopMatrix()

    if not is_front:
        draw_face_details()

    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 120)
    glScalef(0.65, 0.4, 1.8)
    glutSolidCube(100)
    glPopMatrix()

    if is_front:
        draw_face_details()

    for side_x in [-38.5, 38.5]:
        glPushMatrix()
        glColor3f(*c_body)
        glTranslatef(side_x, 0, 95)
        glScalef(0.12, 0.2, 0.9)
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


def draw_connected_floor_pathways():

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

    glPushMatrix()
    glTranslatef(20.0, -0.1, 60.0)
    draw_box(52.0, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()


    glPushMatrix()
    glTranslatef(0.0, -0.1, 120.0)
    draw_box(92.0, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-40.0, -0.1, 128.0)
    draw_box(11.2, 0.2, 5.6, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-40.0, -0.1, 172.0)
    draw_box(11.2, 0.2, 5.6, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-10.2, -0.1, 180.0)
    draw_box(71.6, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(20.0, -0.1, 210.0)
    draw_box(11.2, 0.2, 48.8, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(45.0, -0.1, 240.0)
    draw_box(61.2, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(70.0, -0.1, 292.8)
    draw_box(11.2, 0.2, 94.4, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()


MAZE_WALL_SEGMENTS = [
    (0.0, 3.5, -0.4, 13.6, 7.0, 0.8),          
    (-6.4, 3.5, 27.0, 0.8, 7.0, 54.8),         
    (6.4, 3.5, 27.0, 0.8, 7.0, 54.8),          
    (-6.4, 3.5, 60.0, 0.8, 7.0, 12.0),         
    (13.8, 3.5, 65.6, 41.2, 7.0, 0.8),         
    (26.0, 3.5, 54.4, 40.0, 7.0, 0.8),         
    (34.4, 3.5, 90.2, 0.8, 7.0, 49.2),        
    (45.6, 3.5, 87.0, 0.8, 7.0, 66.0),         
    (45.6, 3.5, 120.0, 0.8, 7.0, 12.0),        
    (5.8, 3.5, 125.6, 80.4, 7.0, 0.8),         
    (-5.8, 3.5, 114.4, 80.4, 7.0, 0.8),        
    (-45.6, 3.5, 147.5, 0.8, 7.0, 67.0),       
    (-34.4, 3.5, 147.2, 0.8, 7.0, 56.0),       
    (-45.6, 3.5, 180.0, 0.8, 7.0, 12.0),       
    (-15.8, 3.5, 185.6, 60.4, 7.0, 0.8),      
    (-4.5, 3.5, 174.4, 61.0, 7.0, 0.8),        
    (14.4, 3.5, 215.5, 0.8, 7.0, 61.0),        
    (25.6, 3.5, 210.0, 0.8, 7.0, 66.0),        
    (50.8, 3.5, 234.4, 50.4, 7.0, 0.8),       
    (39.8, 3.5, 245.6, 51.6, 7.0, 0.8),        
    (64.4, 3.5, 292.8, 0.8, 7.0, 95.2),       
    (75.6, 3.5, 287.2, 0.8, 7.0, 106.4),       
    (70.0, 3.5, 340.4, 12.0, 7.0, 0.8),        
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

    for px, pz in PILLAR_COORDS:
        glPushMatrix()
        glTranslatef(px, 3.5, pz)
        draw_box(1.4, 7.0, 1.4, color_top=COLOR_PILLAR, color_side=(0.12, 0.12, 0.14))
        glPopMatrix()

        glPushMatrix()
        glTranslatef(px, 6.2, pz)
        draw_box(1.6, 0.4, 1.6, color_top=COLOR_CYAN_GLOW, color_side=(0.0, 0.6, 0.8))
        glPopMatrix()


LAVA_TILE_ROCKS = [
    (40.0,  68.0,  3.6, 4.2,  0.0),   
    (38.8,  74.3,  3.6, 4.2,  6.0),   
    (41.2,  80.6,  3.6, 4.2, -6.0),   
    (38.8,  86.9,  3.6, 4.2,  5.0),   
    (41.2,  93.2,  3.6, 4.2, -5.0),   
    (38.8,  99.5,  3.6, 4.2,  6.0),   
    (41.2, 105.8,  3.6, 4.2, -6.0),   
    (40.0, 112.0,  3.6, 4.2,  0.0),   
]

def draw_lava_base_only():

    CX   = 40.0       
    CXHW = 5.6         
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

    for z_tile in range(int(ZSTART) + 2, int(ZEND) - 2, 3):
        for x_off in [-3.8, -1.9, 0.0, 1.9, 3.8]:
            glPushMatrix()
            glTranslatef(CX + x_off, 0.15, float(z_tile))
            draw_box(1.5, 0.08, 2.2,
                     color_top=(0.14, 0.11, 0.12),
                     color_side=(0.75, 0.20, 0.0))
            glPopMatrix()

def _draw_lava_spike(x, y, z, base_w=0.35, height=1.5):
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

    draw_lava_base_and_tiles()
    for rx, rz, sx, sz, tilt in LAVA_TILE_ROCKS:
        draw_lava_tile_rock(rx, rz, sx, sz, tilt)


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


LASER_BEAMS = [
    (192.0, 2.2,  COLOR_LASER_RED, "Laser 1 (Z: 192.0, Y: 2.2) - High Beam (Crouch Under)"),
    (202.0, 0.65, COLOR_LASER_RED, "Laser 2 (Z: 202.0, Y: 0.65) - Low Beam (Jump Over)"),
    (212.0, 2.2,  COLOR_LASER_RED, "Laser 3 (Z: 212.0, Y: 2.2) - High Beam (Crouch Under)"),
    (222.0, 0.65, COLOR_LASER_RED, "Laser 4 (Z: 222.0, Y: 0.65) - Low Beam (Jump Over)"),
    (232.0, 1.8,  COLOR_LASER_RED, "Laser 5 (Z: 232.0, Y: 1.8) - Mid-High Beam (Crouch Dodge)")
]

def draw_laser_emitters():

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
        draw_box(10.0, 0.08, 0.08, color_top=color_rgb, color_side=color_rgb)
        draw_box(10.0, 0.03, 0.03, color_top=(1.0, 1.0, 1.0), color_side=(1.0, 1.0, 1.0))
        glPopMatrix()


MOVING_WALL_PAIRS = [
    (260.0,  1.0),  
    (275.0, -1.0),   
    (290.0,  1.0),   
]
MOVING_WALL_CX = 70.0      
MOVING_WALL_BLOCK_W = 3.0  
MOVING_WALL_REST_L = 65.5  
MOVING_WALL_REST_R = 74.5  

def draw_moving_walls():
 
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


def setup_camera():
    
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(WINDOW_WIDTH) / float(WINDOW_HEIGHT), 0.1, 400.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    rad_yaw = math.radians(player_yaw)
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
        cam_x = player_pos[0] - math.sin(rad_yaw) * cam_dist
        cam_y = player_pos[1] + cam_height
        cam_z = player_pos[2] - math.cos(rad_yaw) * cam_dist

        center_x = cam_x + math.sin(rad_yaw) * math.cos(rad_pitch) * 100.0
        center_y = cam_y + math.sin(rad_pitch) * 100.0
        center_z = cam_z + math.cos(rad_yaw) * math.cos(rad_pitch) * 100.0

        gluLookAt(cam_x, cam_y, cam_z,
                  center_x, center_y, center_z,
                  0.0, 1.0, 0.0)

def draw_rect_2d(x1, y1, x2, y2, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()

def draw_rect_border_2d(x1, y1, x2, y2, color, line_width=2.0):
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

    title_str = "★  9 LIVES: EVIL CAT WORLD  ★"
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
        (1.0, 0.88, 0.35),  
        (0.95, 0.92, 0.85), 
        (0.95, 0.92, 0.85)  
    ]

    for i, line in enumerate(story_lines):
        if chars_left <= 0:
            break
        visible_text = line[:chars_left]
        chars_left -= len(line)

        l_w = len(line) * 9.2
        start_x = (WINDOW_WIDTH - l_w) // 2
        line_y = body_center_y + line_y_offsets[i]

        glColor3f(*line_colors[i])
        glRasterPos2f(start_x, line_y)
        for ch in visible_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    prompt_str = "PRESS SPACE OR ENTER TO START"
    p_w = len(prompt_str) * 9.2
    p_start_x = (WINDOW_WIDTH - p_w) // 2
    prompt_y = py1 + 35

    pulse_val = 0.5 + 0.5 * math.sin(story_timer * 0.08)

    box_x1 = p_start_x - 24
    box_x2 = p_start_x + p_w + 24
    box_y1 = prompt_y - 10
    box_y2 = prompt_y + 26

    # Draw prompt button background & glowing border frame
    draw_rect_2d(box_x1, box_y1, box_x2, box_y2, (0.05, 0.12 + 0.10 * pulse_val, 0.20 + 0.15 * pulse_val))
    draw_rect_border_2d(box_x1, box_y1, box_x2, box_y2, (0.0, 0.70 + 0.30 * pulse_val, 0.90 + 0.10 * pulse_val), line_width=2.0)

    # Render prompt text perfectly centered inside button bar
    glColor3f(0.85 + 0.15 * pulse_val, 0.95 + 0.05 * pulse_val, 1.0)
    glRasterPos2f(p_start_x, prompt_y)
    for ch in prompt_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glutSwapBuffers()

def display():
    update_window_dimensions()

    if in_story_screen:
        draw_story_screen()
        return

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    setup_camera()

    draw_connected_floor_pathways()
    draw_lava_base_only()

    rad = math.radians(player_yaw)
    curr_eye_h = 0.8 if crouching else eye_height

    if first_person:
        cam_x = player_pos[0]
        cam_y = player_pos[1] + curr_eye_h
        cam_z = player_pos[2]
    else:
        cam_x = player_pos[0] - math.sin(rad) * cam_dist
        cam_y = player_pos[1] + cam_height
        cam_z = player_pos[2] - math.cos(rad) * cam_dist

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
            if wall_invincibility_timer > 0:
                if (wall_invincibility_timer // 10) % 2 == 0:
                    draw_character(cam_x, cam_z)
            else:
                draw_character(cam_x, cam_z)
        render_list.append((player_pos[0], player_pos[1] + 0.8, player_pos[2], _draw_player))

    def _dist_sq(entity):
        ex, ey, ez, fn = entity
        return (ex - cam_x)**2 + (ey - cam_y)**2 + (ez - cam_z)**2

    render_list.sort(key=_dist_sq, reverse=True)

    for ex, ey, ez, fn in render_list:
        fn()

    remaining_lives = max(0, 9 - consecutive_lava_falls)
    player_pct = remaining_lives / 9.0

    if player_pct > 0.5:
        bar_color = (0.1, 0.9, 0.2)   
    elif player_pct > 0.25:
        bar_color = (1.0, 0.8, 0.0)    
    else:
        bar_color = (1.0, 0.15, 0.15) 

    pw, ph = 220, 16
    px, py = 15, WINDOW_HEIGHT - 35
    draw_bar_2d(px, py, pw, ph, player_pct, bar_color, border_color=(0.9, 0.9, 0.9))
    draw_text(px + pw + 12, py + 1, f"Lives ({remaining_lives}/9)")

    draw_text(15, WINDOW_HEIGHT - 65, f"Crouch: {'ON' if crouching else 'OFF'}")
    if cheat_mode:
        draw_text(15, WINDOW_HEIGHT - 90, "Cheat Mode Activated", color=(1.0, 0.15, 0.15))

    if game_over:
        draw_text(15, WINDOW_HEIGHT - 120, "GAME OVER! All 9 Lifelines lost. Press 'R' to restart.")
    elif game_paused:
        draw_text(15, WINDOW_HEIGHT - 120, "GAME PAUSED (Press 'P' to Resume)")
    elif lava_alert_timer > 0:
        draw_text(15, WINDOW_HEIGHT - 120, f"ALERT: {hazard_alert_text}")

    draw_text(15, 20, "WASD: Move | Mouse: Aim | Space: Jump | Ctrl/X: Crouch | V/RMB: Camera | P: Pause | C: God Mode | R: Reset", font=GLUT_BITMAP_HELVETICA_12)

    glutSwapBuffers()


LAVA_PIT_X_MIN  = 34.4
LAVA_PIT_X_MAX  = 45.6
LAVA_PIT_1_ZMIN = 66.0     
LAVA_PIT_1_ZMAX = 114.4    

STEP_TOP_Y = 1.34


STEPPING_BOXES = [
    (40.0,  68.0, 1.8, 2.1),  
    (38.8,  74.3, 1.8, 2.1),  
    (41.2,  80.6, 1.8, 2.1),  
    (38.8,  86.9, 1.8, 2.1),  
    (41.2,  93.2, 1.8, 2.1), 
    (38.8,  99.5, 1.8, 2.1),  
    (41.2, 105.8, 1.8, 2.1), 
    (40.0, 112.0, 1.8, 2.1), 
]

def on_stepping_box():
    px, pz = player_pos[0], player_pos[2]
    for (bx, bz, hx, hz) in STEPPING_BOXES:
        if (bx - hx) <= px <= (bx + hx) and (bz - hz) <= pz <= (bz + hz):
            return True
    return False

def in_lava_pit():
    px, pz = player_pos[0], player_pos[2]
    in_x  = LAVA_PIT_X_MIN <= px <= LAVA_PIT_X_MAX
    in_z  = LAVA_PIT_1_ZMIN <= pz <= LAVA_PIT_1_ZMAX
    return in_x and in_z and not on_stepping_box()

def check_laser_collisions():
    global player_pos, player_yaw, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over

    if cheat_mode:
        return False

    px, py, pz = player_pos[0], player_pos[1], player_pos[2]

    if not (14.4 <= px <= 25.6 and 180.0 <= pz <= 240.0):
        return False

    player_is_dodging = crouching or is_jumping or (py > ground_y + 0.15)

    for lz, ly, color_rgb, desc in LASER_BEAMS:
        if abs(pz - lz) <= 0.7:
            if not player_is_dodging:
                consecutive_lava_falls += 1
                hazard_alert_text = "Hit by Laser! (Crouch 'CTRL' or Jump 'SPACE' to dodge)"
                lava_alert_timer = 180
                if consecutive_lava_falls >= 9:
                    game_over = True
                player_pos = [20.0, 1.0, 182.0]
                player_yaw = 0.0
                is_jumping = False
                y_velocity = 0.0
                return True
    return False

def check_moving_wall_collisions():

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
        if abs(pz - wz) < 4.0:
            offset = moving_walls_offset * phase

            left_inner_edge = (MOVING_WALL_REST_L + offset) + MOVING_WALL_BLOCK_W / 2.0
            right_inner_edge = (MOVING_WALL_REST_R - offset) - MOVING_WALL_BLOCK_W / 2.0

            
            if px <= left_inner_edge or px >= right_inner_edge:
                consecutive_wall_hits += 1
                consecutive_lava_falls += 1
                hazard_alert_text = "Crushed by Moving Walls!"
                lava_alert_timer = 180
                wall_invincibility_timer = 60  

                if consecutive_lava_falls >= 9:
                    game_over = True

                if consecutive_wall_hits >= 3:
                   
                    player_pos = [70.0, 1.0, 245.0]
                    player_yaw = 0.0
                    consecutive_wall_hits = 0
                else:
                   
                    player_pos[0] = MOVING_WALL_CX

                is_jumping = False
                y_velocity = 0.0
                return True
    return False

def is_on_active_disappearing_tile(px, pz):
    for tile_x, tile_z, color_idx in DISAPPEARING_TILE_COORDS:
        if (tile_x - 1.4) <= px <= (tile_x + 1.4) and (tile_z - 2.0) <= pz <= (tile_z + 2.0):
            if disappearing_tiles_active[color_idx]:
                return True
    return False

def check_disappearing_floor():
    global player_pos, player_yaw, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over

    if cheat_mode:
        return False

    px, py, pz = player_pos[0], player_pos[1], player_pos[2]

    if not (-45.6 <= px <= -34.4 and 135.0 <= pz <= 165.0):
        return False

    if py > ground_y + 0.15:
        return False

    if not is_on_active_disappearing_tile(px, pz):
        consecutive_lava_falls += 1
        hazard_alert_text = "Fell into the void!"
        lava_alert_timer = 180
        if consecutive_lava_falls >= 9:
            game_over = True
        player_pos = [-40.0, 1.0, 128.0]
        player_yaw = 0.0
        is_jumping = False
        y_velocity = 0.0
        return True

    return False

def update_player_physics():
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
                    hazard_alert_text = "Fell into the lava!"
                    lava_alert_timer = 180          
                    if consecutive_lava_falls >= 9:
                        game_over = True
                   
                    player_pos = [40.0, 1.0, 65.0]
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
                hazard_alert_text = "Fell into the lava!"
                lava_alert_timer = 180
                if consecutive_lava_falls >= 9:
                    game_over = True
                player_pos = [40.0, 1.0, 65.0]
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
   
    global story_timer, story_char_index, in_story_screen
    global moving_walls_offset, moving_walls_dir, platform_timer, disappearing_tiles_active
    global wall_invincibility_timer, game_paused, game_over
    global player_yaw, player_pitch, last_mouse_x, last_mouse_y, mouse_initialized

    if in_story_screen:
        story_timer += 1
        if story_timer % 2 == 0 and story_char_index < total_story_len:
            story_char_index += 1
        glutPostRedisplay()
        return

    if game_paused or game_over:
        glutPostRedisplay()
        return

    try:
        class _POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        _pt = _POINT()
        if ctypes.windll.user32.GetCursorPos(ctypes.byref(_pt)):
            if mouse_initialized:
                dx = _pt.x - last_mouse_x
                dy = _pt.y - last_mouse_y
                if dx != 0 or dy != 0:
                    mouse_sensitivity = 0.28
                    player_yaw = (player_yaw + dx * mouse_sensitivity) % 360.0
                    player_pitch = max(-65.0, min(65.0, player_pitch - dy * mouse_sensitivity))
            else:
                mouse_initialized = True
            last_mouse_x = _pt.x
            last_mouse_y = _pt.y
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

   
    global _idle_ticks_since_move, is_walking
    if is_walking:
        _idle_ticks_since_move += 1
        if _idle_ticks_since_move > 6:
            is_walking = False

    glutPostRedisplay()

def is_valid_walkway_position(x, z):
    if -5.5 <= x <= 5.5 and 0.0 <= z <= 54.4:
        return True

   
    if -5.5 <= x <= 45.0 and 54.8 <= z <= 65.2:
        return True

   
    if 34.8 <= x <= 45.2 and 54.8 <= z <= 125.2:
        return True

  
    if -45.2 <= x <= 45.2 and 114.8 <= z <= 125.2:
        return True

   
    if -45.2 <= x <= -34.8 and 114.8 <= z <= 185.2:
        return True

   
    if -45.2 <= x <= 25.2 and 174.8 <= z <= 185.2:
        return True

   
    if 14.8 <= x <= 25.2 and 174.8 <= z <= 245.2:
        return True

   
    if 14.8 <= x <= 75.2 and 234.8 <= z <= 245.2:
        return True

   
    if 64.8 <= x <= 75.2 and 234.8 <= z <= 339.6:
        return True

    return False

def try_move_player(dx, dz):
    global walk_cycle_phase, is_walking, _idle_ticks_since_move

    new_x = player_pos[0] + dx
    new_z = player_pos[2] + dz

    moved = False

  
    if is_valid_walkway_position(new_x, new_z):
        player_pos[0] = new_x
        player_pos[2] = new_z
        moved = True
   
    elif is_valid_walkway_position(new_x, player_pos[2]):
        player_pos[0] = new_x
        moved = True
    
    elif is_valid_walkway_position(player_pos[0], new_z):
        player_pos[2] = new_z
        moved = True

    if moved:
        walk_cycle_phase += 0.35
        is_walking = True
        _idle_ticks_since_move = 0

def reset_game():
  
    global player_pos, player_yaw, player_pitch, crouching, first_person, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text
    global consecutive_wall_hits, wall_invincibility_timer, cheat_mode, game_over, game_paused
    global moving_walls_offset, moving_walls_dir
    global walk_cycle_phase, is_walking, _idle_ticks_since_move
    global last_mouse_x, last_mouse_y, mouse_initialized

    player_pos = [0.0, 1.0, 7.4]
    player_yaw = 0.0
    player_pitch = 0.0
    mouse_initialized = False
    crouching = False
    is_jumping = False
    y_velocity = 0.0
    consecutive_lava_falls = 0
    lava_alert_timer = 0
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
   
    global in_story_screen, player_pos, player_yaw, crouching, first_person, anim_moving_walls, anim_disappearing_floor
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

    rad = math.radians(player_yaw)

    
    if ch == 'w':
        try_move_player(math.sin(rad) * player_speed, math.cos(rad) * player_speed)
    elif ch == 's':
        try_move_player(-math.sin(rad) * player_speed, -math.cos(rad) * player_speed)

   
    elif ch == 'a':
        try_move_player(math.sin(rad + math.pi/2.0) * player_speed, math.cos(rad + math.pi/2.0) * player_speed)
    elif ch == 'd':
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
    global crouching
    if key in (114, 115, 112, 113):  
        crouching = not crouching
        glutPostRedisplay()

def mouse_listener(button, state, x, y):
    global first_person
    if state == GLUT_DOWN:
        if button == GLUT_RIGHT_BUTTON:
            first_person = not first_person
            glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(WINDOW_TITLE)

    load_character_model()

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)

    print("=================================================================")
    print(" '9 Lives' - Level 1: Fully Connected Backrooms Maze Arena")
    print(" Sole Active Character: 'tung tung tung sahur'")
    print("=================================================================")

    glutMainLoop()

if __name__ == "__main__":
    main()



######################################################LEVEL 2 FILE######################################
import math
import random
import sys
import ctypes
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

WIN_W = 1000
WIN_H = 750
WINDOW_TITLE = b"9 Lives - Level 2 Arena: Combat & Tactical Cover"

ARENA_SIZE = 60.0  
WALL_HEIGHT = 9.0  


player_pos = [0.0, 1.0, -35.0] 
player_yaw = 0.0                 
player_pitch = 0.0              
BASE_PLAYER_SPEED = 0.45
player_speed = 0.45
crouching = False
eye_height = 1.6

is_jumping = False
y_velocity = 0.0
gravity = -0.016
jump_strength = 0.36
ground_y = 1.0


MAX_PLAYER_HITS = 9
player_hits_left = 9
player_invulnerable_timer = 0
cheat_mode = False               
is_game_over = False
is_level_cleared = False
is_paused = False

last_mouse_x = 0
last_mouse_y = 0
mouse_initialized = False

first_person = False
cam_dist = 6.5
cam_height = 3.8


gun_pickup_pos = [0.0, 1.2, 0.0]  
gun_picked_up = False
gun_rotation_angle = 0.0

catnip_spawned = False
catnip_picked_up = False
catnip_pickup_pos = [0.0, 1.2, 0.0]
catnip_rotation_angle = 0.0
door_glow_angle = 0.0         

active_weapon = "gun"            
fire_cooldown = 0
score = 0
zombies_killed = 0
is_target_locked = False

grenades = []
GRENADE_SPEED = 0.38             
GRENADE_GRAVITY = -0.0055         
GRENADE_MAX_LIFE = 220

death_effects = []

TOTAL_ZOMBIES_COUNT = 10
zombies_spawned = 0
zombies = []
MAX_ACTIVE_ZOMBIES = 4       
ZOMBIE_SPAWN_INTERVAL = 120  
zombie_spawn_timer = 0
zombie_base_speed = 0.020   


CRATE_RAW_DATA = [
   
    {"pos": [-26.0, 0.0, 24.0], "size": 2.6, "angle": 12.0},
    {"pos": [-23.2, 0.0, 24.5], "size": 2.4, "angle": -8.0},
    {"pos": [-24.6, 2.6, 24.2], "size": 2.2, "angle": 18.0},

   
    {"pos": [32.0, 0.0, 28.0], "size": 2.8, "angle": 5.0},
    {"pos": [35.0, 0.0, 26.5], "size": 2.4, "angle": -20.0},
    {"pos": [33.2, 2.8, 27.5], "size": 2.3, "angle": 10.0},

   
    {"pos": [-34.0, 0.0, -18.0], "size": 2.5, "angle": 25.0},
    {"pos": [-31.2, 0.0, -19.0], "size": 2.5, "angle": -15.0},
    {"pos": [-32.6, 2.5, -18.5], "size": 2.2, "angle": 5.0},

   
    {"pos": [26.0, 0.0, -28.0], "size": 2.6, "angle": -10.0},
    {"pos": [28.8, 0.0, -27.0], "size": 2.4, "angle": 15.0},
    {"pos": [27.4, 2.6, -27.5], "size": 2.1, "angle": -5.0},

   
    {"pos": [-42.0, 0.0, 2.0], "size": 2.8, "angle": 0.0},
    {"pos": [-39.0, 0.0, 1.5], "size": 2.6, "angle": 30.0},
    {"pos": [-40.5, 2.8, 1.8], "size": 2.2, "angle": 12.0},

   
    {"pos": [40.0, 0.0, -2.0], "size": 2.8, "angle": -15.0},
    {"pos": [43.0, 0.0, -1.0], "size": 2.4, "angle": 20.0},
    {"pos": [41.2, 2.8, -1.5], "size": 2.2, "angle": 5.0}
]

CRATE_BOXES = []
for c in CRATE_RAW_DATA:
    cx, cy, cz = c["pos"]
    s = c["size"]
    half = s / 2.0
    CRATE_BOXES.append({
        "min_x": cx - half,
        "max_x": cx + half,
        "min_y": cy,
        "max_y": cy + s,
        "min_z": cz - half,
        "max_z": cz + half,
        "cx": cx,
        "cz": cz,
        "size": s,
        "angle": c["angle"]
    })


COLOR_FLOOR = (0.08, 0.09, 0.13)         
COLOR_FLOOR_SIDE = (0.04, 0.04, 0.06)    
COLOR_WALL = (0.24, 0.13, 0.16)          
COLOR_WALL_SIDE = (0.16, 0.08, 0.10)    
COLOR_WALL_TRIM = (0.45, 0.15, 0.20)     
COLOR_PILLAR = (0.12, 0.12, 0.15)        
COLOR_PILLAR_GLOW = (0.9, 0.2, 0.2)     

COLOR_CRATE_WOOD = (0.46, 0.28, 0.16)   
COLOR_CRATE_TRIM = (0.28, 0.16, 0.09)    

COLOR_PEDESTAL = (0.15, 0.18, 0.25)
COLOR_PEDESTAL_RING = (0.0, 0.85, 1.0)   
COLOR_GUN_BODY = (0.20, 0.22, 0.25)      
COLOR_GUN_ACCENT = (1.0, 0.60, 0.0)      
COLOR_GRENADE = (0.18, 0.40, 0.20)       
COLOR_GRENADE_FUSE = (1.0, 0.45, 0.0)   

COLOR_CATNIP_BLUE = (0.0, 0.65, 1.0)     
COLOR_CATNIP_AURA = (0.2, 0.85, 1.0)    

c_body = (222/255, 137/255, 34/255)
c_dark = (117/255, 76/255, 18/255)
c_goggle = (229/255, 230/255, 230/255)
c_white = (1.0, 1.0, 1.0)

c_z_skin = (112/255, 168/255, 59/255)
c_z_hair = (46/255, 94/255, 33/255)
c_z_eye_nose = (18/255, 18/255, 18/255)
c_z_shirt = (0/255, 168/255, 222/255)
c_z_pants = (36/255, 68/255, 184/255)
c_z_shoes = (64/255, 64/255, 64/255)
c_z_orange = (1.0, 0.50, 0.0)


_Q = None
def Q():
    global _Q
    if _Q is None:
        _Q = gluNewQuadric()
    return _Q

def line_intersects_aabb_2d(p1x, p1z, p2x, p2z, min_x, max_x, min_z, max_z):
    dx = p2x - p1x
    dz = p2z - p1z

    t_min = 0.0
    t_max = 1.0

    if abs(dx) < 1e-7:
        if p1x < min_x or p1x > max_x:
            return False
    else:
        t1 = (min_x - p1x) / dx
        t2 = (max_x - p1x) / dx
        t_near = min(t1, t2)
        t_far = max(t1, t2)
        t_min = max(t_min, t_near)
        t_max = min(t_max, t_far)
        if t_min > t_max:
            return False

    if abs(dz) < 1e-7:
        if p1z < min_z or p1z > max_z:
            return False
    else:
        t1 = (min_z - p1z) / dz
        t2 = (max_z - p1z) / dz
        t_near = min(t1, t2)
        t_far = max(t1, t2)
        t_min = max(t_min, t_near)
        t_max = min(t_max, t_far)
        if t_min > t_max:
            return False

    return t_min <= t_max and t_max >= 0.0 and t_min <= 1.0

def is_line_of_sight_clear(p1x, p1z, p2x, p2z):
    for c in CRATE_BOXES:
        if line_intersects_aabb_2d(p1x, p1z, p2x, p2z, c['min_x'], c['max_x'], c['min_z'], c['max_z']):
            return False
    return True

def resolve_entity_crate_collision(x, z, radius, y_height=1.0):
    resolved_x, resolved_z = x, z

    for c in CRATE_BOXES:
        if y_height > c['max_y']:
            continue

        cx = max(c['min_x'], min(resolved_x, c['max_x']))
        cz = max(c['min_z'], min(resolved_z, c['max_z']))

        dist_x = resolved_x - cx
        dist_z = resolved_z - cz
        dist_sq = dist_x * dist_x + dist_z * dist_z

        if dist_sq < radius * radius:
            dist = math.sqrt(dist_sq)
            if dist < 1e-5:
                dx1 = abs(resolved_x - c['min_x'])
                dx2 = abs(resolved_x - c['max_x'])
                dz1 = abs(resolved_z - c['min_z'])
                dz2 = abs(resolved_z - c['max_z'])
                min_push = min(dx1, dx2, dz1, dz2)
                if min_push == dx1: resolved_x = c['min_x'] - radius
                elif min_push == dx2: resolved_x = c['max_x'] + radius
                elif min_push == dz1: resolved_z = c['min_z'] - radius
                else: resolved_z = c['max_z'] + radius
            else:
                overlap = radius - dist
                resolved_x += (dist_x / dist) * overlap
                resolved_z += (dist_z / dist) * overlap

    return resolved_x, resolved_z


def draw_box(sx, sy, sz, color_top=None, color_side=None, cam_rel=None):
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0

    top_col = color_top if color_top else (0.5, 0.5, 0.5)
    bot_col = (color_side[0] * 0.7, color_side[1] * 0.7, color_side[2] * 0.7) if color_side else (0.25, 0.25, 0.25)
    f_col = (color_side[0] * 0.95, color_side[1] * 0.95, color_side[2] * 0.95) if color_side else (0.4, 0.4, 0.4)
    b_col = (color_side[0] * 0.85, color_side[1] * 0.85, color_side[2] * 0.85) if color_side else (0.35, 0.35, 0.35)
    l_col = (color_side[0] * 0.80, color_side[1] * 0.80, color_side[2] * 0.80) if color_side else (0.3, 0.3, 0.3)
    r_col = (color_side[0] * 0.90, color_side[1] * 0.90, color_side[2] * 0.90) if color_side else (0.38, 0.38, 0.38)

    face_list = [
        (0.0, 1.0, 0.0, top_col, [(-hx, hy, hz), (hx, hy, hz), (hx, hy, -hz), (-hx, hy, -hz)]),
        (0.0, -1.0, 0.0, bot_col, [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz)]),
        (0.0, 0.0, 1.0, f_col, [(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]),
        (0.0, 0.0, -1.0, b_col, [(-hx, hy, -hz), (hx, hy, -hz), (hx, -hy, -hz), (-hx, -hy, -hz)]),
        (-1.0, 0.0, 0.0, l_col, [(-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz), (-hx, -hy, -hz)]),
        (1.0, 0.0, 0.0, r_col, [(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)])
    ]

    if cam_rel is not None:
        rx, ry, rz = cam_rel
        face_list.sort(key=lambda f: f[0]*rx + f[1]*ry + f[2]*rz)

    glBegin(GL_QUADS)
    for nx, ny, nz, col, quad in face_list:
        glColor3f(*col)
        for vx, vy, vz in quad:
            glVertex3f(vx, vy, vz)
    glEnd()


def draw_text(x, y, text_str, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)

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
    for dx in [-1.0, 0.0, 1.0]:
        for dy in [-1.0, 0.0, 1.0]:
            draw_text(x + dx, y + dy, text_str, color=color, font=font)

def draw_bar_2d(x, y, w, h, fill_pct, fill_color, border_color=(1.0, 1.0, 1.0)):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)

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

def draw_crosshair():
    cx, cy = WIN_W // 2, WIN_H // 2
    size = 10
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_LINES)
    if is_target_locked:
        glColor3f(1.0, 0.2, 0.2)
    else:
        glColor3f(0.0, 0.85, 1.0)
    glVertex2f(cx - size, cy); glVertex2f(cx + size, cy)
    glVertex2f(cx, cy - size); glVertex2f(cx, cy + size)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_hud():
    pw, ph = 220, 16
    px, py = 25, 25
    player_pct = player_hits_left / float(MAX_PLAYER_HITS)
    draw_bar_2d(px, py, pw, ph, player_pct, (0.1, 0.9, 0.2), border_color=(0.9, 0.9, 0.9))
    draw_text(px + pw + 12, py + 1, f"LIVES: {player_hits_left}/{MAX_PLAYER_HITS}", color=(0.1, 0.9, 0.2), font=GLUT_BITMAP_HELVETICA_18)

    if cheat_mode:
        draw_text_bold(WIN_W - 220, WIN_H - 35, 'CHEAT MODE ON', color=(1.0, 0.85, 0.2), font=GLUT_BITMAP_HELVETICA_18)

    hud_top_y = WIN_H - 30
    draw_text_bold(25, hud_top_y, "9 LIVES - LEVEL 2: ZOMBIE OUTBREAK", color=(1.0, 0.85, 0.2), font=GLUT_BITMAP_HELVETICA_18)

    if gun_picked_up or catnip_picked_up:
        w_name = "GRENADE LAUNCHER" if active_weapon == "gun" else "GLOWING BLUE CATNIP"
        switch_prompt = " (Press 'F' to Switch Weapon)" if catnip_picked_up else ""
        status_text = " [TARGET LOCKED - CLICK LMB TO FIRE!]" if is_target_locked else " [AIM & CLICK LMB TO FIRE]"
        color_status = (1.0, 0.3, 0.3) if is_target_locked else (0.0, 0.9, 1.0)
        weapon_str = f"Active Weapon: {w_name}{switch_prompt} | Status:{status_text}"
        draw_text(25, hud_top_y - 25, weapon_str, color=color_status, font=GLUT_BITMAP_HELVETICA_18)
    else:
        draw_text(25, hud_top_y - 25, "Objective: PICK UP GRENADE LAUNCHER AT CENTER PEDESTAL!", color=(1.0, 0.35, 0.35), font=GLUT_BITMAP_HELVETICA_18)

    draw_text(25, hud_top_y - 48, f"Zombies Defeated: {zombies_killed}/{TOTAL_ZOMBIES_COUNT} (Active: {len(zombies)})", color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18)

    draw_text(25, 5, "WASD: Move | Mouse: Aim | LMB: Shoot | RMB/V: POV | Space: Jump | Ctrl: Crouch | C: Cheat | F: Switch | P: Pause | R: Reset", color=(0.7, 0.7, 0.7), font=GLUT_BITMAP_HELVETICA_12)

    if catnip_spawned and not catnip_picked_up:
        draw_text_bold(WIN_W // 2 - 250, WIN_H // 2 + 50, "★ ALL ZOMBIES CLEARED! PICK UP GLOWING BLUE CATNIP AT THE CENTER! ★", color=(0.0, 0.85, 1.0))

    if is_paused:
        draw_text_bold(WIN_W // 2 - 120, WIN_H // 2 + 10, "=== GAME PAUSED ===", color=(1.0, 0.9, 0.1))
        draw_text(WIN_W // 2 - 100, WIN_H // 2 - 20, "Press 'P' to Resume Game", color=(1.0, 1.0, 1.0))

    if catnip_picked_up:
        draw_text_bold(WIN_W // 2 - 200, WIN_H // 2 + 35, "★ EXIT DOOR OPEN ON THE NORTH WALL! ★", color=(0.2, 1.0, 0.9), font=GLUT_BITMAP_HELVETICA_18)
        draw_text(WIN_W // 2 - 160, WIN_H // 2 + 10, "Walk into the glowing portal on the north wall!", color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18)

    if is_game_over:
        draw_text_bold(WIN_W // 2 - 130, WIN_H // 2 + 20, "=== MISSION FAILED! ===", color=(1.0, 0.1, 0.1))
        draw_text(WIN_W // 2 - 90, WIN_H // 2 - 15, "Press 'R' to Restart Arena", color=(1.0, 1.0, 1.0))


def draw_single_crate(x, y, z, size=2.5, angle_y=0.0, cam_x=0.0, cam_y=0.0, cam_z=0.0):
    glPushMatrix()
    cy = y + size / 2.0
    glTranslatef(x, cy, z)
    if angle_y != 0.0:
        glRotatef(angle_y, 0, 1, 0)
        rad_a = math.radians(-angle_y)
        dx = cam_x - x
        dz = cam_z - z
        rx = dx * math.cos(rad_a) - dz * math.sin(rad_a)
        rz = dx * math.sin(rad_a) + dz * math.cos(rad_a)
        ry = cam_y - cy
    else:
        rx = cam_x - x
        ry = cam_y - cy
        rz = cam_z - z

    draw_box(size, size, size, color_top=COLOR_CRATE_WOOD, color_side=COLOR_CRATE_WOOD, cam_rel=(rx, ry, rz))

    trim_h = size * 0.14
    draw_box(size * 1.01, trim_h, size * 1.01, color_top=COLOR_CRATE_TRIM, color_side=COLOR_CRATE_TRIM, cam_rel=(rx, ry, rz))

    glPopMatrix()


def draw_level_exit_door(cam_x=0.0, cam_y=0.0, cam_z=0.0):
   
    if not catnip_picked_up:
        return

   
    door_x = 0.0
    door_z = ARENA_SIZE - 0.85   
    door_bottom_y = 0.0
    door_w = 3.5   
    door_h = 5.0   

   
    pulse = 0.55 + 0.45 * math.sin(math.radians(door_glow_angle))
    r = 0.1 * pulse
    g = 0.65 + 0.35 * pulse
    b = 1.0

    
    frame_thickness = 0.45
    glColor3f(0.06, 0.06, 0.10)
    glBegin(GL_QUADS)
    glVertex3f(door_x - door_w - frame_thickness, door_bottom_y,          door_z)
    glVertex3f(door_x - door_w,                   door_bottom_y,          door_z)
    glVertex3f(door_x - door_w,                   door_bottom_y + door_h, door_z)
    glVertex3f(door_x - door_w - frame_thickness, door_bottom_y + door_h, door_z)
    glVertex3f(door_x + door_w,                   door_bottom_y,          door_z)
    glVertex3f(door_x + door_w + frame_thickness, door_bottom_y,          door_z)
    glVertex3f(door_x + door_w + frame_thickness, door_bottom_y + door_h, door_z)
    glVertex3f(door_x + door_w,                   door_bottom_y + door_h, door_z)
    glVertex3f(door_x - door_w - frame_thickness, door_bottom_y + door_h,                   door_z)
    glVertex3f(door_x + door_w + frame_thickness, door_bottom_y + door_h,                   door_z)
    glVertex3f(door_x + door_w + frame_thickness, door_bottom_y + door_h + frame_thickness, door_z)
    glVertex3f(door_x - door_w - frame_thickness, door_bottom_y + door_h + frame_thickness, door_z)
    glEnd()

    panel_pulse = 0.35 + 0.20 * pulse
    glColor3f(r * 0.5, g * panel_pulse, b * panel_pulse)
    glBegin(GL_QUADS)
    glVertex3f(door_x - door_w, door_bottom_y,          door_z)
    glVertex3f(door_x + door_w, door_bottom_y,          door_z)
    glVertex3f(door_x + door_w, door_bottom_y + door_h, door_z)
    glVertex3f(door_x - door_w, door_bottom_y + door_h, door_z)
    glEnd()

    glColor3f(r, g * pulse, b)
    glBegin(GL_LINES)
    glVertex3f(door_x - door_w, door_bottom_y,          door_z)
    glVertex3f(door_x + door_w, door_bottom_y,          door_z)
    glVertex3f(door_x + door_w, door_bottom_y,          door_z)
    glVertex3f(door_x + door_w, door_bottom_y + door_h, door_z)
    glVertex3f(door_x + door_w, door_bottom_y + door_h, door_z)
    glVertex3f(door_x - door_w, door_bottom_y + door_h, door_z)
    glVertex3f(door_x - door_w, door_bottom_y + door_h, door_z)
    glVertex3f(door_x - door_w, door_bottom_y,          door_z)
    glVertex3f(door_x - door_w, door_bottom_y,          door_z)
    glVertex3f(door_x + door_w, door_bottom_y + door_h, door_z)
    glVertex3f(door_x + door_w, door_bottom_y,          door_z)
    glVertex3f(door_x - door_w, door_bottom_y + door_h, door_z)
    glEnd()

  
    glColor3f(r * 0.6, g, b * 0.8)
    glBegin(GL_LINES)
    for bx in [-door_w, 0.0, door_w]:
        glVertex3f(door_x + bx, door_bottom_y,      door_z - 0.05)
        glVertex3f(door_x + bx, door_bottom_y + 6.5, door_z - 0.05)
    glEnd()

    glColor3f(r, g * pulse, b)
    glPointSize(5.0)
    glBegin(GL_POINTS)
    orbit_r = door_w * 0.75
    orbit_y = door_bottom_y + door_h * 0.5
    for i in range(10):
        ang = math.radians(door_glow_angle * 2.5 + i * 36)
        glVertex3f(door_x + orbit_r * math.cos(ang), orbit_y, door_z + orbit_r * 0.12 * math.sin(ang))
    glEnd()

    glPointSize(1.0)

def draw_arena_floor():
    glPushMatrix()
    glTranslatef(0.0, -0.1, 0.0)
    draw_box(ARENA_SIZE * 2.0, 0.2, ARENA_SIZE * 2.0, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

def draw_north_wall(cam_x=0.0, cam_y=0.0, cam_z=0.0):
    half_size = ARENA_SIZE
    wall_thickness = 1.6
    wall_y = WALL_HEIGHT / 2.0
    glPushMatrix()
    glTranslatef(0.0, wall_y, half_size + wall_thickness / 2.0)
    draw_box(half_size * 2.0 + wall_thickness * 2.0, WALL_HEIGHT, wall_thickness, color_top=COLOR_WALL, color_side=COLOR_WALL_SIDE, cam_rel=(cam_x, cam_y - wall_y, cam_z - (half_size + wall_thickness / 2.0)))
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, WALL_HEIGHT - 0.4, half_size)
    draw_box(half_size * 2.0, 0.6, 0.4, color_top=COLOR_WALL_TRIM, color_side=COLOR_WALL_TRIM)
    glPopMatrix()

def draw_south_wall(cam_x=0.0, cam_y=0.0, cam_z=0.0):
    half_size = ARENA_SIZE
    wall_thickness = 1.6
    wall_y = WALL_HEIGHT / 2.0
    glPushMatrix()
    glTranslatef(0.0, wall_y, -half_size - wall_thickness / 2.0)
    draw_box(half_size * 2.0 + wall_thickness * 2.0, WALL_HEIGHT, wall_thickness, color_top=COLOR_WALL, color_side=COLOR_WALL_SIDE, cam_rel=(cam_x, cam_y - wall_y, cam_z - (-half_size - wall_thickness / 2.0)))
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, WALL_HEIGHT - 0.4, -half_size)
    draw_box(half_size * 2.0, 0.6, 0.4, color_top=COLOR_WALL_TRIM, color_side=COLOR_WALL_TRIM)
    glPopMatrix()

def draw_west_wall(cam_x=0.0, cam_y=0.0, cam_z=0.0):
    half_size = ARENA_SIZE
    wall_thickness = 1.6
    wall_y = WALL_HEIGHT / 2.0
    glPushMatrix()
    glTranslatef(-half_size - wall_thickness / 2.0, wall_y, 0.0)
    draw_box(wall_thickness, WALL_HEIGHT, half_size * 2.0, color_top=COLOR_WALL, color_side=COLOR_WALL_SIDE, cam_rel=(cam_x - (-half_size - wall_thickness / 2.0), cam_y - wall_y, cam_z))
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-half_size, WALL_HEIGHT - 0.4, 0.0)
    draw_box(0.4, 0.6, half_size * 2.0, color_top=COLOR_WALL_TRIM, color_side=COLOR_WALL_TRIM)
    glPopMatrix()

def draw_east_wall(cam_x=0.0, cam_y=0.0, cam_z=0.0):
    half_size = ARENA_SIZE
    wall_thickness = 1.6
    wall_y = WALL_HEIGHT / 2.0
    glPushMatrix()
    glTranslatef(half_size + wall_thickness / 2.0, wall_y, 0.0)
    draw_box(wall_thickness, WALL_HEIGHT, half_size * 2.0, color_top=COLOR_WALL, color_side=COLOR_WALL_SIDE, cam_rel=(cam_x - (half_size + wall_thickness / 2.0), cam_y - wall_y, cam_z))
    glPopMatrix()
    glPushMatrix()
    glTranslatef(half_size, WALL_HEIGHT - 0.4, 0.0)
    draw_box(0.4, 0.6, half_size * 2.0, color_top=COLOR_WALL_TRIM, color_side=COLOR_WALL_TRIM)
    glPopMatrix()

def draw_single_pillar(px, pz):
    glPushMatrix()
    glTranslatef(px, WALL_HEIGHT / 2.0, pz)
    draw_box(3.2, WALL_HEIGHT + 1.0, 3.2, color_top=COLOR_PILLAR, color_side=(0.10, 0.10, 0.12))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(px, WALL_HEIGHT + 0.8, pz)
    draw_box(2.0, 0.6, 2.0, color_top=COLOR_PILLAR_GLOW, color_side=(0.7, 0.1, 0.1))
    glPopMatrix()


def draw_3d_gun_model():
    glPushMatrix()
    glColor3f(*COLOR_GUN_BODY)
    glPushMatrix()
    glScalef(0.16, 0.24, 0.65)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.15, 0.15, 0.18)
    glPushMatrix()
    glTranslatef(0.0, -0.22, -0.15)
    glRotatef(20, 1, 0, 0)
    glScalef(0.11, 0.30, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(*COLOR_GUN_ACCENT)
    glPushMatrix()
    glTranslatef(0.0, 0.04, 0.28)
    gluCylinder(Q(), 0.09, 0.09, 0.48, 14, 4)
    glPopMatrix()

    glColor3f(1.0, 0.3, 0.0)
    glPushMatrix()
    glTranslatef(0.0, 0.04, 0.76)
    glutSolidCube(0.18)
    glPopMatrix()

    glPopMatrix()

def draw_gun_pickup():
    if gun_picked_up:
        return

    gx, gy, gz = gun_pickup_pos

    glPushMatrix()
    glTranslatef(gx, 0.2, gz)
    draw_box(2.2, 0.4, 2.2, color_top=COLOR_PEDESTAL, color_side=(0.10, 0.12, 0.16))
    glPopMatrix()

    glColor3f(*COLOR_PEDESTAL_RING)
    glBegin(GL_LINES)
    for i in range(24):
        a1 = 2.0 * math.pi * i / 24
        a2 = 2.0 * math.pi * (i + 1) / 24
        r = 1.8
        glVertex3f(gx + r * math.cos(a1), 0.42, gz + r * math.sin(a1))
        glVertex3f(gx + r * math.cos(a2), 0.42, gz + r * math.sin(a2))
    glEnd()

    glColor3f(0.0, 0.75, 1.0)
    glBegin(GL_LINES)
    for i in range(4):
        ang = math.pi / 4.0 + i * math.pi / 2.0
        px = gx + 1.2 * math.cos(ang)
        pz = gz + 1.2 * math.sin(ang)
        glVertex3f(px, 0.4, pz)
        glVertex3f(px, 2.5, pz)
    glEnd()

    glPushMatrix()
    bob_y = gy + 0.3 * math.sin(gun_rotation_angle * 0.05)
    glTranslatef(gx, bob_y, gz)
    glRotatef(gun_rotation_angle, 0, 1, 0)
    glScalef(2.0, 2.0, 2.0)
    draw_3d_gun_model()
    glPopMatrix()


def draw_3d_catnip_model():
    glPushMatrix()
    glColor3f(*COLOR_CATNIP_BLUE)
    glPushMatrix()
    glScalef(0.35, 0.40, 0.35)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(*COLOR_CATNIP_AURA)
    for rot_leaf in [0, 45, 90, 135]:
        glPushMatrix()
        glTranslatef(0.0, 0.22, 0.0)
        glRotatef(rot_leaf, 0, 1, 0)
        glRotatef(25, 1, 0, 0)
        glScalef(0.12, 0.25, 0.08)
        glutSolidCube(1.0)
        glPopMatrix()

    glColor3f(0.7, 0.95, 1.0)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    glutSolidCube(0.16)
    glPopMatrix()

    glPopMatrix()

def draw_catnip_pickup():
    if not catnip_spawned or catnip_picked_up:
        return

    cx, cy, cz = catnip_pickup_pos

    glColor3f(*COLOR_CATNIP_BLUE)
    glBegin(GL_LINES)
    for i in range(24):
        a1 = 2.0 * math.pi * i / 24
        a2 = 2.0 * math.pi * (i + 1) / 24
        r = 1.6
        glVertex3f(cx + r * math.cos(a1), 0.12, cz + r * math.sin(a1))
        glVertex3f(cx + r * math.cos(a2), 0.12, cz + r * math.sin(a2))
    glEnd()

    glColor3f(*COLOR_CATNIP_AURA)
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for i in range(8):
        ang = i * (math.pi / 4.0) + (catnip_rotation_angle * 0.04)
        r = 0.8 + 0.3 * math.sin(catnip_rotation_angle * 0.08 + i)
        py = 0.3 + (i * 0.2)
        glVertex3f(cx + r * math.cos(ang), py, cz + r * math.sin(ang))
    glEnd()

    glPushMatrix()
    bob_y = cy + 0.3 * math.sin(catnip_rotation_angle * 0.06)
    glTranslatef(cx, bob_y, cz)
    glRotatef(catnip_rotation_angle, 0, 1, 0)
    glScalef(2.2, 2.2, 2.2)
    draw_3d_catnip_model()
    glPopMatrix()


def draw_character(cam_x=0.0, cam_z=0.0):
    if first_person:
        return

    glPushMatrix()
    curr_y = player_pos[1]
    glTranslatef(player_pos[0], curr_y, player_pos[2])
    glRotatef(player_yaw, 0, 1, 0)
    glRotatef(-90.0, 1, 0, 0)
    glRotatef(180.0, 0, 0, 1)

    if player_invulnerable_timer > 0 and (player_invulnerable_timer // 4) % 2 == 1:
        glColor3f(1.0, 0.2, 0.2)
    else:
        glColor3f(*c_body)

    scale_factor = 0.008
    if crouching:
        glScalef(scale_factor, scale_factor * 0.5, scale_factor)
    else:
        glScalef(scale_factor, scale_factor, scale_factor)

    rad_yaw = math.radians(player_yaw)
    fwd_x = math.sin(rad_yaw)
    fwd_z = math.cos(rad_yaw)
    to_cam_x = cam_x - player_pos[0]
    to_cam_z = cam_z - player_pos[2]
    is_front = (fwd_x * to_cam_x + fwd_z * to_cam_z) > 0.0

    def draw_face_details():
        for eye_x in [-16, 16]:
            glPushMatrix()
            glColor3f(*c_goggle)
            glTranslatef(eye_x, 21, 160)
            glScalef(0.28, 0.08, 0.35)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_white)
            glTranslatef(eye_x, 25, 160)
            glScalef(0.18, 0.08, 0.22)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_dark)
            glTranslatef(eye_x, 29, 160)
            glScalef(0.08, 0.05, 0.1)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_dark)
            glTranslatef(eye_x, 22, 185)
            glScalef(0.25, 0.06, 0.06)
            glutSolidCube(100)
            glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(0, 22, 138)
        glScalef(0.06, 0.06, 0.16)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(-2, 22, 122)
        glScalef(0.38, 0.06, 0.06)
        glutSolidCube(100)
        glPopMatrix()

    def draw_held_weapon():
        if gun_picked_up and active_weapon == "gun":
            glPushMatrix()
            glTranslatef(38.5, 20, 70)
            glRotatef(90, 1, 0, 0)
            glScalef(120.0, 120.0, 120.0)
            draw_3d_gun_model()
            glPopMatrix()
        elif catnip_picked_up and active_weapon == "catnip":
            glPushMatrix()
            glTranslatef(38.5, 20, 70)
            glScalef(140.0, 140.0, 140.0)
            draw_3d_catnip_model()
            glPopMatrix()

    if not is_front:
        draw_face_details()
        draw_held_weapon()

    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 120)
    glScalef(0.65, 0.4, 1.8)
    glutSolidCube(100)
    glPopMatrix()

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

    for leg_x in [-14, 14]:
        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(leg_x, 0, 18)
        glScalef(0.12, 0.15, 0.6)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(leg_x, 10, -8)
        glScalef(0.2, 0.35, 0.12)
        glutSolidCube(100)
        glPopMatrix()

    if is_front:
        draw_face_details()
        draw_held_weapon()

    glPopMatrix()


def draw_zombie_mesh(is_orange=False, is_front=True):
    glPushMatrix()

    if is_orange:
        c_skin = c_z_orange
        c_hair = (0.85, 0.35, 0.0)
        c_eye_nose = (0.1, 0.1, 0.1)
        c_shirt = (1.0, 0.60, 0.1)
        c_pants = (0.90, 0.40, 0.0)
        c_shoes = (0.50, 0.20, 0.0)
    else:
        c_skin = c_z_skin
        c_hair = c_z_hair
        c_eye_nose = c_z_eye_nose
        c_shirt = c_z_shirt
        c_pants = c_z_pants
        c_shoes = c_z_shoes

    def draw_zombie_face():
        glPushMatrix()
        glColor3f(*c_hair)
        glTranslatef(0, 0, 162)
        glScalef(0.64, 0.64, 0.2)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_eye_nose)
        glTranslatef(-14, 31, 142)
        glScalef(0.18, 0.04, 0.08)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_eye_nose)
        glTranslatef(14, 31, 142)
        glScalef(0.18, 0.04, 0.08)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_hair)
        glTranslatef(0, 31, 134)
        glScalef(0.14, 0.04, 0.08)
        glutSolidCube(100)
        glPopMatrix()

    if not is_front:
        draw_zombie_face()

    glPushMatrix()
    glColor3f(*c_skin)
    glTranslatef(0, 0, 140)
    glScalef(0.6, 0.6, 0.6)
    glutSolidCube(100)
    glPopMatrix()

    if is_front:
        draw_zombie_face()

    glPushMatrix()
    glColor3f(*c_shirt)
    glTranslatef(0, 0, 80)
    glScalef(0.6, 0.3, 0.6)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_skin)
    glTranslatef(-39.8, 28, 92)
    glScalef(0.2, 0.45, 0.24)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_shirt)
    glTranslatef(-39.8, 5, 92)
    glScalef(0.21, 0.4, 0.25)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_skin)
    glTranslatef(39.8, 28, 92)
    glScalef(0.2, 0.45, 0.24)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_shirt)
    glTranslatef(39.8, 5, 92)
    glScalef(0.21, 0.4, 0.25)
    glutSolidCube(100)
    glPopMatrix()

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

class Zombie:
    def __init__(self, x, z):
        self.pos = [x, 0.0, z]
        self.is_hit_orange = False
        self.speed = zombie_base_speed + random.uniform(-0.003, 0.003)
        self.yaw = 0.0
        self.walk_anim = random.uniform(0, 10)

    def update(self):
        self.walk_anim += 0.04
        dx = player_pos[0] - self.pos[0]
        dz = player_pos[2] - self.pos[2]
        dist = math.sqrt(dx * dx + dz * dz)

        if dist > 1.2:
            step_x = (dx / dist) * self.speed
            step_z = (dz / dist) * self.speed

            next_x = self.pos[0] + step_x
            next_z = self.pos[2] + step_z

            res_x, res_z = resolve_entity_crate_collision(next_x, next_z, radius=1.6, y_height=1.0)

            self.pos[0] = res_x
            self.pos[2] = res_z

            move_dx = res_x - self.pos[0]
            move_dz = res_z - self.pos[2]
            if move_dx * move_dx + move_dz * move_dz > 1e-6:
                self.yaw = math.degrees(math.atan2(move_dx, move_dz))
            else:
                self.yaw = math.degrees(math.atan2(dx, dz))

        limit = ARENA_SIZE - 2.5
        self.pos[0] = max(-limit, min(limit, self.pos[0]))
        self.pos[2] = max(-limit, min(limit, self.pos[2]))

    def draw(self, cam_x=0.0, cam_z=0.0):
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        glRotatef(180, 0, 0, 1)

        scale_factor = 0.016
        glScalef(scale_factor, scale_factor, scale_factor)

        rad_z = math.radians(self.yaw)
        fwd_x = math.sin(rad_z)
        fwd_z = math.cos(rad_z)
        to_cam_x = cam_x - self.pos[0]
        to_cam_z = cam_z - self.pos[2]
        is_front = (fwd_x * to_cam_x + fwd_z * to_cam_z) > 0.0

        draw_zombie_mesh(is_orange=self.is_hit_orange, is_front=is_front)
        glPopMatrix()

def spawn_zombie():
    global zombies_spawned

    if zombies_spawned >= TOTAL_ZOMBIES_COUNT:
        return
    if len(zombies) >= MAX_ACTIVE_ZOMBIES:
        return

    side = random.randint(0, 3)
    spawn_offset = ARENA_SIZE - 4.0
    if side == 0:
        x = random.uniform(-spawn_offset, spawn_offset)
        z = spawn_offset
    elif side == 1:
        x = random.uniform(-spawn_offset, spawn_offset)
        z = -spawn_offset
    elif side == 2:
        x = -spawn_offset
        z = random.uniform(-spawn_offset, spawn_offset)
    else:
        x = spawn_offset
        z = random.uniform(-spawn_offset, spawn_offset)

    zombies.append(Zombie(x, z))
    zombies_spawned += 1


def check_target_lock():
    global is_target_locked

    if (not gun_picked_up and not catnip_picked_up) or is_paused or is_game_over or is_level_cleared:
        is_target_locked = False
        return

    rad_yaw = math.radians(player_yaw)
    rad_pitch = math.radians(player_pitch)

    dir_x = math.sin(rad_yaw) * math.cos(rad_pitch)
    dir_y = math.sin(rad_pitch)
    dir_z = math.cos(rad_yaw) * math.cos(rad_pitch)

    eye_y = player_pos[1] + (0.8 if crouching else eye_height)

    locked = False
    for z in zombies:
        if not is_line_of_sight_clear(player_pos[0], player_pos[2], z.pos[0], z.pos[2]):
            continue

        vx = z.pos[0] - player_pos[0]
        vy = (z.pos[1] + 2.4) - eye_y
        vz = z.pos[2] - player_pos[2]
        dist = math.sqrt(vx * vx + vy * vy + vz * vz)

        if dist > 0.5 and dist < 80.0:
            ux, uy, uz = vx / dist, vy / dist, vz / dist
            dot = dir_x * ux + dir_y * uy + dir_z * uz

            if dot > 0.93:
                locked = True
                break

    is_target_locked = locked

def launch_projectile():
    global fire_cooldown

    if active_weapon == "gun" and not gun_picked_up:
        return
    if active_weapon == "catnip" and not catnip_picked_up:
        return
    if fire_cooldown > 0 or is_paused or is_game_over or is_level_cleared:
        return

    fire_cooldown = 18

    rad_yaw = math.radians(player_yaw)
    rad_pitch = math.radians(player_pitch)

    vx = math.sin(rad_yaw) * math.cos(rad_pitch) * GRENADE_SPEED
    vy = math.sin(rad_pitch) * GRENADE_SPEED + 0.08
    vz = math.cos(rad_yaw) * math.cos(rad_pitch) * GRENADE_SPEED

    start_x = player_pos[0] + math.sin(rad_yaw) * 0.8
    start_y = player_pos[1] + (0.8 if crouching else 1.3)
    start_z = player_pos[2] + math.cos(rad_yaw) * 0.8

    grenades.append({
        'pos': [start_x, start_y, start_z],
        'vel': [vx, vy, vz],
        'rot': 0.0,
        'is_catnip': (active_weapon == "catnip"),
        'life': GRENADE_MAX_LIFE
    })

def update_grenades_and_explosions():
    global score, zombies_killed, is_level_cleared, catnip_spawned

    for g in list(grenades):
        g['pos'][0] += g['vel'][0]
        g['pos'][1] += g['vel'][1]
        g['pos'][2] += g['vel'][2]

        g['vel'][1] += GRENADE_GRAVITY
        g['rot'] = (g['rot'] + 8.0) % 360.0
        g['life'] -= 1

        gx, gy, gz = g['pos']

        hit_ground = (gy <= 0.2)
        out_of_bounds = (abs(gx) >= ARENA_SIZE or abs(gz) >= ARENA_SIZE)

        hit_crate = False
        for c in CRATE_BOXES:
            if c['min_x'] <= gx <= c['max_x'] and c['min_y'] <= gy <= c['max_y'] and c['min_z'] <= gz <= c['max_z']:
                hit_crate = True
                break

        hit_zombie_target = None
        for z in zombies:
            dist_sq = (gx - z.pos[0])**2 + (gy - (z.pos[1] + 2.0))**2 + (gz - z.pos[2])**2
            if dist_sq < 6.0:
                hit_zombie_target = z
                break

        if hit_zombie_target or hit_crate or hit_ground or out_of_bounds or g['life'] <= 0:
            if g in grenades:
                grenades.remove(g)

            for z in list(zombies):
                dist_blast = math.sqrt((gx - z.pos[0])**2 + (gy - z.pos[1])**2 + (gz - z.pos[2])**2)
                if dist_blast <= 4.0 or z == hit_zombie_target:
                    if z == hit_zombie_target or is_line_of_sight_clear(gx, gz, z.pos[0], z.pos[2]):
                        z.is_hit_orange = True
                        death_effects.append({
                            'pos': [z.pos[0], 0.1, z.pos[2]],
                            'timer': 60,
                            'max_timer': 60
                        })

                        if z in zombies:
                            zombies.remove(z)
                            score += 100
                            zombies_killed += 1

                            if zombies_killed >= TOTAL_ZOMBIES_COUNT:
                                is_level_cleared = True
                                catnip_spawned = True
                                print(">> ALL 10 ZOMBIES DEFEATED! A Glowing Blue Catnip has spawned on the ground!")

    for d in list(death_effects):
        d['timer'] -= 1
        if d['timer'] <= 0:
            death_effects.remove(d)

def draw_single_grenade(g):
    gx, gy, gz = g['pos']
    glPushMatrix()
    glTranslatef(gx, gy, gz)
    glRotatef(g['rot'], 1, 1, 0)

    if g.get('is_catnip', False):
        draw_box(0.35, 0.35, 0.35, color_top=COLOR_CATNIP_BLUE, color_side=COLOR_CATNIP_AURA)
    else:
        draw_box(0.35, 0.35, 0.35, color_top=COLOR_GRENADE, color_side=(0.12, 0.28, 0.14))
        glTranslatef(0.0, 0.22, 0.0)
        draw_box(0.14, 0.14, 0.14, color_top=COLOR_GRENADE_FUSE, color_side=COLOR_GRENADE_FUSE)

    glPopMatrix()

def draw_single_death_effect(d):
    dx, dy, dz = d['pos']
    progress = 1.0 - (d['timer'] / float(d['max_timer']))
    current_radius = 1.0 + progress * 3.5
    alpha_intensity = max(0.2, 1.0 - progress)

    glColor3f(1.0 * alpha_intensity, 0.1 * alpha_intensity, 0.1 * alpha_intensity)
    glBegin(GL_LINES)
    segs = 28
    for i in range(segs):
        t1 = 2.0 * math.pi * i / segs
        t2 = 2.0 * math.pi * (i + 1) / segs
        glVertex3f(dx + current_radius * math.cos(t1), dy + 0.02, dz + current_radius * math.sin(t1))
        glVertex3f(dx + current_radius * math.cos(t2), dy + 0.02, dz + current_radius * math.sin(t2))
    glEnd()

    glPointSize(6.0)
    glBegin(GL_POINTS)
    for h_step in range(6):
        py = dy + h_step * 0.35
        pr = current_radius * (1.0 - h_step * 0.15)
        for j in range(4):
            ang = j * (math.pi / 2.0) + progress * 2.0
            glVertex3f(dx + pr * 0.4 * math.cos(ang), py, dz + pr * 0.4 * math.sin(ang))
    glEnd()

    glPushMatrix()
    glTranslatef(dx, dy + 0.6, dz)
    core_scale = max(0.1, 0.6 * (1.0 - progress))
    draw_box(core_scale, core_scale * 1.5, core_scale, color_top=(1.0, 0.2, 0.2), color_side=(0.8, 0.1, 0.1))
    glPopMatrix()


def setup_camera():
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55.0, WIN_W / float(WIN_H), 0.1, 350.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    rad_yaw = math.radians(player_yaw)
    rad_pitch = math.radians(player_pitch)
    curr_eye_h = 0.8 if crouching else eye_height

    if first_person:
        eye_x = player_pos[0]
        eye_y = player_pos[1] + curr_eye_h
        eye_z = player_pos[2]
        center_x = eye_x + math.sin(rad_yaw) * math.cos(rad_pitch) * 100.0
        center_y = eye_y + math.sin(rad_pitch) * 100.0
        center_z = eye_z + math.cos(rad_yaw) * math.cos(rad_pitch) * 100.0
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0.0, 1.0, 0.0)
        return eye_x, eye_y, eye_z
    else:
        eye_x = player_pos[0] - math.sin(rad_yaw) * cam_dist
        eye_y = player_pos[1] + cam_height
        eye_z = player_pos[2] - math.cos(rad_yaw) * cam_dist
        center_x = eye_x + math.sin(rad_yaw) * math.cos(rad_pitch) * 100.0
        center_y = eye_y + math.sin(rad_pitch) * 100.0
        center_z = eye_z + math.cos(rad_yaw) * math.cos(rad_pitch) * 100.0
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0.0, 1.0, 0.0)
        return eye_x, eye_y, eye_z

_user32 = ctypes.windll.user32

def update_window_dimensions():
    global WIN_W, WIN_H
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
                    WIN_W = w
                    WIN_H = h
    except:
        pass

def display():
    global WIN_W, WIN_H
    update_window_dimensions()

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    cam_x, cam_y, cam_z = setup_camera()

    draw_arena_floor()

    render_list = []

    wall_y = WALL_HEIGHT / 2.0
    half_size = ARENA_SIZE
    wall_thickness = 1.6

    # Perimeter walls
    render_list.append((0.0, wall_y, half_size + wall_thickness / 2.0, lambda: draw_north_wall(cam_x, cam_y, cam_z)))
    render_list.append((0.0, wall_y, -half_size - wall_thickness / 2.0, lambda: draw_south_wall(cam_x, cam_y, cam_z)))
    render_list.append((-half_size - wall_thickness / 2.0, wall_y, 0.0, lambda: draw_west_wall(cam_x, cam_y, cam_z)))
    render_list.append((half_size + wall_thickness / 2.0, wall_y, 0.0, lambda: draw_east_wall(cam_x, cam_y, cam_z)))

    for px, pz in [(-half_size, -half_size), (half_size, -half_size), (-half_size, half_size), (half_size, half_size)]:
        def _draw_pil(px=px, pz=pz):
            draw_single_pillar(px, pz)
        render_list.append((px, wall_y, pz, _draw_pil))

    if catnip_picked_up:
        render_list.append((0.0, 2.5, ARENA_SIZE - 0.85, lambda: draw_level_exit_door(cam_x, cam_y, cam_z)))

    for c in CRATE_BOXES:
        def _draw_cr(c=c):
            draw_single_crate(c["cx"], c["min_y"], c["cz"], c["size"], c["angle"], cam_x, cam_y, cam_z)
        render_list.append((c["cx"], c["min_y"] + c["size"] * 0.5, c["cz"], _draw_cr))

    if not gun_picked_up:
        render_list.append((gun_pickup_pos[0], gun_pickup_pos[1], gun_pickup_pos[2], draw_gun_pickup))

    if catnip_spawned and not catnip_picked_up:
        render_list.append((catnip_pickup_pos[0], catnip_pickup_pos[1], catnip_pickup_pos[2], draw_catnip_pickup))
    for d in death_effects:
        def _draw_de(d=d):
            draw_single_death_effect(d)
        render_list.append((d['pos'][0], d['pos'][1], d['pos'][2], _draw_de))

    for z in zombies:
        def _draw_z(z=z):
            z.draw(cam_x, cam_z)
        render_list.append((z.pos[0], z.pos[1] + 2.0, z.pos[2], _draw_z))

    if not first_person:
        render_list.append((player_pos[0], player_pos[1] + 1.0, player_pos[2], lambda: draw_character(cam_x, cam_z)))

    for g in grenades:
        def _draw_g(g=g):
            draw_single_grenade(g)
        render_list.append((g['pos'][0], g['pos'][1], g['pos'][2], _draw_g))

    def _dist_sq(entity):
        ex, ey, ez, fn = entity
        return (ex - cam_x)**2 + (ey - cam_y)**2 + (ez - cam_z)**2

    render_list.sort(key=_dist_sq, reverse=True)

    for ex, ey, ez, fn in render_list:
        fn()

    draw_crosshair()
    draw_hud()

    glutSwapBuffers()


def idle():
    global player_pos, is_jumping, y_velocity, gun_rotation_angle, catnip_rotation_angle, door_glow_angle
    global gun_picked_up, catnip_picked_up, fire_cooldown, zombie_spawn_timer
    global player_hits_left, player_invulnerable_timer, is_game_over
    global player_yaw, player_pitch, last_mouse_x, last_mouse_y, mouse_initialized

    if is_paused or is_game_over:
        glutPostRedisplay()
        return

    try:
        class _POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        _pt = _POINT()
        if ctypes.windll.user32.GetCursorPos(ctypes.byref(_pt)):
            if mouse_initialized:
                dx = _pt.x - last_mouse_x
                dy = _pt.y - last_mouse_y
                if dx != 0 or dy != 0:
                    mouse_sensitivity = 0.28
                    player_yaw = (player_yaw + dx * mouse_sensitivity) % 360.0
                    player_pitch = max(-65.0, min(65.0, player_pitch - dy * mouse_sensitivity))
            else:
                mouse_initialized = True
            last_mouse_x = _pt.x
            last_mouse_y = _pt.y
    except:
        pass

    gun_rotation_angle = (gun_rotation_angle + 2.5) % 360.0
    catnip_rotation_angle = (catnip_rotation_angle + 3.0) % 360.0
    door_glow_angle = (door_glow_angle + 1.8) % 360.0

    if not gun_picked_up:
        dist_to_gun = math.sqrt((player_pos[0] - gun_pickup_pos[0])**2 + (player_pos[2] - gun_pickup_pos[2])**2)
        if dist_to_gun < 2.2:
            gun_picked_up = True
            print(">> Grenade Launcher Acquired! Click LMB to Launch Slow Projectile Nades!")

    if catnip_spawned and not catnip_picked_up:
        dist_to_catnip = math.sqrt((player_pos[0] - catnip_pickup_pos[0])**2 + (player_pos[2] - catnip_pickup_pos[2])**2)
        if dist_to_catnip < 2.2:
            catnip_picked_up = True
            print(">> Glowing Blue Catnip Acquired! Press 'F' to switch between Gun & Catnip!")

    if is_jumping:
        player_pos[1] += y_velocity
        y_velocity += gravity
        if player_pos[1] <= ground_y:
            player_pos[1] = ground_y
            is_jumping = False
            y_velocity = 0.0

    if fire_cooldown > 0:
        fire_cooldown -= 1

    check_target_lock()

    update_grenades_and_explosions()

    if zombies_spawned < TOTAL_ZOMBIES_COUNT:
        zombie_spawn_timer += 1
        if zombie_spawn_timer >= ZOMBIE_SPAWN_INTERVAL:
            zombie_spawn_timer = 0
            spawn_zombie()

    if player_invulnerable_timer > 0:
        player_invulnerable_timer -= 1

    for z in zombies:
        z.update()
        dist_to_player = math.sqrt((z.pos[0] - player_pos[0])**2 + (z.pos[2] - player_pos[2])**2)
        if dist_to_player < 2.2 and player_invulnerable_timer <= 0:
            if not cheat_mode:
                player_hits_left -= 1
                player_invulnerable_timer = 50
                print(f">> Player hit by Zombie! Lives remaining: {player_hits_left}/{MAX_PLAYER_HITS}")
                if player_hits_left <= 0:
                    is_game_over = True
                    print(">> All 9 Lives depleted! Press R to Restart.")
            else:
                player_invulnerable_timer = 30

    glutPostRedisplay()


def mouse_listener(button, state, x, y):
    global first_person

    if is_paused or is_game_over or is_level_cleared:
        return

    try:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            launch_projectile()
        elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            first_person = not first_person
            glutPostRedisplay()
    except Exception as e:
        print(f"Mouse event error: {e}")

def keyboard_listener(key, x, y):
    global player_pos, is_jumping, y_velocity
    global first_person, is_paused, is_game_over, cheat_mode, active_weapon
    global player_yaw, player_pitch

    try:
        ch = key.decode('utf-8').lower()
    except:
        ch = str(key).lower()

    rad = math.radians(player_yaw)

    if not is_paused and not is_game_over:
        next_x = player_pos[0]
        next_z = player_pos[2]

        if ch == 'w':
            next_x += math.sin(rad) * player_speed
            next_z += math.cos(rad) * player_speed
        elif ch == 's':
            next_x -= math.sin(rad) * player_speed
            next_z -= math.cos(rad) * player_speed
        elif ch == 'a':
            next_x += math.sin(rad + math.pi / 2.0) * player_speed
            next_z += math.cos(rad + math.pi / 2.0) * player_speed
        elif ch == 'd':
            next_x += math.sin(rad - math.pi / 2.0) * player_speed
            next_z += math.cos(rad - math.pi / 2.0) * player_speed

        curr_y = player_pos[1]
        res_x, res_z = resolve_entity_crate_collision(next_x, next_z, radius=0.9, y_height=curr_y)
        player_pos[0] = res_x
        player_pos[2] = res_z

        if ch == ' ' or key == b' ':
            if not is_jumping:
                is_jumping = True
                y_velocity = jump_strength
        elif ch == 'c':
            cheat_mode = not cheat_mode
            if cheat_mode:
                player_hits_left = MAX_PLAYER_HITS
                print(">> [CHEAT MODE ENABLED]: 9 Lives & Invulnerability ON!")
            else:
                print(">> [CHEAT MODE DISABLED]: Normal Damage Restored.")
        elif ch == 'f':
            if catnip_picked_up:
                active_weapon = "catnip" if active_weapon == "gun" else "gun"
                print(f">> Active Weapon Switched to: {active_weapon.upper()}")
            else:
                launch_projectile()
        elif ch == 'v':
            first_person = not first_person
        elif ch == 'j':
            player_yaw -= 5.0
        elif ch == 'l':
            player_yaw += 5.0
        elif ch == 'i':
            player_pitch = min(65.0, player_pitch + 5.0)
        elif ch == 'k':
            player_pitch = max(-65.0, player_pitch - 5.0)

    if ch == 'p':
        is_paused = not is_paused
    elif ch == 'r':
        reset_arena()
    elif key == b'\x1b':
        sys.exit(0)

    limit = ARENA_SIZE - 1.8
    player_pos[0] = max(-limit, min(limit, player_pos[0]))
    player_pos[2] = max(-limit, min(limit, player_pos[2]))

    glutPostRedisplay()

def special_key_listener(key, x, y):
    global crouching
    if key == 114 or key == 115:  
        crouching = not crouching
        glutPostRedisplay()

def reset_arena():
    global player_pos, player_yaw, player_pitch, player_hits_left
    global is_jumping, crouching, gun_picked_up, catnip_spawned, catnip_picked_up, active_weapon
    global score, zombies_killed, zombies_spawned, grenades, death_effects, zombies
    global is_game_over, is_level_cleared, is_paused, is_target_locked

    player_pos = [0.0, 1.0, -35.0]
    player_yaw = 0.0
    player_pitch = 0.0
    player_hits_left = MAX_PLAYER_HITS
    is_jumping = False
    crouching = False

    gun_picked_up = False
    catnip_spawned = False
    catnip_picked_up = False
    active_weapon = "gun"
    score = 0
    zombies_killed = 0
    zombies_spawned = 0
    grenades.clear()
    death_effects.clear()
    zombies.clear()
    is_game_over = False
    is_level_cleared = False
    is_paused = False
    is_target_locked = False

    for _ in range(2):
        spawn_zombie()

    print(">> Level 2 Arena Reset! Pick up the Grenade Launcher and eliminate all 10 zombies.")

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)   
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(WINDOW_TITLE)
    glClearColor(0.04, 0.05, 0.07, 1.0)   

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)

    reset_arena()

    print("=================================================================")
    print(" '9 Lives' - Level 2 Arena: Tactical Crate Cover & Combat")
    print(" Sole Character: 'tung tung tung sahur'")
    print(" Controls: Mouse Aim (Level 3 style), LMB Shoot, P Pause, C Cheat, F Switch")
    print(" 100% CSE423 Labs 1, 1.2, 2, 3 Compliant")
    print("=================================================================")

    glutMainLoop()

if __name__ == "__main__":
    main()


######################################################LAUNCHER FILE######################################
import os
import sys
import math
import random
import ctypes
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_LEVEL_DIR = os.path.join(BASE_DIR, "Main level files")

LEVEL_FILES = {
    1: os.path.join(MAIN_LEVEL_DIR, "Level 1 final.py"),
    2: os.path.join(MAIN_LEVEL_DIR, "Level 2 final"),
    3: os.path.join(MAIN_LEVEL_DIR, "Level 3 final")
}

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750

STATE_LEVEL_1           = 1
STATE_TRANSITION_1_TO_2 = 2
STATE_LEVEL_2           = 3
STATE_TRANSITION_2_TO_3 = 4
STATE_LEVEL_3           = 5
STATE_VICTORY           = 6

current_state = STATE_LEVEL_1

lvl1 = None
lvl2 = None
lvl3 = None

transition_timer = 0
transition_particles = []

def load_level_module(level_num):
    file_path = LEVEL_FILES.get(level_num)
    if not file_path or not os.path.isfile(file_path):
        print(f"[ERROR] Level {level_num} file not found: {file_path}")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as fp:
        code_str = fp.read()

    namespace = {
        '__file__': file_path,
        '__name__': f'level_{level_num}_module',
        'sys': sys,
        'os': os,
        'math': math,
        'random': random,
        'ctypes': ctypes,
    }

    compiled = compile(code_str, file_path, 'exec')
    exec(compiled, namespace)
    return namespace

def init_all_levels():
    global lvl1, lvl2, lvl3
    print(">> Initializing Campaign: Loading Level 1...")
    lvl1 = load_level_module(1)
    if 'load_character_model' in lvl1:
        lvl1['load_character_model']()
    if 'reset_game' in lvl1:
        lvl1['reset_game']()

    print(">> Initializing Campaign: Loading Level 2...")
    lvl2 = load_level_module(2)

    print(">> Initializing Campaign: Loading Level 3...")
    lvl3 = load_level_module(3)

    print(">> All 3 Levels loaded successfully into memory.")


    global transition_particles
    transition_particles = []
    for _ in range(count):
        ang = random.uniform(0, 2 * math.pi)
        spd = random.uniform(2.5, 9.0)
        dist = random.uniform(20, 600)
        size = random.uniform(2.0, 5.5)
        color_choice = random.choice([
            (0.1, 0.9, 1.0),
            (0.3, 0.6, 1.0),
            (0.8, 0.2, 1.0),
            (0.2, 1.0, 0.6),
            (1.0, 0.85, 0.2),
        ])
        transition_particles.append({
            'x': WINDOW_WIDTH / 2.0 + math.cos(ang) * dist,
            'y': WINDOW_HEIGHT / 2.0 + math.sin(ang) * dist,
            'vx': math.cos(ang) * spd,
            'vy': math.sin(ang) * spd,
            'size': size,
            'color': color_choice,
            'life': random.uniform(0.5, 1.0)
        })

def update_transition_particles():
    cx, cy = WINDOW_WIDTH / 2.0, WINDOW_HEIGHT / 2.0
    for p in transition_particles:
        p['x'] += p['vx']
        p['y'] += p['vy']
        if p['x'] < -50 or p['x'] > WINDOW_WIDTH + 50 or p['y'] < -50 or p['y'] > WINDOW_HEIGHT + 50:
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(3.0, 8.5)
            p['x'] = cx + math.cos(ang) * random.uniform(5, 40)
            p['y'] = cy + math.sin(ang) * random.uniform(5, 40)
            p['vx'] = math.cos(ang) * spd
            p['vy'] = math.sin(ang) * spd


def draw_rect_2d(x1, y1, x2, y2, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()

def draw_rect_border_2d(x1, y1, x2, y2, color, line_width=2.0):
    glColor3f(*color)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()

def render_string_2d(x, y, text_str, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for ch in text_str:
        glutBitmapCharacter(font, ord(ch))

def render_string_centered(y, text_str, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
    char_w = 9.0
    if font == GLUT_BITMAP_HELVETICA_12:
        char_w = 6.5
    elif font == GLUT_BITMAP_TIMES_ROMAN_24:
        char_w = 12.0
    total_w = len(text_str) * char_w
    start_x = max(20, (WINDOW_WIDTH - total_w) / 2.0)
    render_string_2d(start_x, y, text_str, color=color, font=font)

def render_string_bold(x, y, text_str, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
    for dx in [-1.0, 0.0, 1.0]:
        for dy in [-1.0, 0.0, 1.0]:
            render_string_2d(x + dx, y + dy, text_str, color=color, font=font)


def draw_transition_screen(from_lvl, to_lvl):
    global WINDOW_WIDTH, WINDOW_HEIGHT, transition_timer

    glClearColor(0.02, 0.03, 0.06, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    pulse = 0.5 + 0.5 * math.sin(transition_timer * 0.05)
    fast_pulse = 0.5 + 0.5 * math.sin(transition_timer * 0.12)

    for p in transition_particles:
        glColor3f(*p['color'])
        glPointSize(p['size'])
        glBegin(GL_POINTS)
        glVertex2f(p['x'], p['y'])
        glEnd()

        cx, cy = WINDOW_WIDTH / 2.0, WINDOW_HEIGHT / 2.0
        dx = p['x'] - cx
        dy = p['y'] - cy
        d = math.sqrt(dx*dx + dy*dy) + 0.01
        glColor3f(p['color'][0] * 0.4, p['color'][1] * 0.4, p['color'][2] * 0.4)
        glBegin(GL_LINES)
        glVertex2f(p['x'], p['y'])
        glVertex2f(p['x'] - (dx / d) * 16.0, p['y'] - (dy / d) * 16.0)
        glEnd()

    # 2. Outer Cybernetic Frame
    frame_col = (0.0, 0.75 + 0.25 * pulse, 1.0) if to_lvl == 2 else (1.0, 0.3 + 0.7 * pulse, 0.2)
    draw_rect_border_2d(30, 30, WINDOW_WIDTH - 30, WINDOW_HEIGHT - 30, frame_col, line_width=3.0)
    draw_rect_border_2d(36, 36, WINDOW_WIDTH - 36, WINDOW_HEIGHT - 36, (0.1, 0.2, 0.35), line_width=1.0)

    for cx, cy in [(30, 30), (WINDOW_WIDTH - 30, 30), (30, WINDOW_HEIGHT - 30), (WINDOW_WIDTH - 30, WINDOW_HEIGHT - 30)]:
        draw_rect_2d(cx - 8, cy - 8, cx + 8, cy + 8, frame_col)

    top_y = WINDOW_HEIGHT - 75
    if from_lvl == 1 and to_lvl == 2:
        badge_text = "* * *   LEVEL 1 CLEARED : THE BACKROOMS CONQUERED   * * *"
        badge_color = (0.2, 1.0, 0.5)
        title_text = "DIMENSIONAL WARP >> SECTOR 2: THE ZOMBIE CAT ARENA"
        title_color = (0.0, 0.95, 1.0)
    elif from_lvl == 2 and to_lvl == 3:
        badge_text = "* * *   LEVEL 2 CLEARED : ZOMBIE HORDE PURGED   * * *"
        badge_color = (0.2, 1.0, 0.5)
        title_text = "DIMENSIONAL WARP >> FINAL SECTOR: EVIL LARRY'S LAIR"
        title_color = (1.0, 0.45, 0.15)
    else:
        badge_text = "* * *   WARP GATE ACTIVE   * * *"
        badge_color = (0.2, 1.0, 0.5)
        title_text = f"PREPARING LEVEL {to_lvl}..."
        title_color = (1.0, 1.0, 1.0)

    render_string_centered(top_y, badge_text, color=badge_color, font=GLUT_BITMAP_HELVETICA_18)
    render_string_centered(top_y - 35, title_text, color=title_color, font=GLUT_BITMAP_TIMES_ROMAN_24)

    glBegin(GL_LINES)
    glColor3f(*title_color)
    glVertex2f(80, top_y - 50)
    glVertex2f(WINDOW_WIDTH - 80, top_y - 50)
    glEnd()

    panel_left = 65
    panel_right = WINDOW_WIDTH - 65
    panel_top = top_y - 75
    panel_bot = 120

    draw_rect_2d(panel_left, panel_bot, panel_right, panel_top, (0.04, 0.07, 0.12))
    draw_rect_border_2d(panel_left, panel_bot, panel_right, panel_top, (0.15, 0.35, 0.55), line_width=1.5)

    lore_y = panel_top - 32
    if from_lvl == 1 and to_lvl == 2:
        lore_lines = [
            ("MISSION REPORT:", (1.0, 0.85, 0.2)),
            ("Tung Tung Tung Sahur has successfully leaped through the Backrooms Exit Portal!", (0.9, 0.95, 1.0)),
            ("You survived treacherous lava pits, phasing tiles, and crushing mechanical walls.", (0.8, 0.85, 0.9)),
            ("", (1, 1, 1)),
            ("CURRENT SITUATION (LEVEL 2):", (1.0, 0.4, 0.4)),
            ("- You have emerged inside an abandoned high-security warehouse arena.", (0.9, 0.95, 1.0)),
            ("- The sector is overrun by 10 mutated Zombie!", (1.0, 0.75, 0.3)),
            ("- A tactical Grenade Launcher is resting on the central weapon pedestal.", (0.2, 0.95, 1.0)),
            ("- Eliminate all 10 zombies to unlock the rare Glowing Blue Catnip.", (0.2, 1.0, 0.6)),
            ("- Collect the catnip and enter the Glowing North Door to reach the Boss Sanctum.", (0.2, 1.0, 0.9)),
            ("", (1, 1, 1)),
            ("COMBAT CONTROLS:", (1.0, 0.85, 0.2)),
            ("- Mouse Look: Aim Reticle  |  LMB (Click): Launch Explosive Grenades", (0.0, 0.95, 1.0)),
            ("- W / A / S / D: Move  |  Spacebar: Jump  |  Ctrl: Crouch  |  V: Switch Camera POV", (0.85, 0.9, 0.95)),
        ]
    elif from_lvl == 2 and to_lvl == 3:
        lore_lines = [
            ("MISSION REPORT:", (1.0, 0.85, 0.2)),
            ("All 10 Zombie Cats neutralized! The Glowing Blue Catnip has been secured!", (0.9, 0.95, 1.0)),
            ("You have entered through the North Exit Door into the dark heart of the cat realm.", (0.8, 0.85, 0.9)),
            ("", (1, 1, 1)),
            ("FINAL MISSION (LEVEL 3 - BOSS FIGHT):", (1.0, 0.35, 0.35)),
            ("- EVIL LARRY has awakened! He is shielded by ancient Ash Energy.", (1.0, 0.55, 0.55)),
            ("- Regular weapons cannot pierce Evil Larry's shield directly.", (1.0, 0.75, 0.3)),
            ("- Press 'F' to switch to Glowing Catnip projectiles.", (0.0, 0.95, 1.0)),
            ("- Shoot Catnip at Small Larry minions to CHARM them into crashing his shield!", (0.2, 1.0, 0.6)),
            ("- Once his shield is broken, switch back to Bombs ('F') to finish Evil Larry!", (1.0, 0.85, 0.2)),
            ("- WATCH OUT for poisonous hairball pools, pounce shockwaves, and energy spheres.", (1.0, 0.4, 0.4)),
            ("", (1, 1, 1)),
            ("TACTICAL WEAPON SWITCHING:", (1.0, 0.85, 0.2)),
            ("- Press 'F': Toggle Weapons (Bombs <-> Charmed Catnip)  |  LMB: Throw Active Weapon", (0.0, 0.95, 1.0)),
        ]
    else:
        lore_lines = [
            ("LEVEL COMPLETE!", (0.2, 1.0, 0.5)),
            ("Entering next sector...", (1.0, 1.0, 1.0))
        ]

    for line_text, color in lore_lines:
        if line_text.startswith("MISSION REPORT:") or line_text.startswith("CURRENT SITUATION") or line_text.startswith("FINAL MISSION") or line_text.startswith("COMBAT") or line_text.startswith("TACTICAL"):
            render_string_bold(panel_left + 25, lore_y, line_text, color=color, font=GLUT_BITMAP_HELVETICA_18)
        else:
            render_string_2d(panel_left + 25, lore_y, line_text, color=color, font=GLUT_BITMAP_HELVETICA_18)
        lore_y -= 22

    # 5. Interactive Prompt Button at Bottom
    btn_w = 580
    btn_h = 44
    btn_x = (WINDOW_WIDTH - btn_w) / 2.0
    btn_y = 52

    btn_bg = (0.05, 0.15 + 0.15 * fast_pulse, 0.28 + 0.20 * fast_pulse)
    btn_border = (0.0, 0.85 + 0.15 * fast_pulse, 1.0) if to_lvl == 2 else (1.0, 0.65 + 0.35 * fast_pulse, 0.1)

    draw_rect_2d(btn_x, btn_y, btn_x + btn_w, btn_y + btn_h, btn_bg)
    draw_rect_border_2d(btn_x, btn_y, btn_x + btn_w, btn_y + btn_h, btn_border, line_width=2.5)

    prompt_label = f">> PRESS [ SPACEBAR ] OR [ ENTER ] TO ENTER LEVEL {to_lvl} <<"
    render_string_centered(btn_y + 14, prompt_label, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18)

    render_string_centered(22, "Press 'P' to pause  |  'R' to restart level  |  'ESC' / 'Q' to quit", color=(0.55, 0.65, 0.75), font=GLUT_BITMAP_HELVETICA_12)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()


def start_transition_1_to_2():
    global current_state, transition_timer
    print("\n" + "=" * 70)
    print(" [*] LEVEL 1 CLEAR! Player passed through the Backrooms Exit Portal!")
    print(" [*] Displaying Transition Screen: Escaping to Level 2 (Zombie Arena)...")
    print("=" * 70 + "\n")
    current_state = STATE_TRANSITION_1_TO_2
    transition_timer = 0
    init_transition_particles(90)

def enter_level_2():
    global current_state
    print("\n>> Loading Level 2: Zombie Cat Arena...")
    current_state = STATE_LEVEL_2
    if 'reset_arena' in lvl2:
        lvl2['reset_arena']()
    lvl2['mouse_initialized'] = False

def start_transition_2_to_3():
    global current_state, transition_timer
    print("\n" + "=" * 70)
    print(" [*] LEVEL 2 CLEAR! Player collected Catnip & unlocked North Exit Door!")
    print(" [*] Displaying Transition Screen: Entering Level 3 (Boss Fight)...")
    print("=" * 70 + "\n")
    current_state = STATE_TRANSITION_2_TO_3
    transition_timer = 0
    init_transition_particles(90)

def enter_level_3():
    global current_state
    print("\n>> Loading Level 3: The Boss Fight (Evil Larry)...")
    current_state = STATE_LEVEL_3
    if 'reset_level_3' in lvl3:
        lvl3['reset_level_3']()
    lvl3['mouse_initialized'] = False


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
                    if lvl1:
                        lvl1['WINDOW_WIDTH'] = w
                        lvl1['WINDOW_HEIGHT'] = h
                    if lvl2:
                        lvl2['WIN_W'] = w
                        lvl2['WIN_H'] = h
                    if lvl3:
                        lvl3['WIN_W'] = w
                        lvl3['WIN_H'] = h
    except:
        pass

def master_display():
    global current_state
    update_window_dimensions()

    if current_state == STATE_LEVEL_1:
        if lvl1 and 'display' in lvl1:
            lvl1['display']()

    elif current_state == STATE_TRANSITION_1_TO_2:
        draw_transition_screen(1, 2)

    elif current_state == STATE_LEVEL_2:
        if lvl2 and 'display' in lvl2:
            lvl2['display']()

    elif current_state == STATE_TRANSITION_2_TO_3:
        draw_transition_screen(2, 3)

    elif current_state == STATE_LEVEL_3:
        if lvl3 and 'display' in lvl3:
            lvl3['display']()

def master_idle():
    global current_state, transition_timer

    if current_state == STATE_LEVEL_1:
        if lvl1 and 'idle' in lvl1:
            lvl1['idle']()

        pos = lvl1.get('player_pos') if lvl1 else None
        if pos:
            px, py, pz = pos[0], pos[1], pos[2]
            dist_to_portal = math.sqrt((px - 70.0)**2 + (pz - 330.0)**2)
            if (64.0 <= px <= 76.0 and pz >= 318.0) or dist_to_portal <= 9.0:
                start_transition_1_to_2()

    elif current_state == STATE_TRANSITION_1_TO_2:
        transition_timer += 1
        update_transition_particles()
        glutPostRedisplay()

    elif current_state == STATE_LEVEL_2:
        if lvl2 and 'idle' in lvl2:
            lvl2['idle']()

        pos = lvl2.get('player_pos') if lvl2 else None
        catnip_picked = lvl2.get('catnip_picked_up', False) if lvl2 else False
        if catnip_picked and pos:
            px, py, pz = pos[0], pos[1], pos[2]
            dist_to_door = math.sqrt((px - 0.0)**2 + (pz - 59.0)**2)
            if (abs(px) <= 6.0 and pz >= 52.0) or dist_to_door <= 7.0:
                start_transition_2_to_3()

    elif current_state == STATE_TRANSITION_2_TO_3:
        transition_timer += 1
        update_transition_particles()
        glutPostRedisplay()


    elif current_state == STATE_LEVEL_3:
        if lvl3 and 'idle' in lvl3:
            lvl3['idle']()

def master_keyboard(key, x, y):
    global current_state

    try:
        raw_ch = key.decode('utf-8')
    except:
        raw_ch = str(key)
    ch = raw_ch.lower()

    if key == b'\x1b' or ch == 'q':
        print("\n>> Player exited campaign.")
        sys.exit(0)

    if current_state == STATE_TRANSITION_1_TO_2:
        if ch in (' ', '\r', '\n') or key in (b' ', b'\r', b'\n'):
            enter_level_2()
        return

    elif current_state == STATE_TRANSITION_2_TO_3:
        if ch in (' ', '\r', '\n') or key in (b' ', b'\r', b'\n'):
            enter_level_3()
        return

    if current_state == STATE_LEVEL_1:
        if lvl1 and 'keyboard_listener' in lvl1:
            lvl1['keyboard_listener'](key, x, y)

    elif current_state == STATE_LEVEL_2:
        if lvl2 and 'keyboard_listener' in lvl2:
            lvl2['keyboard_listener'](key, x, y)

    elif current_state == STATE_LEVEL_3:
        if lvl3 and 'keyboard_listener' in lvl3:
            lvl3['keyboard_listener'](key, x, y)

def master_special(key, x, y):
    if current_state == STATE_LEVEL_1:
        if lvl1 and 'special_key_listener' in lvl1:
            lvl1['special_key_listener'](key, x, y)
    elif current_state == STATE_LEVEL_2:
        if lvl2 and 'special_key_listener' in lvl2:
            lvl2['special_key_listener'](key, x, y)
    elif current_state == STATE_LEVEL_3:
        if lvl3 and 'special_key_listener' in lvl3:
            lvl3['special_key_listener'](key, x, y)

def master_mouse(button, state, x, y):
    if current_state == STATE_LEVEL_1:
        if lvl1 and 'mouse_listener' in lvl1:
            lvl1['mouse_listener'](button, state, x, y)
    elif current_state == STATE_LEVEL_2:
        if lvl2 and 'mouse_listener' in lvl2:
            lvl2['mouse_listener'](button, state, x, y)
    elif current_state == STATE_LEVEL_3:
        if lvl3 and 'mouse_listener' in lvl3:
            lvl3['mouse_listener'](button, state, x, y)


def run_campaign():
    print("\n" + "=" * 75)
    print("       9 LIVES: EVIL CAT WORLD - MASTER CAMPAIGN")
    print("       Seamless 3-Level Progression & Transition Engine")
    print("=" * 75)
    print(" [1] Level 1: The Backrooms Maze (Exit Portal at Z >= 318)")
    print(" [2] Level 2: Zombie Arena   (North Exit Door at Z >= 52)")
    print(" [3] Level 3: The Boss Fight     (Defeat Evil Larry)")
    print("=" * 75 + "\n")

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"9 Lives - Level 1: Connected Backrooms Maze Arena ('tung tung tung sahur')")

    init_all_levels()

    glutDisplayFunc(master_display)
    glutIdleFunc(master_idle)
    glutKeyboardFunc(master_keyboard)
    glutSpecialFunc(master_special)
    glutMouseFunc(master_mouse)

    print(">> Game started! Starting Level 1...")
    glutMainLoop()

if __name__ == "__main__":
    run_campaign()

        
######################################################LEVEL 3 FILES######################################
import sys
import math
import random
import ctypes
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
WIN_W, WIN_H = 1000, 750
ARENA_RADIUS = 550.0
WALL_HEIGHT  = 110.0

INNER_RING_R = 200.0
INNER_COUNT  = 8
INNER_BASE_R = 8.0
INNER_TOP_R  = 8.0
INNER_HEIGHT = 48.0

OUTER_RING_R = 400.0
OUTER_COUNT  = 8
OUTER_BASE_R = 16.0
OUTER_TOP_R  = 12.0
OUTER_HEIGHT = 100.0


player_pos   = [0.0, 0.0, -320.0]
player_yaw   = 0.0
player_pitch = 0.0
BASE_PLAYER_SPEED = 5
player_speed = 5
crouching    = False

is_jumping   = False
y_velocity   = 0.0
gravity      = -0.055
jump_strength = 1.20
ground_y     = 0.0

MAX_PLAYER_HITS = 9
player_hits_left = 9
player_invulnerable_timer = 0
cheat_mode   = False
is_game_over     = False
is_level_cleared = False
is_paused        = False
score            = 0

first_person = False
cam_dist     = 48.0
cam_height   = 14.0

last_mouse_x = 0
last_mouse_y = 0
mouse_initialized = False

walk_anim_phase = 0.0
is_moving = False
arm_throw_timer = 0

active_weapon = "gun"


evil_larry_pos      = [0.0, 0.0, 0.0]
evil_larry_yaw      = 180.0
EVIL_LARRY_MAX_SHIELD = 300.0
EVIL_LARRY_MAX_HP     = 500.0
evil_larry_shield     = 300.0
evil_larry_hp         = 500.0
evil_larry_shield_broken = False
evil_larry_speed      = 0.52
evil_larry_hit_flash  = 0
small_pillars_destroyed = False
meow_timer = 0

def resolve_pillar_collisions(nx, nz):
    for k in range(OUTER_COUNT):
        ang = 2 * math.pi * k / OUTER_COUNT
        px = OUTER_RING_R * math.cos(ang)
        pz = OUTER_RING_R * math.sin(ang)
        d = math.sqrt((nx - px)**2 + (nz - pz)**2)
        min_d = OUTER_BASE_R + 12.0
        if d < min_d:
            if d > 0.001:
                nx = px + ((nx - px) / d) * min_d
                nz = pz + ((nz - pz) / d) * min_d
            else:
                nx += 1.0

    if not small_pillars_destroyed:
        for k in range(INNER_COUNT):
            ang = 2 * math.pi * k / INNER_COUNT
            px = INNER_RING_R * math.cos(ang)
            pz = INNER_RING_R * math.sin(ang)
            d = math.sqrt((nx - px)**2 + (nz - pz)**2)
            min_d = INNER_BASE_R + 10.0
            if d < min_d:
                if d > 0.001:
                    nx = px + ((nx - px) / d) * min_d
                    nz = pz + ((nz - pz) / d) * min_d
                else:
                    nx += 1.0

    return nx, nz

TOTAL_SMALL_LARRY_ALLOWED = 9
small_larrys_spawned_count = 0
MAX_ACTIVE_SMALL_LARRY    = 3
small_larrys = []

small_larry_speed = 0.08

class SmallLarry:
    def __init__(self, x, z):
        self.pos = [x, 0.0, z]
        self.x = x
        self.y = 0.0
        self.z = z
        self.yaw = 0.0
        self.alive = True
        self.hp = 4
        self.hit_flash = 0
        self.charmed = False  
        self.sparkle_rot = 0.0

    def update(self, player_x, player_z, boss_x, boss_z):
        if not self.alive:
            return

        if self.charmed:
            self.sparkle_rot = (self.sparkle_rot + 12.0) % 360.0
            target_x = boss_x
            target_z = boss_z
            speed = 0.85  # Faster sprint to Big Larry
        else:
            target_x = player_x
            target_z = player_z
            speed = small_larry_speed

        dx = target_x - self.x
        dz = target_z - self.z
        dist = math.sqrt(dx*dx + dz*dz)
        if dist > 0.001:
            nx = self.x + (dx / dist) * speed
            nz = self.z + (dz / dist) * speed
            self.x, self.z = resolve_pillar_collisions(nx, nz)
            self.pos[0] = self.x
            self.pos[2] = self.z
            self.yaw = math.degrees(math.atan2(dx, dz))

        if self.hit_flash > 0:
            self.hit_flash -= 1


bombs = []
catnips = []
weapon_cooldown = 0
WEAPON_COOLDOWN_MAX = 14
BOMB_DAMAGE = 15.0

class Bomb:
    def __init__(self, x, y, z, vx, vy, vz):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.life = 130
        self.alive = True
        self.rot = 0.0

    def update(self):
        if not self.alive:
            return
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vy += -0.048
        self.rot += 14.0
        self.life -= 1
        if self.life <= 0:
            self.alive = False

class CatnipProjectile:
    def __init__(self, x, y, z, vx, vy, vz):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.life = 150
        self.alive = True
        self.rot = 0.0

    def update(self):
        if not self.alive:
            return
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vy += -0.038
        self.rot += 12.0
        self.life -= 1
        if self.life <= 0:
            self.alive = False


explosions = []

class Explosion:
    def __init__(self, x, y, z, max_r=18.0, is_blue=False):
        self.x = x
        self.y = y
        self.z = z
        self.radius = 1.5
        self.max_radius = max_r
        self.life = 24
        self.max_life = 24
        self.is_blue = is_blue
        self.particles = []
        for _ in range(18):
            theta = random.uniform(0, 2*math.pi)
            phi = random.uniform(-math.pi/2, math.pi/2)
            spd = random.uniform(0.7, 2.4)
            self.particles.append([
                0.0, 0.0, 0.0,
                math.cos(phi)*math.sin(theta)*spd,
                math.sin(phi)*spd + 0.35,
                math.cos(phi)*math.cos(theta)*spd
            ])

    def update(self):
        self.life -= 1
        progress = 1.0 - (self.life / float(self.max_life))
        self.radius = 1.5 + (self.max_radius - 1.5) * progress
        for p in self.particles:
            p[0] += p[3]
            p[1] += p[4]
            p[2] += p[5]
            p[4] -= 0.032

SPEEDBOOST_INTERVAL_FRAMES = 13 * 60
speedboost_spawn_timer = 0
speed_boost_duration_timer = 0

SPEEDBOOST_LOCATIONS = [
    [-240.0, 6.0, 0.0],
    [ 240.0, 6.0, 0.0],
    [ 0.0, 6.0, -240.0],
    [ 0.0, 6.0,  240.0]
]

class SpeedboostItem:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.active = True
        self.rot = 0.0
        self.respawn_timer = 0

    def update(self):
        self.rot = (self.rot + 3.0) % 360.0
        if not self.active:
            self.respawn_timer += 1
            if self.respawn_timer >= SPEEDBOOST_INTERVAL_FRAMES:
                self.active = True
                self.respawn_timer = 0

speedboost_items = [
    SpeedboostItem(*SPEEDBOOST_LOCATIONS[0]),
    SpeedboostItem(*SPEEDBOOST_LOCATIONS[1]),
    SpeedboostItem(*SPEEDBOOST_LOCATIONS[2]),
    SpeedboostItem(*SPEEDBOOST_LOCATIONS[3])
]

HAIRBALL_COOLDOWN = 30 * 60
hairball_timer = HAIRBALL_COOLDOWN
hairballs = []
hairball_puddles = []

class Hairball:
    def __init__(self, x, y, z, tx, tz):
        self.x = x
        self.y = y
        self.z = z
        self.rot = 0.0
        self.alive = True

        target_limit = ARENA_RADIUS - 65.0
        dist_t = math.sqrt(tx*tx + tz*tz)
        if dist_t > target_limit:
            tx = (tx / dist_t) * target_limit
            tz = (tz / dist_t) * target_limit

        dx = tx - x
        dz = tz - z
        dist = math.sqrt(dx*dx + dz*dz)
        flight_time = max(45.0, min(85.0, dist / 4.2))
        self.vx = dx / flight_time
        self.vz = dz / flight_time
        self.vy = 0.5 * 0.045 * flight_time + 1.2
        self.gravity = -0.045

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vy += self.gravity
        self.rot += 14.0

        r_curr = math.sqrt(self.x**2 + self.z**2)
        wall_limit = ARENA_RADIUS - 35.0
        if r_curr > wall_limit:
            self.x = (self.x / r_curr) * wall_limit
            self.z = (self.z / r_curr) * wall_limit
            self.y = 0.2
            self.alive = False

        if self.y <= 0.2:
            self.y = 0.2
            self.alive = False

class HairballPuddle:
    def __init__(self, x, z):
        self.radius = 38.0
        puddle_limit = ARENA_RADIUS - self.radius - 20.0
        r = math.sqrt(x*x + z*z)
        if r > puddle_limit:
            x = (x / r) * puddle_limit
            z = (z / r) * puddle_limit

        self.x = x
        self.z = z
        self.life = 480
        self.max_life = 480
        self.bubbles = []
        for _ in range(16):
            self.bubbles.append([
                random.uniform(-30, 30),
                random.uniform(0.2, 4.5),
                random.uniform(-30, 30),
                random.uniform(0.05, 0.14)
            ])

    def update(self):
        self.life -= 1
        for b in self.bubbles:
            b[1] += b[3]
            if b[1] > 6.5:
                b[1] = 0.2
                b[0] = random.uniform(-30, 30)
                b[2] = random.uniform(-30, 30)

POUNCE_COOLDOWN = 15 * 60
pounce_timer = POUNCE_COOLDOWN
pounce_state = 'IDLE'
pounce_sub_timer = 0
pounce_target = [0.0, 0.0]
pounce_start = [0.0, 0.0]
pounce_shockwave_r = 0.0
pounce_shockwave_life = 0

boss_spherical_timer = random.randint(4 * 60, 5 * 60)
boss_projectiles = []

class BossProjectile:
    def __init__(self, x, y, z, tx, ty, tz):
        self.x = x
        self.y = y
        self.z = z
        self.rot = 0.0
        self.radius = 6.0
        self.life = 180
        self.alive = True
        dx = tx - x
        dy = ty - y
        dz = tz - z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        spd = 3.6
        if dist > 0.001:
            self.vx = (dx / dist) * spd
            self.vy = (dy / dist) * spd
            self.vz = (dz / dist) * spd
        else:
            self.vx = 0.0
            self.vy = 0.0
            self.vz = spd

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.rot += 16.0
        self.life -= 1
        if self.life <= 0 or self.y <= 0.0:
            self.alive = False

        for k in range(OUTER_COUNT):
            ang = 2 * math.pi * k / OUTER_COUNT
            px = OUTER_RING_R * math.cos(ang)
            pz = OUTER_RING_R * math.sin(ang)
            d = math.sqrt((self.x - px)**2 + (self.z - pz)**2)
            if d < (OUTER_BASE_R + self.radius) and self.y < OUTER_HEIGHT:
                self.alive = False
                explosions.append(Explosion(self.x, self.y, self.z, max_r=14.0))
                break

        if not small_pillars_destroyed and self.alive:
            for k in range(INNER_COUNT):
                ang = 2 * math.pi * k / INNER_COUNT
                px = INNER_RING_R * math.cos(ang)
                pz = INNER_RING_R * math.sin(ang)
                d = math.sqrt((self.x - px)**2 + (self.z - pz)**2)
                if d < (INNER_BASE_R + self.radius) and self.y < INNER_HEIGHT:
                    self.alive = False
                    explosions.append(Explosion(self.x, self.y, self.z, max_r=14.0))
                    break

_Q = None
def Q():
    global _Q
    if _Q is None:
        _Q = gluNewQuadric()
    return _Q


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
            if cx*cx + cz*cz > ARENA_RADIUS*ARENA_RADIUS:
                continue
            def s(v, cx=cx, cz=cz):
                return (cx+(v[0]-cx)*shrink, cz+(v[1]-cz)*shrink)
            w1=s(v1); w2=s(v2); w3=s(v3); w4=s(v4)
            _floor_cache['plates'].extend([
                (w1[0],0.18,w1[1]),(w2[0],0.18,w2[1]),
                (w3[0],0.18,w3[1]),(w4[0],0.18,w4[1]),
            ])

def draw_floor():
    if _floor_cache is None:
        _build_floor()
    glBegin(GL_TRIANGLES)
    for tri in _floor_cache['lava']:
        glColor3f(0.80,0.26,0.0); glVertex3f(*tri[0])
        glColor3f(0.52,0.08,0.0); glVertex3f(*tri[1]); glVertex3f(*tri[2])
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.07,0.02,0.02)
    for v in _floor_cache['plates']:
        glVertex3f(*v)
    glEnd()

def draw_floor_occluder():
    glBegin(GL_TRIANGLES)
    glColor3f(0.02, 0.01, 0.01)
    S = 48; R = ARENA_RADIUS + 250.0
    for i in range(S):
        t1=2*math.pi*i/S; t2=2*math.pi*(i+1)/S
        glVertex3f(0, -2, 0)
        glVertex3f(R*math.cos(t1), -2, R*math.sin(t1))
        glVertex3f(R*math.cos(t2), -2, R*math.sin(t2))
    glEnd()

_wall_cache = None
WALL_COLORS = {'out': (0.13,0.045,0.04), 'inn': (0.13,0.045,0.04), 'top': (0.13,0.045,0.04)}

def _build_wall():
    global _wall_cache
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
    Ri = ARENA_RADIUS - 20.0
    glBegin(GL_LINES)
    glColor3f(0.92,0.32,0.0)
    for i in range(72):
        a1=2*math.pi*i/72; a2=2*math.pi*(i+1)/72
        glVertex3f(Ri*math.cos(a1),0.8,Ri*math.sin(a1))
        glVertex3f(Ri*math.cos(a2),0.8,Ri*math.sin(a2))
    glEnd()

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

def draw_small_pillar():
    segs = 20
    glColor3f(0.55, 0.54, 0.51)
    gluCylinder(Q(), INNER_BASE_R, INNER_TOP_R, INNER_HEIGHT, segs, 1)

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
    glTranslatef(0, 0, plinth_h)
    body_h = H - plinth_h - 12.0

    glColor3f(0.14, 0.045, 0.04)
    gluCylinder(Q(), Rb, Rt, body_h, segs, 1)

    for frac in [0.0, 0.33, 0.66, 1.0]:
        bp = frac * body_h
        br = Rb + (Rt-Rb)*frac + 2.8
        bh = 6.0
        glPushMatrix()
        glTranslatef(0, 0, bp)
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


def draw_tung_tung_sahur(cam_x=0.0, cam_z=0.0):
    if first_person:
        return

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_yaw + 180.0, 0, 1, 0)
    glRotatef(-90.0, 1, 0, 0)

    scale_f = 0.08
    if crouching:
        glScalef(scale_f, scale_f * 0.6, scale_f)
    else:
        glScalef(scale_f, scale_f, scale_f)

    glTranslatef(0, 0, 10.0)

    c_body   = (222/255, 137/255, 34/255)
    c_dark   = (117/255, 76/255, 18/255)
    c_goggle = (229/255, 230/255, 230/255)
    c_white  = (1.0, 1.0, 1.0)

    rad_yaw = math.radians(player_yaw)
    fwd_x = math.sin(rad_yaw)
    fwd_z = math.cos(rad_yaw)
    to_cam_x = cam_x - player_pos[0]
    to_cam_z = cam_z - player_pos[2]
    is_front = (fwd_x * to_cam_x + fwd_z * to_cam_z) > 0.0

    def draw_face_details():
        for eye_x in [-16, 16]:
            glPushMatrix()
            glColor3f(*c_goggle)
            glTranslatef(eye_x, 21, 140)
            glScalef(0.28, 0.08, 0.35)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_white)
            glTranslatef(eye_x, 25, 140)
            glScalef(0.18, 0.08, 0.22)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_dark)
            glTranslatef(eye_x, 29, 140)
            glScalef(0.08, 0.05, 0.1)
            glutSolidCube(100)
            glPopMatrix()

            glPushMatrix()
            glColor3f(*c_dark)
            glTranslatef(eye_x, 22, 162)
            glScalef(0.25, 0.06, 0.06)
            glutSolidCube(100)
            glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(0, 22, 120)
        glScalef(0.06, 0.06, 0.16)
        glutSolidCube(100)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(-2, 22, 105)
        glScalef(0.38, 0.06, 0.06)
        glutSolidCube(100)
        glPopMatrix()

    if not is_front:
        draw_face_details()

    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 95)
    glScalef(0.65, 0.4, 1.5)
    glutSolidCube(100)
    glPopMatrix()

    if is_front:
        draw_face_details()

    # Left Arm
    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(-38.5, 0, 85)
    glScalef(0.12, 0.2, 0.8)
    glutSolidCube(100)
    glPopMatrix()

    # Right Arm
    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(38.5, 0, 85)
    if arm_throw_timer > 0:
        throw_angle = math.sin((14.0 - arm_throw_timer) / 14.0 * math.pi) * 55.0
        glRotatef(-throw_angle, 1, 0, 0)
    glScalef(0.12, 0.2, 0.8)
    glutSolidCube(100)
    glPopMatrix()

    leg_swing = math.sin(walk_anim_phase) * 20.0

    glPushMatrix()
    glTranslatef(-14, 0, 10)
    glRotatef(leg_swing, 1, 0, 0)
    glColor3f(*c_dark)
    glScalef(0.14, 0.18, 0.28)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-14, 8, -5)
    glRotatef(leg_swing, 1, 0, 0)
    glColor3f(*c_dark)
    glScalef(0.22, 0.36, 0.10)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(14, 0, 10)
    glRotatef(-leg_swing, 1, 0, 0)
    glColor3f(*c_dark)
    glScalef(0.14, 0.18, 0.28)
    glutSolidCube(100)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(14, 8, -5)
    glRotatef(-leg_swing, 1, 0, 0)
    glColor3f(*c_dark)
    glScalef(0.22, 0.36, 0.10)
    glutSolidCube(100)
    glPopMatrix()

    glPopMatrix()

def draw_evil_larry_boss():
    if evil_larry_hp <= 0:
        return

    glPushMatrix()
    glTranslatef(evil_larry_pos[0], evil_larry_pos[1], evil_larry_pos[2])
    glRotatef(evil_larry_yaw + 180.0, 0, 1, 0)
    glRotatef(-90.0, 1, 0, 0)

    scale_boss = 0.72
    glScalef(scale_boss, scale_boss, scale_boss)

    if evil_larry_hit_flash > 0:
        c_black = (0.85, 0.15, 0.15)
    else:
        c_black = (0.02, 0.02, 0.02)

    if small_pillars_destroyed:
        c_inner_ear  = (0.55, 0.04, 0.04)
        c_eye_white  = (0.75, 0.05, 0.05)
        c_pupil      = (0.20, 0.00, 0.00)
    else:
        c_inner_ear  = (0.35, 0.35, 0.35)
        c_eye_white  = (0.95, 0.95, 0.95)
        c_pupil      = (0.02, 0.02, 0.02)

    c_nose_mouth = (0.95, 0.95, 0.95)


    glPushMatrix()
    glColor3f(*c_black)
    glTranslatef(0, 0, 45)
    glScalef(1.2, 0.6, 0.9)
    glutSolidCube(100)
    glPopMatrix()


    glPushMatrix()
    glColor3f(*c_black)
    glTranslatef(0, 0, 100)
    glScalef(1.2, 0.6, 0.8)
    gluSphere(Q(), 50, 16, 16)
    glPopMatrix()

    for side, angle in [(-32, -8), (32, 8)]:
        glPushMatrix()
        glColor3f(*c_black)
        glTranslatef(side, 0, 115)
        glRotatef(angle, 0, 1, 0)
        gluCylinder(Q(), 22, 0, 70, 14, 14)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_inner_ear)
        glTranslatef(side, 0, 115)
        glRotatef(angle, 0, 1, 0)
        glBegin(GL_TRIANGLES)
        glVertex3f(-8, 20, 10)
        glVertex3f(8, 20, 10)
        glVertex3f(0, 12, 52)
        glEnd()
        glPopMatrix()

  
    for eye_x in [-22, 22]:
        glPushMatrix()
        glColor3f(*c_eye_white)
        glTranslatef(eye_x, 32, 100)
        glScalef(1.0, 0.35, 1.0)
        gluSphere(Q(), 17, 16, 16)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_pupil)
        glTranslatef(eye_x, 35, 106)
        glScalef(0.7, 0.35, 0.95)
        gluSphere(Q(), 11.0, 14, 14)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0.02, 0.02, 0.02)
        glTranslatef(eye_x, 36, 114)
        glScalef(0.42, 0.18, 0.14)
        glutSolidCube(100)
        glPopMatrix()


    glPushMatrix()
    glColor3f(*c_nose_mouth)
    glTranslatef(0, 34, 88)
    glScalef(1.1, 0.45, 0.9)
    gluSphere(Q(), 4.5, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_nose_mouth)
    glTranslatef(0, 33, 80)
    glScalef(0.03, 0.03, 0.14)
    glutSolidCube(100)
    glPopMatrix()

    for side, sign in [(-3, 35), (3, -35)]:
        glPushMatrix()
        glColor3f(*c_nose_mouth)
        glTranslatef(side, 33, 74)
        glRotatef(sign, 0, 1, 0)
        glScalef(0.10, 0.03, 0.03)
        glutSolidCube(100)
        glPopMatrix()


    glColor3f(0.05, 0.05, 0.05)
    glBegin(GL_LINES)
    glVertex3f(-45, 20, 104); glVertex3f(-95, 20, 108)
    glVertex3f(-45, 20, 96);  glVertex3f(-98, 20, 96)
    glVertex3f(-45, 20, 88);  glVertex3f(-95, 20, 84)
    glVertex3f(45, 20, 104);  glVertex3f(95, 20, 108)
    glVertex3f(45, 20, 96);   glVertex3f(98, 20, 96)
    glVertex3f(45, 20, 88);   glVertex3f(95, 20, 84)
    glEnd()

    glPopMatrix()

def draw_single_small_larry(sl):
    if not sl.alive:
        return

    glPushMatrix()
    glTranslatef(sl.x, sl.y, sl.z)
    glRotatef(sl.yaw + 180.0, 0, 1, 0)
    glRotatef(-90.0, 1, 0, 0)

    scale_small = 0.13
    glScalef(scale_small, scale_small, scale_small)

    if sl.charmed:
        c_body = (0.1, 0.85, 1.0)
        c_dark = (0.0, 0.50, 0.85)
        c_inner_ear = (0.7, 0.95, 1.0)
    elif sl.hit_flash > 0:
        c_body = (1.0, 0.3, 0.3)
        c_dark = (0.8, 0.1, 0.1)
        c_inner_ear  = (0.9, 0.7, 0.6)
    else:
        c_body = (212/255, 155/255, 95/255)
        c_dark = (140/255, 90/255, 45/255)
        c_inner_ear  = (0.9, 0.7, 0.6)

    c_eye_white  = (1.0, 1.0, 1.0)
    c_eye_black  = (0.05, 0.05, 0.05)
    c_nose_mouth = (0.95, 0.95, 0.95)

    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 45)
    glScalef(1.2, 0.6, 0.9)
    glutSolidCube(100)
    glPopMatrix()

   
    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 100)
    glScalef(1.2, 0.6, 0.8)
    gluSphere(Q(), 50, 14, 14)
    glPopMatrix()

    for side, angle in [(-32, -8), (32, 8)]:
        glPushMatrix()
        glColor3f(*c_body)
        glTranslatef(side, 0, 115)
        glRotatef(angle, 0, 1, 0)
        gluCylinder(Q(), 22, 0, 70, 12, 12)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_inner_ear)
        glTranslatef(side, 0, 115)
        glRotatef(angle, 0, 1, 0)
        glBegin(GL_TRIANGLES)
        glVertex3f(-8, 20, 10); glVertex3f(8, 20, 10); glVertex3f(0, 12, 52)
        glEnd()
        glPopMatrix()

    
    for eye_x in [-22, 22]:
        glPushMatrix()
        glColor3f(*c_eye_white)
        glTranslatef(eye_x, 32, 100)
        glScalef(1.0, 0.35, 1.0)
        gluSphere(Q(), 17, 14, 14)
        glPopMatrix()

        glPushMatrix()
        glColor3f(*c_eye_black)
        glTranslatef(eye_x, 35, 106)
        glScalef(0.7, 0.35, 0.95)
        gluSphere(Q(), 11.0, 12, 12)
        glPopMatrix()

    glPushMatrix()
    glColor3f(*c_nose_mouth)
    glTranslatef(0, 34, 88)
    glScalef(1.1, 0.45, 0.9)
    gluSphere(Q(), 4.5, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glColor3f(*c_nose_mouth)
    glTranslatef(0, 33, 80)
    glScalef(0.03, 0.03, 0.14)
    glutSolidCube(100)
    glPopMatrix()

    if sl.charmed:
        glPointSize(6)
        glBegin(GL_POINTS)
        for ang in range(0, 360, 45):
            r = math.radians(ang + sl.sparkle_rot)
            glColor3f(0.2, 0.95, 1.0)
            glVertex3f(math.cos(r) * 75, math.sin(r) * 75, 120)
        glEnd()

    glPopMatrix()

def draw_bombs():
    for b in bombs:
        if not b.alive:
            continue
        glPushMatrix()
        glTranslatef(b.x, b.y, b.z)
        glRotatef(b.rot, 1, 1, 0)
        glColor3f(0.12, 0.12, 0.12)
        gluSphere(Q(), 4.0, 10, 10)
        glTranslatef(0.0, 4.0, 0.0)
        glColor3f(1.0, 0.55, 0.0)
        gluSphere(Q(), 1.4, 6, 6)
        glPopMatrix()

def draw_catnips():
    for cn in catnips:
        if not cn.alive:
            continue
        glPushMatrix()
        glTranslatef(cn.x, cn.y, cn.z)
        glRotatef(cn.rot, 1, 1, 0)
        glColor3f(0.0, 0.70, 1.0)
        glutSolidCube(5.0)
        glColor3f(0.3, 0.95, 1.0)
        gluSphere(Q(), 3.2, 8, 8)
        glPopMatrix()

def draw_explosions():
    for exp in explosions:
        if exp.life <= 0:
            continue
        glPushMatrix()
        glTranslatef(exp.x, exp.y, exp.z)
        alpha = exp.life / float(exp.max_life)
        if exp.is_blue:
            glColor3f(0.1 * alpha, 0.85 * alpha, 1.0 * alpha)
        else:
            glColor3f(1.0 * alpha, 0.45 * alpha, 0.05 * alpha)
        gluSphere(Q(), exp.radius, 10, 10)
        glPointSize(4)
        glBegin(GL_POINTS)
        for p in exp.particles:
            if exp.is_blue:
                glColor3f(0.4 * alpha, 0.95 * alpha, 1.0 * alpha)
            else:
                glColor3f(1.0, 0.85 * alpha, 0.2 * alpha)
            glVertex3f(p[0], p[1], p[2])
        glEnd()
        glPopMatrix()

def draw_hairballs_and_puddles():
    for hb in hairballs:
        if not hb.alive:
            continue
        glPushMatrix()
        glTranslatef(hb.x, hb.y, hb.z)
        glRotatef(hb.rot, 1, 1, 0)
        glColor3f(0.20, 0.85, 0.10)
        gluSphere(Q(), 9.5, 12, 12)
        glColor3f(0.35, 0.95, 0.15)
        gluSphere(Q(), 7.0, 8, 8)
        glPointSize(6)
        glBegin(GL_POINTS)
        for a in range(0, 360, 40):
            rad_hb = math.radians(a + hb.rot)
            glColor3f(0.40, 1.0, 0.20)
            glVertex3f(math.cos(rad_hb) * 11.5, math.sin(rad_hb) * 11.5, 0)
            glVertex3f(0, math.cos(rad_hb) * 11.5, math.sin(rad_hb) * 11.5)
        glEnd()
        glPopMatrix()

    for pd in hairball_puddles:
        if pd.life <= 0:
            continue
        alpha = pd.life / float(pd.max_life)
        glBegin(GL_TRIANGLES)
        segs = 28
        for i in range(segs):
            a1 = 2 * math.pi * i / segs
            a2 = 2 * math.pi * (i + 1) / segs
            glColor3f(0.20 * alpha, 0.75 * alpha, 0.12 * alpha)
            glVertex3f(pd.x, 0.35, pd.z)
            glColor3f(0.10 * alpha, 0.40 * alpha, 0.06 * alpha)
            glVertex3f(pd.x + math.cos(a1) * pd.radius, 0.35, pd.z + math.sin(a1) * pd.radius)
            glVertex3f(pd.x + math.cos(a2) * pd.radius, 0.35, pd.z + math.sin(a2) * pd.radius)
        glEnd()

        glPointSize(5)
        glBegin(GL_POINTS)
        glColor3f(0.45 * alpha, 1.0 * alpha, 0.25 * alpha)
        for b in pd.bubbles:
            glVertex3f(pd.x + b[0], b[1], pd.z + b[2])
        glEnd()

def draw_pounce_effects():
    if pounce_state in ['WINDUP', 'AIR']:
        glBegin(GL_LINES)
        glColor3f(1.0, 0.15, 0.15)
        segs = 36
        r = 38.0
        for i in range(segs):
            a1 = 2 * math.pi * i / segs
            a2 = 2 * math.pi * (i + 1) / segs
            glVertex3f(pounce_target[0] + math.cos(a1) * r, 0.6, pounce_target[1] + math.sin(a1) * r)
            glVertex3f(pounce_target[0] + math.cos(a2) * r, 0.6, pounce_target[1] + math.sin(a2) * r)
        glVertex3f(pounce_target[0] - 15, 0.6, pounce_target[1] - 15)
        glVertex3f(pounce_target[0] + 15, 0.6, pounce_target[1] + 15)
        glVertex3f(pounce_target[0] - 15, 0.6, pounce_target[1] + 15)
        glVertex3f(pounce_target[0] + 15, 0.6, pounce_target[1] - 15)
        glEnd()

    if pounce_shockwave_life > 0:
        fade = pounce_shockwave_life / 25.0
        glBegin(GL_LINES)
        glColor3f(1.0 * fade, 0.6 * fade, 0.1 * fade)
        segs = 40
        for i in range(segs):
            a1 = 2 * math.pi * i / segs
            a2 = 2 * math.pi * (i + 1) / segs
            glVertex3f(pounce_target[0] + math.cos(a1) * pounce_shockwave_r, 0.8, pounce_target[1] + math.sin(a1) * pounce_shockwave_r)
            glVertex3f(pounce_target[0] + math.cos(a2) * pounce_shockwave_r, 0.8, pounce_target[1] + math.sin(a2) * pounce_shockwave_r)
        glEnd()

def draw_boss_projectiles():
    for bp in boss_projectiles:
        if not bp.alive:
            continue
        glPushMatrix()
        glTranslatef(bp.x, bp.y, bp.z)
        glRotatef(bp.rot, 1, 0, 1)
        glColor3f(0.95, 0.20, 0.95)
        gluSphere(Q(), bp.radius, 12, 12)
        glColor3f(1.0, 0.85, 1.0)
        gluSphere(Q(), bp.radius * 0.55, 8, 8)
        glPointSize(4)
        glBegin(GL_POINTS)
        for a in range(0, 360, 60):
            rad_bp = math.radians(a + bp.rot)
            glColor3f(1.0, 0.5, 1.0)
            glVertex3f(math.cos(rad_bp) * (bp.radius + 3.0), math.sin(rad_bp) * (bp.radius + 3.0), 0)
        glEnd()
        glPopMatrix()


def draw_text(x, y, text_str, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
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
    for dx in [-1.0, 0.0, 1.0]:
        for dy in [-1.0, 0.0, 1.0]:
            draw_text(x + dx, y + dy, text_str, color=color, font=font)

def draw_bar_2d(x, y, w, h, fill_pct, fill_color, border_color=(1.0, 1.0, 1.0)):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
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

def draw_crosshair():
    cx, cy = WIN_W // 2, WIN_H // 2
    size = 10
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_LINES)
    glColor3f(1.0, 0.2, 0.2)
    glVertex2f(cx - size, cy); glVertex2f(cx + size, cy)
    glVertex2f(cx, cy - size); glVertex2f(cx, cy + size)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_hud():
   
    pw, ph = 220, 16
    px, py = 25, 25
    player_pct = player_hits_left / float(MAX_PLAYER_HITS)
    draw_bar_2d(px, py, pw, ph, player_pct, (0.1, 0.9, 0.2), border_color=(0.9, 0.9, 0.9))

   
    w_name = "BOMB / GRENADE" if active_weapon == "gun" else "GLOWING CATNIP"
    draw_text(px, py + 26, f"WEAPON: {w_name} (Press 'F' to switch | Click LMB to shoot)", color=(0.0, 0.95, 1.0), font=GLUT_BITMAP_HELVETICA_18)

    if speed_boost_duration_timer > 0:
        secs_left = speed_boost_duration_timer / 60.0
        draw_text(px, py + 48, f'SPEED BOOST: {secs_left:.1f}s', color=(1.0, 0.85, 0.2), font=GLUT_BITMAP_HELVETICA_18)

  
    if cheat_mode:
        draw_text_bold(WIN_W - 220, WIN_H - 35, 'CHEAT MODE ON', color=(1.0, 0.85, 0.2), font=GLUT_BITMAP_HELVETICA_18)

   
    bar_w, bar_h = 380, 15
    bx = (WIN_W - bar_w) // 2
    by_name   = WIN_H - 24
    by_hp     = WIN_H - 45
    by_shield = WIN_H - 66

    draw_text_bold(WIN_W // 2 - 55, by_name, 'EVIL LARRY', color=(1.0, 0.25, 0.25), font=GLUT_BITMAP_HELVETICA_18)

   
    hp_pct = evil_larry_hp / EVIL_LARRY_MAX_HP
    draw_bar_2d(bx, by_hp, bar_w, bar_h, hp_pct, (1.0, 0.1, 0.1), border_color=(0.9, 0.9, 0.9))

    shield_pct = evil_larry_shield / EVIL_LARRY_MAX_SHIELD
    draw_bar_2d(bx, by_shield, bar_w, bar_h, shield_pct, (0.55, 0.54, 0.51), border_color=(0.9, 0.9, 0.9))


    if meow_timer > 0:
        draw_text_bold(WIN_W // 2 - 250, WIN_H // 2 + 55, 'MEOWWWWWWWWWWWW!!!!!!!!!!!!!!!!!!', color=(1.0, 0.15, 0.15), font=GLUT_BITMAP_HELVETICA_18)

   
    if is_paused:
        draw_text_bold(WIN_W // 2 - 120, WIN_H // 2 + 10, "=== GAME PAUSED ===", color=(1.0, 0.9, 0.1))
        draw_text(WIN_W // 2 - 100, WIN_H // 2 - 20, "Press 'P' to Resume Combat", color=(1.0, 1.0, 1.0))


    if is_game_over:
        draw_text_bold(WIN_W // 2 - 120, WIN_H // 2 + 25, 'MISSION FAILED!', color=(1.0, 0.1, 0.1), font=GLUT_BITMAP_HELVETICA_18)
        draw_text_bold(WIN_W // 2 - 85, WIN_H // 2 - 15, 'Press R to retry.', color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18)

    if is_level_cleared:
        draw_text_bold(WIN_W // 2 - 145, WIN_H // 2 + 35, 'CONGRATULATIONS!!!', color=(0.2, 1.0, 0.4), font=GLUT_BITMAP_HELVETICA_18)
        draw_text_bold(WIN_W // 2 - 340, WIN_H // 2 - 5, 'YOU HAVE DEFEATED EVIL LARRY AND SAVED THE WORLD!', color=(1.0, 0.85, 0.2), font=GLUT_BITMAP_HELVETICA_18)
        draw_text_bold(WIN_W // 2 - 105, WIN_H // 2 - 45, 'Press R to play again.', color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18)


def spawn_one_small_larry():
    global small_larrys_spawned_count
    if small_larrys_spawned_count >= TOTAL_SMALL_LARRY_ALLOWED or evil_larry_shield_broken:
        return
    angle = random.uniform(0, 2*math.pi)
    dist  = random.uniform(140.0, 460.0)
    sx = math.cos(angle) * dist
    sz = math.sin(angle) * dist
    small_larrys.append(SmallLarry(sx, sz))
    small_larrys_spawned_count += 1

def fire_weapon():
    global weapon_cooldown, arm_throw_timer

    if weapon_cooldown > 0 or is_game_over or is_level_cleared or is_paused:
        return

    weapon_cooldown = WEAPON_COOLDOWN_MAX
    arm_throw_timer = 14

    clamped_pitch = max(-10.0, min(25.0, player_pitch))
    rad = math.radians(player_yaw)
    rad_pitch = math.radians(clamped_pitch)

    bx = player_pos[0] + math.sin(rad) * 8.0 + math.cos(rad) * 6.0
    by = player_pos[1] + 16.0
    bz = player_pos[2] + math.cos(rad) * 8.0 - math.sin(rad) * 6.0

    throw_speed = 5.2
    vx = math.sin(rad) * math.cos(rad_pitch) * throw_speed
    vy = math.sin(rad_pitch) * throw_speed + 0.35
    vz = math.cos(rad) * math.cos(rad_pitch) * throw_speed

    if active_weapon == "gun":
        bombs.append(Bomb(bx, by, bz, vx, vy, vz))
    else:
        catnips.append(CatnipProjectile(bx, by, bz, vx, vy, vz))


def idle():
    global player_pos, is_jumping, y_velocity, player_speed, player_hits_left
    global arm_throw_timer, walk_anim_phase, is_moving
    global speed_boost_duration_timer, player_invulnerable_timer
    global evil_larry_pos, evil_larry_yaw, evil_larry_shield, evil_larry_hp
    global evil_larry_shield_broken, evil_larry_hit_flash, small_pillars_destroyed
    global weapon_cooldown, is_game_over, is_level_cleared, score, meow_timer
    global player_yaw, player_pitch, last_mouse_x, last_mouse_y, mouse_initialized

    if is_paused or is_game_over or is_level_cleared:
        glutPostRedisplay()
        return


    try:
        class _POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        _pt = _POINT()
        if ctypes.windll.user32.GetCursorPos(ctypes.byref(_pt)):
            if mouse_initialized:
                dx = _pt.x - last_mouse_x
                dy = _pt.y - last_mouse_y
                if dx != 0 or dy != 0:
                    mouse_sensitivity = 0.28
                    player_yaw = (player_yaw + dx * mouse_sensitivity) % 360.0
                    player_pitch = max(-65.0, min(65.0, player_pitch - dy * mouse_sensitivity))
            else:
                mouse_initialized = True
            last_mouse_x = _pt.x
            last_mouse_y = _pt.y
    except:
        pass


    if is_jumping:
        player_pos[1] += y_velocity
        y_velocity += gravity
        if player_pos[1] <= ground_y:
            player_pos[1] = ground_y
            is_jumping = False
            y_velocity = 0.0

    if speed_boost_duration_timer > 0:
        speed_boost_duration_timer -= 1

    if player_invulnerable_timer > 0:
        player_invulnerable_timer -= 1

    if evil_larry_hit_flash > 0:
        evil_larry_hit_flash -= 1

    if weapon_cooldown > 0:
        weapon_cooldown -= 1

    if arm_throw_timer > 0:
        arm_throw_timer -= 1

    if meow_timer > 0:
        meow_timer -= 1

    if not is_moving and abs(walk_anim_phase) > 0.01:
        walk_anim_phase *= 0.82
    is_moving = False


    for item in speedboost_items:
        item.update()
        if item.active:
            d = math.sqrt((player_pos[0]-item.x)**2 + (player_pos[2]-item.z)**2)
            if d < 18.0:
                item.active = False
                speed_boost_duration_timer = 360

    global hairball_timer
    if evil_larry_hp > 0:
        hairball_timer -= 1
        if hairball_timer <= 0:
            hairball_timer = HAIRBALL_COOLDOWN
            hairballs.append(Hairball(
                evil_larry_pos[0], 65.0, evil_larry_pos[2],
                player_pos[0], player_pos[2]
            ))

    for hb in list(hairballs):
        hb.update()
        if not hb.alive:
            hairballs.remove(hb)
            hairball_puddles.append(HairballPuddle(hb.x, hb.z))
            explosions.append(Explosion(hb.x, 2.0, hb.z, max_r=22.0))

    for pd in list(hairball_puddles):
        pd.update()
        if pd.life <= 0:
            hairball_puddles.remove(pd)
            continue
        d_puddle = math.sqrt((player_pos[0] - pd.x)**2 + (player_pos[2] - pd.z)**2)
        if d_puddle < pd.radius and player_invulnerable_timer <= 0 and not cheat_mode:
            player_hits_left -= 1
            player_invulnerable_timer = 50
            if player_hits_left <= 0:
                is_game_over = True


    global pounce_timer, pounce_state, pounce_sub_timer, pounce_target, pounce_start
    global pounce_shockwave_r, pounce_shockwave_life

    if pounce_shockwave_life > 0:
        pounce_shockwave_life -= 1
        pounce_shockwave_r += 2.4

    if evil_larry_hp > 0 and evil_larry_shield_broken:
        if pounce_state == 'IDLE':
            pounce_timer -= 1
            if pounce_timer <= 0:
                pounce_timer = POUNCE_COOLDOWN
                pounce_state = 'WINDUP'
                pounce_sub_timer = 36
                pounce_target = [player_pos[0], player_pos[2]]
                pounce_start = [evil_larry_pos[0], evil_larry_pos[2]]

        elif pounce_state == 'WINDUP':
            pounce_sub_timer -= 1
            if pounce_sub_timer <= 0:
                pounce_state = 'AIR'
                pounce_sub_timer = 65

        elif pounce_state == 'AIR':
            pounce_sub_timer -= 1
            prog = 1.0 - (pounce_sub_timer / 65.0)
            evil_larry_pos[0] = pounce_start[0] + (pounce_target[0] - pounce_start[0]) * prog
            evil_larry_pos[2] = pounce_start[1] + (pounce_target[1] - pounce_start[1]) * prog
            evil_larry_pos[1] = math.sin(prog * math.pi) * 120.0

            if pounce_sub_timer <= 0:
                evil_larry_pos[0] = pounce_target[0]
                evil_larry_pos[2] = pounce_target[1]
                evil_larry_pos[1] = 0.0
                pounce_state = 'IDLE'
                pounce_shockwave_r = 12.0
                pounce_shockwave_life = 25
                explosions.append(Explosion(pounce_target[0], 5.0, pounce_target[1], max_r=38.0))

                d_impact = math.sqrt((player_pos[0] - pounce_target[0])**2 + (player_pos[2] - pounce_target[1])**2)
                if d_impact < 48.0 and player_pos[1] < 12.0 and player_invulnerable_timer <= 0 and not cheat_mode:
                    player_hits_left -= 1
                    player_invulnerable_timer = 70
                    if player_hits_left <= 0:
                        is_game_over = True

    global boss_spherical_timer
    if evil_larry_hp > 0 and pounce_state == 'IDLE':
        boss_spherical_timer -= 1
        if boss_spherical_timer <= 0:
            boss_spherical_timer = random.randint(4 * 60, 5 * 60)
            boss_projectiles.append(BossProjectile(
                evil_larry_pos[0], evil_larry_pos[1] + 45.0, evil_larry_pos[2],
                player_pos[0], player_pos[1] + 16.0, player_pos[2]
            ))

    for bp in list(boss_projectiles):
        bp.update()
        if not bp.alive:
            boss_projectiles.remove(bp)
            continue
        d_p = math.sqrt((player_pos[0] - bp.x)**2 + (player_pos[2] - bp.z)**2)
        if d_p < (16.0 + bp.radius) and abs(player_pos[1] + 16.0 - bp.y) < 22.0:
            bp.alive = False
            boss_projectiles.remove(bp)
            explosions.append(Explosion(bp.x, bp.y, bp.z, max_r=16.0))
            if player_invulnerable_timer <= 0 and not cheat_mode:
                player_hits_left -= 1
                player_invulnerable_timer = 55
                if player_hits_left <= 0:
                    is_game_over = True


    if not evil_larry_shield_broken:
        while len([sl for sl in small_larrys if sl.alive]) < MAX_ACTIVE_SMALL_LARRY and small_larrys_spawned_count < TOTAL_SMALL_LARRY_ALLOWED:
            spawn_one_small_larry()

    for sl in list(small_larrys):
        if not sl.alive:
            continue

        sl.update(player_pos[0], player_pos[2], evil_larry_pos[0], evil_larry_pos[2])

    
        if sl.charmed:
            d_to_boss = math.sqrt((sl.x - evil_larry_pos[0])**2 + (sl.z - evil_larry_pos[2])**2)
            if d_to_boss < 38.0 and evil_larry_hp > 0:
                sl.alive = False
                evil_larry_hit_flash = 12
                explosions.append(Explosion(evil_larry_pos[0], 25.0, evil_larry_pos[2], max_r=28.0, is_blue=True))

                if evil_larry_shield > 0:
                    evil_larry_shield = max(0.0, evil_larry_shield - 60.0)
                    print(f">> Charmed Small Larry destroyed section of Big Larry's Shield! Shield remaining: {evil_larry_shield}")
                    if evil_larry_shield <= 0:
                        evil_larry_shield_broken = True
                        small_pillars_destroyed = True
                        meow_timer = 120
                        # All remaining Small Larries disappear when shield breaks!
                        for rem_sl in small_larrys:
                            if rem_sl.alive:
                                rem_sl.alive = False
                                explosions.append(Explosion(rem_sl.x, 10.0, rem_sl.z, max_r=20.0))
                        small_larrys.clear()
                        for k in range(INNER_COUNT):
                            ang = 2*math.pi * k / INNER_COUNT
                            px = INNER_RING_R * math.cos(ang)
                            pz = INNER_RING_R * math.sin(ang)
                            explosions.append(Explosion(px, 15.0, pz, max_r=18.0))
        else:
            if player_invulnerable_timer <= 0:
                d = math.sqrt((player_pos[0]-sl.x)**2 + (player_pos[2]-sl.z)**2)
                if d < 14.0:
                    if not cheat_mode:
                        player_hits_left -= 1
                        player_invulnerable_timer = 60
                        if player_hits_left <= 0:
                            is_game_over = True


    if evil_larry_shield_broken and len(small_larrys) > 0:
        for sl in small_larrys:
            if sl.alive:
                sl.alive = False
                explosions.append(Explosion(sl.x, 10.0, sl.z, max_r=20.0))
        small_larrys.clear()

    if evil_larry_hp > 0:
        dx = player_pos[0] - evil_larry_pos[0]
        dz = player_pos[2] - evil_larry_pos[2]
        dist_to_player = math.sqrt(dx*dx + dz*dz)
        if dist_to_player > 0.001:
            evil_larry_yaw = math.degrees(math.atan2(dx, dz))

        if evil_larry_shield_broken and dist_to_player > 20.0 and pounce_state == 'IDLE':
            nx = evil_larry_pos[0] + (dx / dist_to_player) * evil_larry_speed
            nz = evil_larry_pos[2] + (dz / dist_to_player) * evil_larry_speed
            evil_larry_pos[0], evil_larry_pos[2] = resolve_pillar_collisions(nx, nz)

        if dist_to_player < 30.0 and player_invulnerable_timer <= 0:
            if not cheat_mode:
                player_hits_left -= 1
                player_invulnerable_timer = 70
                if player_hits_left <= 0:
                    is_game_over = True
    for b in list(bombs):
        b.update()
        if not b.alive:
            bombs.remove(b)
            continue

        exploded = False
        if b.y <= 0.0:
            exploded = True
            explosions.append(Explosion(b.x, 2.0, b.z, max_r=16.0))

        if not exploded:
            for k in range(OUTER_COUNT):
                ang = 2 * math.pi * k / OUTER_COUNT
                px = OUTER_RING_R * math.cos(ang)
                pz = OUTER_RING_R * math.sin(ang)
                d = math.sqrt((b.x - px)**2 + (b.z - pz)**2)
                if d < (OUTER_BASE_R + 6.0) and b.y < OUTER_HEIGHT:
                    exploded = True
                    explosions.append(Explosion(b.x, b.y, b.z, max_r=16.0))
                    break

        if not exploded and not small_pillars_destroyed:
            for k in range(INNER_COUNT):
                ang = 2 * math.pi * k / INNER_COUNT
                px = INNER_RING_R * math.cos(ang)
                pz = INNER_RING_R * math.sin(ang)
                d = math.sqrt((b.x - px)**2 + (b.z - pz)**2)
                if d < (INNER_BASE_R + 6.0) and b.y < INNER_HEIGHT:
                    exploded = True
                    explosions.append(Explosion(b.x, b.y, b.z, max_r=16.0))
                    break

        if not exploded:
            d_boss = math.sqrt((b.x - evil_larry_pos[0])**2 + (b.z - evil_larry_pos[2])**2)
            if d_boss < 42.0 and b.y < 85.0 and evil_larry_hp > 0:
                exploded = True
                evil_larry_hit_flash = 8
                explosions.append(Explosion(b.x, b.y, b.z, max_r=22.0))

                if evil_larry_shield > 0:
                    evil_larry_shield = max(0.0, evil_larry_shield - BOMB_DAMAGE)
                    if evil_larry_shield <= 0:
                        evil_larry_shield_broken = True
                        small_pillars_destroyed = True
                        meow_timer = 120
                        # All remaining Small Larries disappear when shield breaks!
                        for rem_sl in small_larrys:
                            if rem_sl.alive:
                                rem_sl.alive = False
                                explosions.append(Explosion(rem_sl.x, 10.0, rem_sl.z, max_r=20.0))
                        small_larrys.clear()
                        for k in range(INNER_COUNT):
                            ang = 2*math.pi * k / INNER_COUNT
                            px = INNER_RING_R * math.cos(ang)
                            pz = INNER_RING_R * math.sin(ang)
                            explosions.append(Explosion(px, 15.0, pz, max_r=18.0))
                else:
                    evil_larry_hp = max(0.0, evil_larry_hp - BOMB_DAMAGE)
                    if evil_larry_hp <= 0:
                        is_level_cleared = True
                        for _ in range(8):
                            rx = evil_larry_pos[0] + random.uniform(-30, 30)
                            ry = random.uniform(10, 60)
                            rz = evil_larry_pos[2] + random.uniform(-30, 30)
                            explosions.append(Explosion(rx, ry, rz, max_r=30.0))

        if not exploded:
            for sl in small_larrys:
                if not sl.alive:
                    continue
                d_sl = math.sqrt((b.x - sl.x)**2 + (b.z - sl.z)**2)
                if d_sl < 16.0 and b.y < 30.0:
                    exploded = True
                    sl.hp -= 1
                    sl.hit_flash = 14
                    explosions.append(Explosion(b.x, b.y, b.z, max_r=16.0))
                    if sl.hp <= 0:
                        sl.alive = False
                        score += 1
                        explosions.append(Explosion(sl.x, 10.0, sl.z, max_r=24.0))
                        if not evil_larry_shield_broken and small_larrys_spawned_count < TOTAL_SMALL_LARRY_ALLOWED:
                            spawn_one_small_larry()
                    break

        if exploded and b in bombs:
            bombs.remove(b)

    for cn in list(catnips):
        cn.update()
        if not cn.alive:
            catnips.remove(cn)
            continue

        hit_event = False
        if cn.y <= 0.0:
            hit_event = True
            explosions.append(Explosion(cn.x, 2.0, cn.z, max_r=18.0, is_blue=True))

        if not hit_event:
            for sl in small_larrys:
                if not sl.alive or sl.charmed:
                    continue
                d_sl = math.sqrt((cn.x - sl.x)**2 + (cn.z - sl.z)**2)
                if d_sl < 24.0 and cn.y < 35.0:
                    hit_event = True
                    sl.charmed = True
                    explosions.append(Explosion(sl.x, 10.0, sl.z, max_r=22.0, is_blue=True))
                    print(">> Small Larry CHARMED by Catnip! Running towards Big Larry to destroy shield!")
                    break

        if hit_event and cn in catnips:
            catnips.remove(cn)

    # Explosions Update
    for exp in list(explosions):
        exp.update()
        if exp.life <= 0:
            explosions.remove(exp)

    glutPostRedisplay()


def setup_camera():
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55.0, WIN_W / float(WIN_H), 1.0, 3500.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    rad = math.radians(player_yaw)
    rad_pitch = math.radians(player_pitch)

    if first_person:
        eye_x = player_pos[0]
        eye_y = player_pos[1] + 12.0
        eye_z = player_pos[2]
        center_x = eye_x + math.sin(rad) * math.cos(rad_pitch) * 100.0
        center_y = eye_y + math.sin(rad_pitch) * 100.0
        center_z = eye_z + math.cos(rad) * math.cos(rad_pitch) * 100.0
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 1, 0)
    else:
        eye_x = player_pos[0] - math.sin(rad) * cam_dist
        eye_y = player_pos[1] + cam_height
        eye_z = player_pos[2] - math.cos(rad) * cam_dist
        center_x = eye_x + math.sin(rad) * math.cos(rad_pitch) * 100.0
        center_y = eye_y + math.sin(rad_pitch) * 100.0
        center_z = eye_z + math.cos(rad) * math.cos(rad_pitch) * 100.0
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 1, 0)

_user32 = ctypes.windll.user32

def update_window_dimensions():
    global WIN_W, WIN_H
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
                    WIN_W = w
                    WIN_H = h
    except:
        pass

def display():
    global WIN_W, WIN_H
    update_window_dimensions()

    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    setup_camera()


    draw_floor_occluder()
    draw_floor()
    draw_wall_rim_accent()
    draw_ceiling_rim()

    rad = math.radians(player_yaw)
    rad_pitch = math.radians(player_pitch)
    if first_person:
        cam_x = player_pos[0]
        cam_y = player_pos[1] + 12.0
        cam_z = player_pos[2]
    else:
        cam_x = player_pos[0] - math.sin(rad) * cam_dist
        cam_y = player_pos[1] + cam_height
        cam_z = player_pos[2] - math.cos(rad) * cam_dist

  
    render_list = []

    # Wall segments
    if _wall_cache is None:
        _build_wall()
    for rep, faces in _wall_cache:
        def _draw_seg(faces=faces):
            glBegin(GL_QUADS)
            for col, q in faces:
                glColor3f(*col)
                for v in q:
                    glVertex3f(*v)
            glEnd()
        render_list.append((rep[0], rep[1], rep[2], _draw_seg))

    for k in range(OUTER_COUNT):
        ang = 2 * math.pi * k / OUTER_COUNT
        px = OUTER_RING_R * math.cos(ang)
        pz = OUTER_RING_R * math.sin(ang)
        def _draw_lp(px=px, pz=pz):
            glPushMatrix()
            glTranslatef(px, 0, pz)
            glRotatef(-90, 1, 0, 0)
            draw_large_pillar()
            glPopMatrix()
        render_list.append((px, OUTER_HEIGHT * 0.5, pz, _draw_lp))


    if not small_pillars_destroyed:
        for k in range(INNER_COUNT):
            ang = 2 * math.pi * k / INNER_COUNT
            px = INNER_RING_R * math.cos(ang)
            pz = INNER_RING_R * math.sin(ang)
            def _draw_sp(px=px, pz=pz):
                glPushMatrix()
                glTranslatef(px, 0, pz)
                glRotatef(-90, 1, 0, 0)
                draw_small_pillar()
                glPopMatrix()
            render_list.append((px, INNER_HEIGHT * 0.5, pz, _draw_sp))

  
    for item in speedboost_items:
        if item.active:
            def _draw_sb(item=item):
                glPushMatrix()
                glTranslatef(item.x, item.y, item.z)
                glRotatef(item.rot, 0, 1, 0)
                glRotatef(30, 1, 0, 0)
                glColor3f(0.1, 0.95, 1.0)
                glutSolidCube(14)
                glPopMatrix()
            render_list.append((item.x, item.y, item.z, _draw_sb))

   
    if evil_larry_hp > 0:
        render_list.append((evil_larry_pos[0], evil_larry_pos[1] + 35.0, evil_larry_pos[2], draw_evil_larry_boss))

   
    if not first_person:
        render_list.append((player_pos[0], player_pos[1] + 16.0, player_pos[2], lambda: draw_tung_tung_sahur(cam_x, cam_z)))

    
    for sl in small_larrys:
        if sl.alive:
            def _draw_sl(sl=sl):
                draw_single_small_larry(sl)
            render_list.append((sl.x, sl.y + 10.0, sl.z, _draw_sl))


    for b in bombs:
        if b.alive:
            def _draw_bomb(b=b):
                glPushMatrix()
                glTranslatef(b.x, b.y, b.z)
                glRotatef(b.rot, 1, 1, 0)
                glColor3f(0.12, 0.12, 0.12)
                gluSphere(Q(), 4.0, 10, 10)
                glTranslatef(0.0, 4.0, 0.0)
                glColor3f(1.0, 0.55, 0.0)
                gluSphere(Q(), 1.4, 6, 6)
                glPopMatrix()
            render_list.append((b.x, b.y, b.z, _draw_bomb))


    for cn in catnips:
        if cn.alive:
            def _draw_cn(cn=cn):
                glPushMatrix()
                glTranslatef(cn.x, cn.y, cn.z)
                glRotatef(cn.rot, 1, 1, 0)
                glColor3f(0.0, 0.70, 1.0)
                glutSolidCube(5.0)
                glColor3f(0.3, 0.95, 1.0)
                gluSphere(Q(), 3.2, 8, 8)
                glPopMatrix()
            render_list.append((cn.x, cn.y, cn.z, _draw_cn))


    for exp in explosions:
        if exp.life > 0:
            def _draw_exp(exp=exp):
                glPushMatrix()
                glTranslatef(exp.x, exp.y, exp.z)
                alpha = exp.life / float(exp.max_life)
                if exp.is_blue:
                    glColor3f(0.1 * alpha, 0.85 * alpha, 1.0 * alpha)
                else:
                    glColor3f(1.0 * alpha, 0.45 * alpha, 0.05 * alpha)
                gluSphere(Q(), exp.radius, 10, 10)
                glPointSize(4)
                glBegin(GL_POINTS)
                for p in exp.particles:
                    if exp.is_blue:
                        glColor3f(0.4 * alpha, 0.95 * alpha, 1.0 * alpha)
                    else:
                        glColor3f(1.0, 0.85 * alpha, 0.2 * alpha)
                    glVertex3f(p[0], p[1], p[2])
                glEnd()
                glPopMatrix()
            render_list.append((exp.x, exp.y, exp.z, _draw_exp))

    for hb in hairballs:
        if hb.alive:
            def _draw_hb(hb=hb):
                glPushMatrix()
                glTranslatef(hb.x, hb.y, hb.z)
                glRotatef(hb.rot, 1, 1, 0)
                glColor3f(0.20, 0.85, 0.10)
                gluSphere(Q(), 9.5, 12, 12)
                glColor3f(0.35, 0.95, 0.15)
                gluSphere(Q(), 7.0, 8, 8)
                glPointSize(6)
                glBegin(GL_POINTS)
                for a in range(0, 360, 40):
                    rad_hb = math.radians(a + hb.rot)
                    glColor3f(0.40, 1.0, 0.20)
                    glVertex3f(math.cos(rad_hb) * 11.5, math.sin(rad_hb) * 11.5, 0)
                    glVertex3f(0, math.cos(rad_hb) * 11.5, math.sin(rad_hb) * 11.5)
                glEnd()
                glPopMatrix()
            render_list.append((hb.x, hb.y, hb.z, _draw_hb))


    for pd in hairball_puddles:
        if pd.life > 0:
            def _draw_pd(pd=pd):
                alpha = pd.life / float(pd.max_life)
                glBegin(GL_TRIANGLES)
                segs = 28
                for i in range(segs):
                    a1 = 2 * math.pi * i / segs
                    a2 = 2 * math.pi * (i + 1) / segs
                    glColor3f(0.20 * alpha, 0.75 * alpha, 0.12 * alpha)
                    glVertex3f(pd.x, 0.35, pd.z)
                    glColor3f(0.10 * alpha, 0.40 * alpha, 0.06 * alpha)
                    glVertex3f(pd.x + math.cos(a1) * pd.radius, 0.35, pd.z + math.sin(a1) * pd.radius)
                    glVertex3f(pd.x + math.cos(a2) * pd.radius, 0.35, pd.z + math.sin(a2) * pd.radius)
                glEnd()

                glPointSize(5)
                glBegin(GL_POINTS)
                glColor3f(0.45 * alpha, 1.0 * alpha, 0.25 * alpha)
                for b in pd.bubbles:
                    glVertex3f(pd.x + b[0], b[1], pd.z + b[2])
                glEnd()
            render_list.append((pd.x, 0.35, pd.z, _draw_pd))


    if pounce_state in ['WINDUP', 'AIR'] or pounce_shockwave_life > 0:
        render_list.append((pounce_target[0], 0.6, pounce_target[1], draw_pounce_effects))


    for bp in boss_projectiles:
        if bp.alive:
            def _draw_bp(bp=bp):
                glPushMatrix()
                glTranslatef(bp.x, bp.y, bp.z)
                glRotatef(bp.rot, 1, 0, 1)
                glColor3f(0.95, 0.20, 0.95)
                gluSphere(Q(), bp.radius, 12, 12)
                glColor3f(1.0, 0.85, 1.0)
                gluSphere(Q(), bp.radius * 0.55, 8, 8)
                glPointSize(4)
                glBegin(GL_POINTS)
                for a in range(0, 360, 60):
                    rad_bp = math.radians(a + bp.rot)
                    glColor3f(1.0, 0.5, 1.0)
                    glVertex3f(math.cos(rad_bp) * (bp.radius + 3.0), math.sin(rad_bp) * (bp.radius + 3.0), 0)
                glEnd()
                glPopMatrix()
            render_list.append((bp.x, bp.y, bp.z, _draw_bp))

   
    def _dist_sq(entity):
        ex, ey, ez, fn = entity
        return (ex - cam_x)**2 + (ey - cam_y)**2 + (ez - cam_z)**2

    render_list.sort(key=_dist_sq, reverse=True)

    for ex, ey, ez, fn in render_list:
        fn()

    # 4. 2D HUD & Crosshair
    draw_crosshair()
    draw_hud()

    glutSwapBuffers()

def keyboard_listener(key, x, y):
    global player_pos, crouching, is_jumping, y_velocity
    global first_person, is_paused, is_game_over, cheat_mode, active_weapon
    global walk_anim_phase, is_moving, player_yaw, player_pitch

    try:
        raw_ch = key.decode('utf-8')
    except:
        raw_ch = str(key)
    ch = raw_ch.lower()

    rad = math.radians(player_yaw)

    is_sprint = raw_ch in ['W', 'A', 'S', 'D']

    if speed_boost_duration_timer > 0:
        cur_speed = BASE_PLAYER_SPEED * 2.2
    elif is_sprint:
        cur_speed = BASE_PLAYER_SPEED * 1.70
    else:
        cur_speed = BASE_PLAYER_SPEED

    if not is_paused and not is_game_over and not is_level_cleared:
        nx, nz = player_pos[0], player_pos[2]
        moved = False

        if ch == 'w':
            nx += math.sin(rad) * cur_speed
            nz += math.cos(rad) * cur_speed
            moved = True
        elif ch == 's':
            nx -= math.sin(rad) * cur_speed
            nz -= math.cos(rad) * cur_speed
            moved = True
        elif ch == 'a':
            nx += math.sin(rad + math.pi/2.0) * cur_speed
            nz += math.cos(rad + math.pi/2.0) * cur_speed
            moved = True
        elif ch == 'd':
            nx += math.sin(rad - math.pi/2.0) * cur_speed
            nz += math.cos(rad - math.pi/2.0) * cur_speed
            moved = True
        elif ch == 'c':
            cheat_mode = not cheat_mode
            print('>> Cheat Mode: ON' if cheat_mode else '>> Cheat Mode: OFF')
        elif ch == ' ' or key == b' ':
            if not is_jumping:
                is_jumping = True
                y_velocity = jump_strength
        elif ch == 'f':
            active_weapon = "catnip" if active_weapon == "gun" else "gun"
            print(f">> Active Weapon Toggled to: {active_weapon.upper()}")
        elif ch == 'b':
            fire_weapon()
        elif ch == 'v':
            first_person = not first_person
        elif ch == 'j':
            player_yaw -= 5.0
        elif ch == 'l':
            player_yaw += 5.0
        elif ch == 'i':
            player_pitch = min(65.0, player_pitch + 5.0)
        elif ch == 'k':
            player_pitch = max(-65.0, player_pitch - 5.0)

        if moved:
            player_pos[0], player_pos[2] = resolve_pillar_collisions(nx, nz)
            walk_anim_phase += 0.28 * (cur_speed / BASE_PLAYER_SPEED)
            is_moving = True


    if ch == 'p':
        is_paused = not is_paused
    elif ch == 'r':
        reset_level_3()
    elif key == b'\x1b' or ch == 'q':
        sys.exit(0)

    limit = ARENA_RADIUS - 30.0
    r = math.sqrt(player_pos[0]**2 + player_pos[2]**2)
    if r > limit:
        player_pos[0] = (player_pos[0] / r) * limit
        player_pos[2] = (player_pos[2] / r) * limit

    glutPostRedisplay()

def special_key_listener(key, x, y):
    pass

def mouse_listener(button, state, x, y):
    if is_paused or is_game_over or is_level_cleared:
        return
    try:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            fire_weapon()
        elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            global first_person
            first_person = not first_person
            glutPostRedisplay()
    except Exception as e:
        print(f"Mouse event error: {e}")


def reset_level_3():
    global player_pos, player_yaw, player_pitch, player_hits_left
    global evil_larry_pos, evil_larry_yaw, evil_larry_shield, evil_larry_hp
    global evil_larry_shield_broken, evil_larry_hit_flash, small_pillars_destroyed
    global small_larrys_spawned_count, small_larrys, bombs, catnips, explosions
    global speed_boost_duration_timer, is_game_over, is_level_cleared, is_paused, score
    global hairball_timer, hairballs, hairball_puddles
    global pounce_timer, pounce_state, pounce_sub_timer, pounce_shockwave_life
    global boss_spherical_timer, boss_projectiles, meow_timer, active_weapon

    player_pos   = [0.0, 0.0, -320.0]
    player_yaw   = 0.0
    player_pitch = 0.0
    player_hits_left = MAX_PLAYER_HITS
    active_weapon = "gun"

    evil_larry_pos           = [0.0, 0.0, 0.0]
    evil_larry_yaw           = 180.0
    evil_larry_shield        = EVIL_LARRY_MAX_SHIELD
    evil_larry_hp            = EVIL_LARRY_MAX_HP
    evil_larry_shield_broken = False
    evil_larry_hit_flash     = 0
    small_pillars_destroyed  = False
    meow_timer               = 0

    small_larrys_spawned_count = 0
    small_larrys.clear()
    bombs.clear()
    catnips.clear()
    explosions.clear()

    hairball_timer = HAIRBALL_COOLDOWN
    hairballs.clear()
    hairball_puddles.clear()

    pounce_timer = POUNCE_COOLDOWN
    pounce_state = 'IDLE'
    pounce_sub_timer = 0
    pounce_shockwave_life = 0

    boss_spherical_timer = random.randint(4 * 60, 5 * 60)
    boss_projectiles.clear()

    speed_boost_duration_timer = 0
    is_game_over     = False
    is_level_cleared = False
    is_paused        = False
    score            = 0

    for item in speedboost_items:
        item.active = True
        item.respawn_timer = 0

    for _ in range(MAX_ACTIVE_SMALL_LARRY):
        spawn_one_small_larry()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(60, 40)
    glutCreateWindow(b"9 Lives - Level 3: Boss Fight (Evil Larry)")

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)

    reset_level_3()
    glutMainLoop()

if __name__ == "__main__":
    main()