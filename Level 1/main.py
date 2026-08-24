"""
===============================================================================
"9 Lives" - Level 1: Foundations of Movement (Fully Connected Maze Arena)
===============================================================================
Main Character: "tung tung tung sahur"
Course: CSE423 Computer Graphics Project

Design Theme:
- Expansive 3D Backrooms Labyrinth Walkway with 100% SEAMLESS CONNECTED ROOMS & PATHWAYS
- Unbroken continuous walls and solid floor pathways linking every corner turn, 
  room entrance, and feature chamber from Start Hub to Exit Gateway.
- Connected Progression Route:
  [Start Hub (Z: 0->60)] ==> [Corner A (Z: 60)] ==> [Hazard Pits (Z: 60->120)]
  ==> [Long Backrooms Corridor B (Z: 120)] ==> [Disappearing Floor Void (Z: 120->180)]
  ==> [Corridor C (Z: 180)] ==> [Laser Gauntlet (Z: 180->240)]
  ==> [Corridor D (Z: 240)] ==> [Moving Walls (Z: 240->300)] ==> [Exit Portal (Z: 330)]

Controls:
- W / S / Up / Down     : Move Forward / Backward
- A / D                 : Strafe Left / Right
- Left / Right Arrows   : Turn Character / Camera Yaw
- Spacebar              : Jump (Smooth velocity + gravity)
- C / Left Ctrl         : Crouch (Hitbox drops to 0.8 units)
- V / Right-Click       : Toggle Camera View (1st Person POV <-> 3rd Person Follow)
- M                     : Toggle Moving Wall Shift Demo
- T                     : Toggle Disappearing Platform Flash Demo
- R                     : Reset Player Position to Start Hub
- ESC                   : Exit Game
===============================================================================
"""

import math
import random
import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# -----------------------------------------------------------------------------
# Global Configurations & Window Settings
# -----------------------------------------------------------------------------
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750
WINDOW_TITLE = b"9 Lives - Level 1: Connected Backrooms Maze Arena ('tung tung tung sahur')"

# -----------------------------------------------------------------------------
# Player & Physics State
# -----------------------------------------------------------------------------
player_pos = [0.0, 1.0, 5.0]     # X, Y, Z coordinates
player_yaw = 0.0                  # Character facing angle in degrees
player_pitch = 0.0                # Pitch angle looking up/down
player_speed = 0.45               # Movement speed factor
crouching = False                 # Crouch state
eye_height = 1.6                  # Standing eye height

# Jump Physics Parameters
is_jumping = False
y_velocity = 0.0
gravity = -0.018
jump_strength = 0.38
ground_y = 1.0                    # Floor level Y height

first_person = False              # FPS (True) vs Third-Person Follow (False)
cam_dist = 6.5                    # Distance behind player in 3rd person
cam_height = 3.8                  # Height above player in 3rd person

# Interactive Scaffolding Demo Toggles
moving_walls_offset = 0.0         # Current shift for moving walls
moving_walls_dir = 1.0
anim_moving_walls = True

platform_timer = 0
disappearing_tiles_active = [True, True, True, True, True, True]
anim_disappearing_floor = True

# Game Pause State
game_paused = False

# Lava Pit 3-Strike Tracking
consecutive_lava_falls = 0
lava_alert_timer = 0           # frames to show lava alert message
game_over = False

# -----------------------------------------------------------------------------
# Color Palettes
# -----------------------------------------------------------------------------
COLOR_FLOOR = (0.10, 0.12, 0.15)       # Dark Slate Floor Tiles
COLOR_FLOOR_SIDE = (0.06, 0.07, 0.09)
COLOR_WALL = (0.32, 0.33, 0.28)        # Backrooms Desaturated Slate Wall
COLOR_WALL_SIDE = (0.22, 0.23, 0.20)
COLOR_CEILING = (0.12, 0.13, 0.15)
COLOR_LIGHT_PANEL = (0.95, 0.95, 0.75) # Fluorescent Overhead Light Panels

COLOR_RUNNER = (0.75, 0.08, 0.12)      # Deep Red Carpet
COLOR_GOLD_TRIM = (0.90, 0.75, 0.15)   # Gold Edge Trim
COLOR_PILLAR = (0.16, 0.16, 0.20)      # Dark Charcoal Pillars
COLOR_CYAN_GLOW = (0.0, 0.85, 1.0)     # Neon Cyan Accent Caps
COLOR_LAVA = (1.0, 0.25, 0.0)          # Fiery Orange Lava Pit
COLOR_HAZARD_STRIPE = (0.95, 0.85, 0.1)# Warning Yellow
COLOR_LASER_RED = (1.0, 0.1, 0.2)      # Laser Red
COLOR_LASER_CYAN = (0.0, 0.9, 1.0)     # Laser Cyan
COLOR_PORTAL_CYAN = (0.0, 0.75, 1.0)   # Exit Portal Ring

# Character Palette ("tung tung tung sahur")
c_body = (222/255, 137/255, 34/255)
c_dark = (117/255, 76/255, 18/255)
c_goggle = (229/255, 230/255, 230/255)
c_white = (1.0, 1.0, 1.0)

def load_character_model():
    """Initializes palette for 'tung tung tung sahur'."""
    global c_body, c_dark, c_goggle, c_white
    c_body = (222/255, 137/255, 34/255)
    c_dark = (117/255, 76/255, 18/255)
    c_goggle = (229/255, 230/255, 230/255)
    c_white = (1.0, 1.0, 1.0)

# -----------------------------------------------------------------------------
# 3D Helper Primitives & Text Rendering
# -----------------------------------------------------------------------------
def draw_box(sx, sy, sz, color_top=None, color_side=None):
    """
    Draws a solid box centered at origin with dimensions sx, sy, sz.
    """
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    glBegin(GL_QUADS)
    
    # Top Face (Y+)
    if color_top:
        glColor3f(*color_top)
    glVertex3f(-hx, hy, hz); glVertex3f(hx, hy, hz); glVertex3f(hx, hy, -hz); glVertex3f(-hx, hy, -hz)
    
    # Bottom Face (Y-)
    glVertex3f(-hx, -hy, -hz); glVertex3f(hx, -hy, -hz); glVertex3f(hx, -hy, hz); glVertex3f(-hx, -hy, hz)
    
    # Front Face (Z+)
    if color_side:
        glColor3f(color_side[0] * 0.9, color_side[1] * 0.9, color_side[2] * 0.9)
    glVertex3f(-hx, -hy, hz); glVertex3f(hx, -hy, hz); glVertex3f(hx, hy, hz); glVertex3f(-hx, hy, hz)
    
    # Back Face (Z-)
    if color_side:
        glColor3f(color_side[0] * 0.85, color_side[1] * 0.85, color_side[2] * 0.85)
    glVertex3f(-hx, hy, -hz); glVertex3f(hx, hy, -hz); glVertex3f(hx, -hy, -hz); glVertex3f(-hx, -hy, -hz)
    
    # Left Face (X-)
    if color_side:
        glColor3f(color_side[0] * 0.8, color_side[1] * 0.8, color_side[2] * 0.8)
    glVertex3f(-hx, -hy, -hz); glVertex3f(-hx, -hy, hz); glVertex3f(-hx, hy, hz); glVertex3f(-hx, hy, -hz)
    
    # Right Face (X+)
    if color_side:
        glColor3f(color_side[0] * 0.85, color_side[1] * 0.85, color_side[2] * 0.85)
    glVertex3f(hx, -hy, -hz); glVertex3f(hx, hy, -hz); glVertex3f(hx, hy, hz); glVertex3f(hx, -hy, hz)
    
    glEnd()

def draw_text(x, y, text_str):
    """
    Renders 2D HUD text using GLUT_BITMAP_HELVETICA_18.
    """
    glColor3f(1.0, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# -----------------------------------------------------------------------------
# Character Rendering: "tung tung tung sahur"
# -----------------------------------------------------------------------------
def draw_character():
    """
    Renders 3D character model for 'tung tung tung sahur' at player coordinates.
    """
    if first_person:
        return

    glPushMatrix()
    curr_y = player_pos[1]
    glTranslatef(player_pos[0], curr_y, player_pos[2])
    glRotatef(player_yaw, 0, 1, 0)

    # Align model Z (height) -> World Y, model Y (front) -> World Z
    glRotatef(-90, 1, 0, 0)
    glRotatef(180, 0, 0, 1)

    scale_factor = 0.008
    if crouching:
        glScalef(scale_factor, scale_factor * 0.5, scale_factor)
    else:
        glScalef(scale_factor, scale_factor, scale_factor)

    # Main Body
    glPushMatrix()
    glColor3f(*c_body)
    glTranslatef(0, 0, 120)
    glScalef(0.65, 0.4, 1.8)
    glutSolidCube(100)
    glPopMatrix()

    # Goggles & Eyes (Left/Right)
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

        # Eyebrow
        glPushMatrix()
        glColor3f(*c_dark)
        glTranslatef(eye_x, 22, 185)
        glScalef(0.25, 0.06, 0.06)
        glutSolidCube(100)
        glPopMatrix()

    # Nose & Smirk
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

    # Arms & Legs
    for side_x in [-38.5, 38.5]:
        glPushMatrix()
        glColor3f(*c_body)
        glTranslatef(side_x, 0, 95)
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

    glPopMatrix()

# -----------------------------------------------------------------------------
# 100% CONNECTED MAZE PATHWAYS & WALLS
# -----------------------------------------------------------------------------
def draw_connected_floor_pathways():
    """
    Draws a 100% fully connected solid floor mesh across all rooms, turns, and corridors.
    """
    # 1. Start Hub & Main Hallway (X: -6 to +6, Z: 0 to 60)
    glPushMatrix()
    glTranslatef(0.0, -0.1, 30.0)
    draw_box(12.0, 0.2, 60.0, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # Red Carpet Runner in Start Hub
    glPushMatrix()
    glTranslatef(0.0, 0.02, 20.0)
    draw_box(3.6, 0.04, 40.0, color_top=COLOR_RUNNER, color_side=(0.4, 0.04, 0.06))
    glPopMatrix()

    glColor3f(*COLOR_GOLD_TRIM)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex3f(-1.8, 0.05, 0.0); glVertex3f(-1.8, 0.05, 40.0)
    glVertex3f(1.8, 0.05, 0.0); glVertex3f(1.8, 0.05, 40.0)
    glEnd()

    # 2. Seamless Connection Junction A -> Hazard Corridor (X: 0 -> 45.6, Z: 54.4 -> 65.6)
    glPushMatrix()
    glTranslatef(20.0, -0.1, 60.0)
    draw_box(45.6, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 3. Hazard Corridor: entire floor is lava — NO solid floor tiles here.
    #    draw_hazard_zones() renders the lava + rock slabs instead.

    # 4. Seamless Connection Junction B -> Long Backrooms Corridor B (X: -45.6 -> +45.6, Z: 114.4 -> 125.6)
    glPushMatrix()
    glTranslatef(0.0, -0.1, 120.0)
    draw_box(91.2, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 5. Disappearing Floor Entry & Exit Connected Ledges (X: -45.6 -> -34.4, Z: 120 -> 180)
    glPushMatrix()
    glTranslatef(-40.0, -0.1, 128.0)
    draw_box(11.2, 0.2, 16.0, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-40.0, -0.1, 172.0)
    draw_box(11.2, 0.2, 16.0, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 6. Seamless Connection Junction C -> Corridor C (X: -45.6 -> 25.6, Z: 174.4 -> 185.6)
    glPushMatrix()
    glTranslatef(-10.0, -0.1, 180.0)
    draw_box(71.2, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 7. Laser Gauntlet Corridor Floor (X: 14.4 -> 25.6, Z: 180 -> 240)
    glPushMatrix()
    glTranslatef(20.0, -0.1, 210.0)
    draw_box(11.2, 0.2, 60.0, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 8. Seamless Connection Junction D -> Corridor D (X: 14.4 -> 75.6, Z: 234.4 -> 245.6)
    glPushMatrix()
    glTranslatef(45.0, -0.1, 240.0)
    draw_box(61.2, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 9. Moving Walls & Exit Chamber Floor (X: 64.4 -> 75.6, Z: 240 -> 340)
    glPushMatrix()
    glTranslatef(70.0, -0.1, 290.0)
    draw_box(11.2, 0.2, 100.0, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

def draw_connected_walls():
    """
    Renders 100% unbroken, fully connected walls around the entire maze layout.
    Every corner joint overlaps perfectly with zero gaps!
    """
    def wall(cx, cy, cz, sx, sy, sz):
        glPushMatrix()
        glTranslatef(cx, cy, cz)
        draw_box(sx, sy, sz, color_top=COLOR_WALL, color_side=COLOR_WALL_SIDE)
        glPopMatrix()

    # South Wall of Start Hub (Z = -0.4)
    wall(0.0, 3.5, -0.4, 13.6, 7.0, 0.8)

    # 1. Start Hub West & East Walls (Z: 0 -> 54.4)
    wall(-6.4, 3.5, 27.0, 0.8, 7.0, 54.8)
    wall(6.4, 3.5, 27.0, 0.8, 7.0, 54.8)

    # 2. Turn 1 Junction Walls (Connected to Corridor A)
    wall(-6.4, 3.5, 60.0, 0.8, 7.0, 12.0)            # West end cap of Junction A
    wall(13.8, 3.5, 65.6, 41.2, 7.0, 0.8)           # North Wall (X: -6.4 -> 34.4, clear entry to Zone 2 at X: 34.4->45.6)
    wall(20.4, 3.5, 54.4, 28.8, 7.0, 0.8)           # South Wall (X: 6.4 -> 34.8)

    # 3. Hazard Pit Corridor Walls (Z: 60 -> 120)
    wall(34.4, 3.5, 90.2, 0.8, 7.0, 49.2)           # West Wall (Z: 65.6 -> 114.8, clear walkway from Junction A)
    wall(45.6, 3.5, 92.8, 0.8, 7.0, 54.4)           # East Wall

    # 4. Turn 2 Junction Walls (Connected to Long Backrooms Corridor B)
    wall(45.6, 3.5, 120.0, 0.8, 7.0, 12.0)          # East end cap of Junction B
    wall(5.8, 3.5, 125.6, 80.4, 7.0, 0.8)           # North Wall (X: -34.4 -> +46.0, clear entry to Zone 3 at X: -45.6->-34.4)
    wall(0.0, 3.5, 114.4, 69.6, 7.0, 0.8)           # South Wall (X: -34.8 -> +34.8)

    # 5. Disappearing Chamber Walls (Z: 120 -> 180)
    wall(-45.6, 3.5, 150.0, 0.8, 7.0, 62.0)          # West Wall (X: -45.6)
    wall(-34.4, 3.5, 147.2, 0.8, 7.0, 56.0)          # East Wall (X: -34.4)

    # 6. Turn 3 Junction Walls (Connected to Corridor C)
    wall(-45.6, 3.5, 180.0, 0.8, 7.0, 12.0)          # West end cap of Junction C
    wall(-15.8, 3.5, 185.6, 60.4, 7.0, 0.8)          # North Wall (X: -46.0 -> 14.4, clear entry to Zone 4 at X: 14.4->25.6)
    wall(-10.0, 3.5, 174.4, 50.0, 7.0, 0.8)          # South Wall (X: -34.4 -> 15.6)

    # 7. Laser Gauntlet Corridor Walls (Z: 180 -> 240)
    wall(14.4, 3.5, 210.0, 0.8, 7.0, 50.0)           # West Wall
    wall(25.6, 3.5, 210.0, 0.8, 7.0, 62.0)           # East Wall

    # 8. Turn 4 Junction Walls (Connected to Corridor D)
    wall(50.8, 3.5, 234.4, 50.4, 7.0, 0.8)          # South Wall (X: 25.6 -> 76.0, clear walkway at X: 14.4->25.6)
    wall(45.0, 3.5, 245.6, 40.0, 7.0, 0.8)          # North Wall (X: 25.6 -> 65.6)

    # 9. Moving Walls & Exit Chamber Walls (Z: 240 -> 340)
    wall(64.4, 3.5, 292.8, 0.8, 7.0, 95.2)          # West Wall
    wall(75.6, 3.5, 287.2, 0.8, 7.0, 106.4)         # East Wall
    wall(70.0, 3.5, 340.4, 12.0, 7.0, 0.8)          # North Back Wall (End of Level 1)

    # Fluorescent Overhead Light Panels
    light_coords = [
        (0.0, 15.0), (0.0, 45.0),
        (20.0, 60.0), (40.0, 75.0), (40.0, 105.0),
        (20.0, 120.0), (-20.0, 120.0), (-40.0, 135.0), (-40.0, 165.0),
        (-10.0, 180.0), (20.0, 195.0), (20.0, 225.0),
        (45.0, 240.0), (70.0, 260.0), (70.0, 290.0), (70.0, 320.0)
    ]
    for lx, lz in light_coords:
        glPushMatrix()
        glTranslatef(lx, 6.9, lz)
        draw_box(3.0, 0.1, 4.0, color_top=COLOR_LIGHT_PANEL, color_side=(0.7, 0.7, 0.5))
        glPopMatrix()

def draw_pillars_and_archways():
    """
    Draws dark charcoal vertical pillars with cyan glowing caps at key maze turns.
    """
    pillars = [
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
    
    for px, pz in pillars:
        glPushMatrix()
        glTranslatef(px, 3.5, pz)
        draw_box(1.4, 7.0, 1.4, color_top=COLOR_PILLAR, color_side=(0.12, 0.12, 0.14))
        glPopMatrix()

        glPushMatrix()
        glTranslatef(px, 6.2, pz)
        draw_box(1.6, 0.4, 1.6, color_top=COLOR_CYAN_GLOW, color_side=(0.0, 0.6, 0.8))
        glPopMatrix()

def draw_hazard_zones():
    """
    Draws Section 2 (X: 34.4->45.6, Z: 65.6->114.4): Dark Obsidian & Lava Tile Corridor.
    Designed with a dark atmospheric palette matching 'UPDATE 1.1: WITH LAVA TILES':
    - Deep glowing molten lava channels beneath dark basalt crust tiles
    - Stepping stones formed by raised dark obsidian block islands with magma-filled tile grooves
    - Dark stone wall ledges with glowing lava seams along the corridor edges
    """

    CX   = 40.0        # corridor X centre
    CXHW = 5.6         # corridor X half-width (34.4 to 45.6)
    ZSTART = 65.6
    ZEND   = 114.4
    ZDEPTH = ZEND - ZSTART   # ~48.8 units
    ZCZ    = (ZSTART + ZEND) / 2.0  # centre Z

    # -----------------------------------------------------------------
    # 1. DEEP RECESSED PIT & MOLTEN LAVA BASE
    # -----------------------------------------------------------------
    # Pitch dark abyss pit body
    glPushMatrix()
    glTranslatef(CX, -2.2, ZCZ)
    draw_box(CXHW * 2, 4.4, ZDEPTH, color_top=(0.02, 0.01, 0.02), color_side=(0.06, 0.02, 0.03))
    glPopMatrix()

    # Deep fiery crimson base lava
    glPushMatrix()
    glTranslatef(CX, 0.0, ZCZ)
    draw_box(CXHW * 2, 0.06, ZDEPTH, color_top=(0.75, 0.04, 0.0), color_side=(0.50, 0.02, 0.0))
    glPopMatrix()

    # Bright molten orange-yellow glow channels
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

    # -----------------------------------------------------------------
    # 2. FLOOR LAVA TILES GRID (Scattered dark basalt crust tiles)
    # -----------------------------------------------------------------
    # Renders a grid of dark lava crust tiles with glowing magma gaps
    for z_tile in range(int(ZSTART) + 2, int(ZEND) - 2, 3):
        for x_off in [-3.8, -1.9, 0.0, 1.9, 3.8]:
            glPushMatrix()
            glTranslatef(CX + x_off, 0.15, float(z_tile))
            # Dark volcanic crust tile top with fiery underside glow
            draw_box(1.5, 0.08, 2.2,
                     color_top=(0.14, 0.11, 0.12),
                     color_side=(0.75, 0.20, 0.0))
            glPopMatrix()

    # -----------------------------------------------------------------
    # 3. BASALT SIDE WALL LEDGES WITH MAGMA SEAMS
    # -----------------------------------------------------------------
    for z_side in range(int(ZSTART), int(ZEND), 6):
        # Left wall basalt ledge block
        glPushMatrix()
        glTranslatef(CX - CXHW + 0.6, 0.5, float(z_side) + 3.0)
        draw_box(1.2, 1.2, 5.6, color_top=(0.16, 0.14, 0.16), color_side=(0.10, 0.08, 0.10))
        glPopMatrix()
        # Left magma seam
        glPushMatrix()
        glTranslatef(CX - CXHW + 0.6, 0.1, float(z_side) + 3.0)
        draw_box(1.3, 0.1, 5.6, color_top=(1.0, 0.30, 0.0), color_side=(0.8, 0.15, 0.0))
        glPopMatrix()

        # Right wall basalt ledge block
        glPushMatrix()
        glTranslatef(CX + CXHW - 0.6, 0.5, float(z_side) + 3.0)
        draw_box(1.2, 1.2, 5.6, color_top=(0.16, 0.14, 0.16), color_side=(0.10, 0.08, 0.10))
        glPopMatrix()
        # Right magma seam
        glPushMatrix()
        glTranslatef(CX + CXHW - 0.6, 0.1, float(z_side) + 3.0)
        draw_box(1.3, 0.1, 5.6, color_top=(1.0, 0.30, 0.0), color_side=(0.8, 0.15, 0.0))
        glPopMatrix()

    # -----------------------------------------------------------------
    # 4. LAVA TILE STEPPING STONE ISLANDS (8 Rocks)
    # Renders dark obsidian platforms with 3D lava-tile grid tops!
    # -----------------------------------------------------------------
    def draw_lava_tile_rock(rx, rz, sx, sz, tilt=0.0):
        """
        Draws a dark obsidian stepping stone island with magma-filled
        tile grooves on top (matching the reference image).
        """
        # A. Dark Obsidian Base Structure
        glPushMatrix()
        glTranslatef(rx, 1.0, rz)
        if tilt != 0.0:
            glRotatef(tilt, 0, 1, 0)
        draw_box(sx, 0.50, sz,
                 color_top=(0.12, 0.10, 0.13),
                 color_side=(0.07, 0.05, 0.08))
        glPopMatrix()

        # B. Magma Underglow Base Rim
        glPushMatrix()
        glTranslatef(rx, 0.76, rz)
        if tilt != 0.0:
            glRotatef(tilt, 0, 1, 0)
        draw_box(sx + 0.25, 0.08, sz + 0.25,
                 color_top=(1.0, 0.30, 0.0),
                 color_side=(0.85, 0.15, 0.0))
        glPopMatrix()

        # C. Glowing Magma Sub-Layer on Rock Surface
        glPushMatrix()
        glTranslatef(rx, 1.26, rz)
        if tilt != 0.0:
            glRotatef(tilt, 0, 1, 0)
        draw_box(sx - 0.1, 0.04, sz - 0.1,
                 color_top=(1.0, 0.55, 0.0),
                 color_side=(0.9, 0.30, 0.0))
        glPopMatrix()

        # D. 2x3 Grid of Dark Basalt Lava Tiles on top (Magma glows in the grooves!)
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

    # --- 8 Lava Tile Rock Islands ---
    draw_lava_tile_rock(40.0,  68.0,  3.6, 4.2, tilt= 0.0)   # R1 — entry (centre)
    draw_lava_tile_rock(38.8,  74.3,  3.6, 4.2, tilt= 6.0)   # R2 — left
    draw_lava_tile_rock(41.2,  80.6,  3.6, 4.2, tilt=-6.0)   # R3 — right
    draw_lava_tile_rock(38.8,  86.9,  3.6, 4.2, tilt= 5.0)   # R4 — left
    draw_lava_tile_rock(41.2,  93.2,  3.6, 4.2, tilt=-5.0)   # R5 — right
    draw_lava_tile_rock(38.8,  99.5,  3.6, 4.2, tilt= 6.0)   # R6 — left
    draw_lava_tile_rock(41.2, 105.8,  3.6, 4.2, tilt=-6.0)   # R7 — right
    draw_lava_tile_rock(40.0, 112.0,  3.6, 4.2, tilt= 0.0)   # R8 — exit (centre)

    # Warning stripes at corridor entry and exit
    for pz in [65.8, 114.2]:
        glPushMatrix()
        glTranslatef(CX, 0.04, pz)
        draw_box(CXHW * 2, 0.04, 0.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.6, 0.5, 0.0))
        glPopMatrix()

def draw_disappearing_platforms():
    """
    Draws Section 3 (X: -40, Z: 120 -> 180): Deep abyss gap bridged by color-coded platform tiles.
    """
    glPushMatrix()
    glTranslatef(-40.0, -4.0, 150.0)
    draw_box(17.0, 0.2, 32.0, color_top=(0.02, 0.01, 0.05), color_side=(0.01, 0.0, 0.02))
    glPopMatrix()

    platform_coords = [
        (-43.5, 138.0, 0), (-40.0, 138.0, 1), (-36.5, 138.0, 2),
        (-43.5, 146.0, 3), (-40.0, 146.0, 4), (-36.5, 146.0, 5),
        (-43.5, 154.0, 0), (-40.0, 154.0, 2), (-36.5, 154.0, 4),
        (-43.5, 162.0, 1), (-40.0, 162.0, 3), (-36.5, 162.0, 5)
    ]

    tile_colors = [
        (0.95, 0.45, 0.05), (0.05, 0.85, 0.95), (0.15, 0.90, 0.35),
        (0.90, 0.15, 0.90), (0.95, 0.85, 0.10), (0.10, 0.55, 0.95)
    ]

    for px, pz, color_idx in platform_coords:
        is_active = disappearing_tiles_active[color_idx]
        glPushMatrix()
        glTranslatef(px, 0.0, pz)
        
        if is_active:
            draw_box(2.8, 0.4, 4.0, color_top=tile_colors[color_idx], color_side=(0.15, 0.15, 0.18))
            glPushMatrix()
            glTranslatef(0.0, -0.25, 0.0)
            draw_box(2.4, 0.1, 3.6, color_top=(1.0, 1.0, 1.0), color_side=(0.5, 0.5, 0.5))
            glPopMatrix()
        else:
            glColor3f(0.3, 0.3, 0.35)
            glLineWidth(1.5)
            glBegin(GL_LINES)
            for dx in [-1.4, 1.4]:
                for dz in [-2.0, 2.0]:
                    glVertex3f(dx, -0.2, dz)
                    glVertex3f(dx, 0.2, dz)
            glEnd()
            
        glPopMatrix()

def draw_laser_emitters():
    """
    Draws Section 4 (X: 20, Z: 180 -> 240): Crouch & Jump horizontal laser beams.
    """
    laser_data = [
        (198.0, 2.2, COLOR_LASER_RED, "High Laser - Crouch Under"),
        (210.0, 0.7, COLOR_LASER_CYAN, "Low Laser - Jump Over"),
        (222.0, 1.5, COLOR_LASER_RED, "Mid Laser - Timing Dodge")
    ]

    for pz, py, color_rgb, desc in laser_data:
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

        glLineWidth(6.0)
        glColor3f(*color_rgb)
        glBegin(GL_LINES)
        glVertex3f(15.0, py, pz); glVertex3f(25.0, py, pz)
        glEnd()

        glLineWidth(2.0)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(15.0, py, pz); glVertex3f(25.0, py, pz)
        glEnd()

def draw_moving_walls():
    """
    Draws Section 5 (X: 70, Z: 240 -> 300): Shifting wall blocks with hazard trims.
    """
    glPushMatrix()
    glTranslatef(65.5 + moving_walls_offset, 3.0, 265.0)
    draw_box(3.0, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
    glTranslatef(1.4, 0.0, 0.0)
    draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(74.5 - moving_walls_offset, 3.0, 265.0)
    draw_box(3.0, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
    glTranslatef(-1.4, 0.0, 0.0)
    draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(65.5 + (1.5 - moving_walls_offset), 3.0, 285.0)
    draw_box(3.0, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
    glTranslatef(1.4, 0.0, 0.0)
    draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(74.5 - (1.5 - moving_walls_offset), 3.0, 285.0)
    draw_box(3.0, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
    glTranslatef(-1.4, 0.0, 0.0)
    draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
    glPopMatrix()

def draw_exit_portal():
    """
    Draws Section 6 (X: 70, Z: 330): Glowing blue exit portal gateway out of the Backrooms maze.
    """
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
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex3f(portal_x - 2.4, 0.0, portal_z + 0.2); glVertex3f(portal_x - 2.4, 5.0, portal_z + 0.2)
    glVertex3f(portal_x + 2.4, 0.0, portal_z + 0.2); glVertex3f(portal_x + 2.4, 5.0, portal_z + 0.2)
    glVertex3f(portal_x - 2.4, 5.0, portal_z + 0.2); glVertex3f(portal_x + 2.4, 5.0, portal_z + 0.2)
    glEnd()

# -----------------------------------------------------------------------------
# Camera Setup & Display Callback
# -----------------------------------------------------------------------------
def setup_camera():
    """
    Configures perspective projection and positions camera in 1st or 3rd person mode using gluLookAt.
    Strictly compliant with course Lab 2/3 camera functions.
    """
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

        dir_x = math.sin(rad_yaw) * math.cos(rad_pitch)
        dir_y = math.sin(rad_pitch)
        dir_z = math.cos(rad_yaw) * math.cos(rad_pitch)

        gluLookAt(cam_x, cam_y, cam_z,
                  cam_x + dir_x, cam_y + dir_y, cam_z + dir_z,
                  0.0, 1.0, 0.0)
    else:
        cam_x = player_pos[0] - math.sin(rad_yaw) * cam_dist
        cam_y = player_pos[1] + cam_height
        cam_z = player_pos[2] - math.cos(rad_yaw) * cam_dist

        target_x = player_pos[0]
        target_y = player_pos[1] + curr_eye_h
        target_z = player_pos[2]

        gluLookAt(cam_x, cam_y, cam_z,
                  target_x, target_y, target_z,
                  0.0, 1.0, 0.0)

def display():
    """
    Main OpenGL Display Callback.
    """
    glClearColor(0.06, 0.07, 0.09, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST)

    setup_camera()

    # Render Connected Maze Environment
    draw_connected_floor_pathways()
    draw_connected_walls()
    draw_pillars_and_archways()
    draw_hazard_zones()
    draw_disappearing_platforms()
    draw_laser_emitters()
    draw_moving_walls()
    draw_exit_portal()

    # Render Character ("tung tung tung sahur")
    draw_character()

    # Determine Active Zone based on X, Z position
    px, pz = player_pos[0], player_pos[2]
    if pz < 60.0:
        zone = "1. Starting Hub (Red Runner)"
    elif pz <= 65.0:
        zone = "Maze Walkway A (Turn East)"
    elif px >= 30.0 and pz < 120.0:
        zone = "2. Trap & Jump Zone (Lava Pits)"
    elif pz <= 125.0:
        zone = "Maze Walkway B (Backrooms Corridor West)"
    elif px <= -30.0 and pz < 180.0:
        zone = "3. Disappearing Floor Chamber (Void Gap)"
    elif pz <= 185.0:
        zone = "Maze Walkway C (Corridor East)"
    elif pz < 240.0:
        zone = "4. Laser Gauntlet Corridor (Beam Dodge)"
    elif pz <= 245.0:
        zone = "Maze Walkway D (Corridor East)"
    elif pz < 300.0:
        zone = "5. Moving Walls Segment (Shifting Blocks)"
    else:
        zone = "6. Exit Portal Chamber (Maze End)"

    # Render HUD Text Overlay
    draw_text(15, WINDOW_HEIGHT - 30, f"9 Lives - Level 1: Fully Connected Maze Walkway Arena")
    draw_text(15, WINDOW_HEIGHT - 55, f"Active Player: 'tung tung tung sahur' | Zone: {zone}")
    draw_text(15, WINDOW_HEIGHT - 80, f"Pos: X={player_pos[0]:.1f}, Y={player_pos[1]:.1f}, Z={player_pos[2]:.1f} | Yaw={player_yaw:.0f} deg")
    draw_text(15, WINDOW_HEIGHT - 105, f"Camera: {'1st Person POV (V to switch)' if first_person else '3rd Person Follow (V to switch)'}")
    if game_over:
        draw_text(15, WINDOW_HEIGHT - 130, f"GAME OVER! 3 consecutive lava falls. Press 'R' to restart.")
    elif game_paused:
        draw_text(15, WINDOW_HEIGHT - 130, f"State: GAME PAUSED (Press 'P' to Resume)")
    elif lava_alert_timer > 0:
        draw_text(15, WINDOW_HEIGHT - 130, f"Lava Strikes: {consecutive_lava_falls}/3 - Fell into the lava!")
    else:
        draw_text(15, WINDOW_HEIGHT - 130, f"State: {'CROUCHING (Hitbox Height = 0.8)' if crouching else 'STANDING (Hitbox Height = 1.6)'}")
    draw_text(15, 20, "Controls: WASD/Arrows: Move/Turn | SPACE: Jump | C/Ctrl: Crouch | V: Camera | P: Pause | R: Reset")

    glutSwapBuffers()

# -----------------------------------------------------------------------------
# Physics & Animation Loop
# -----------------------------------------------------------------------------
# --- Lava Corridor Geometry Constants ---
LAVA_PIT_X_MIN  = 34.4
LAVA_PIT_X_MAX  = 45.6
LAVA_PIT_1_ZMIN = 66.0     # Full corridor start
LAVA_PIT_1_ZMAX = 114.4    # Full corridor end
# (no separate pit 2 — entire corridor is one lava zone)

# Rock top surface Y = 1.25  (centre Y=1.0 + half-height 0.25)
STEP_TOP_Y = 1.25

# All 8 rocks: (x_centre, z_centre, half_x, half_z)
# Generous hitboxes (3.6x4.2 slab -> half_x=2.0, half_z=2.3) for fast fluid running
STEPPING_BOXES = [
    (40.0,  68.0, 2.0, 2.3),  # R1 — entry centre
    (38.8,  74.3, 2.0, 2.3),  # R2 — left
    (41.2,  80.6, 2.0, 2.3),  # R3 — right
    (38.8,  86.9, 2.0, 2.3),  # R4 — left
    (41.2,  93.2, 2.0, 2.3),  # R5 — right
    (38.8,  99.5, 2.0, 2.3),  # R6 — left
    (41.2, 105.8, 2.0, 2.3),  # R7 — right
    (40.0, 112.0, 2.0, 2.3),  # R8 — exit centre
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

def update_player_physics():
    """
    Handles player jumping physics, gravity update, floor/stepping-box collision,
    and lava fall 3-strike detection.
    """
    global player_pos, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, game_over

    if is_jumping:
        player_pos[1] += y_velocity
        y_velocity += gravity

        # --- Landing on a stepping stone box ---
        if on_stepping_box() and y_velocity <= 0 and player_pos[1] <= STEP_TOP_Y:
            player_pos[1] = STEP_TOP_Y
            is_jumping = False
            y_velocity = 0.0
            # Safe crossing — reset strike counter
            consecutive_lava_falls = 0
            return

        # --- Sinking into ground ---
        if player_pos[1] <= ground_y:
            if in_lava_pit():
                # Fell into lava — penalise
                consecutive_lava_falls += 1
                lava_alert_timer = 180          # show alert ~3 s at 60 fps
                if consecutive_lava_falls >= 3:
                    game_over = True
                # Respawn at lava section entry
                player_pos = [40.0, 1.0, 65.0]
                player_yaw = 0.0
            else:
                player_pos[1] = ground_y
            is_jumping = False
            y_velocity = 0.0
    else:
        # On stepping box: keep player at box top height
        if on_stepping_box() and player_pos[1] >= STEP_TOP_Y - 0.05:
            player_pos[1] = STEP_TOP_Y
        # Detect walking off platform into lava while not jumping
        elif in_lava_pit() and player_pos[1] <= ground_y + 0.05:
            consecutive_lava_falls += 1
            lava_alert_timer = 180
            if consecutive_lava_falls >= 3:
                game_over = True
            player_pos = [40.0, 1.0, 65.0]
            player_yaw = 0.0
        # Successful crossing past both pits — reset strike counter
        elif player_pos[2] > LAVA_PIT_1_ZMAX and consecutive_lava_falls > 0:
            consecutive_lava_falls = 0

    # Tick alert display timer
    if lava_alert_timer > 0:
        lava_alert_timer -= 1

def idle():
    """
    Idle Callback: Updates player physics and scaffolding animations.
    Uses strictly allowlisted GLUT callbacks (glutDisplayFunc, glutIdleFunc, glutKeyboardFunc, glutSpecialFunc, glutMouseFunc).
    """
    global moving_walls_offset, moving_walls_dir, platform_timer, disappearing_tiles_active

    if game_paused or game_over:
        glutPostRedisplay()
        return

    update_player_physics()

    if anim_moving_walls:
        moving_walls_offset += 0.02 * moving_walls_dir
        if moving_walls_offset > 1.8 or moving_walls_offset < 0.0:
            moving_walls_dir *= -1.0

    if anim_disappearing_floor:
        platform_timer += 1
        if platform_timer % 40 == 0:
            idx = (platform_timer // 40) % len(disappearing_tiles_active)
            disappearing_tiles_active[idx] = not disappearing_tiles_active[idx]

    glutPostRedisplay()

# -----------------------------------------------------------------------------
# Input Event Handlers
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Input Event Handlers (Strictly Allowlisted Lab Callbacks)
# -----------------------------------------------------------------------------
def keyboard_listener(key, x, y):
    """
    Handles WASD, Spacebar, C, V, P, M, T, R, and ESC keys (glutKeyboardFunc).
    """
    global player_pos, player_yaw, crouching, first_person, anim_moving_walls, anim_disappearing_floor
    global is_jumping, y_velocity, game_paused
    global consecutive_lava_falls, lava_alert_timer, game_over

    try:
        ch = key.decode('utf-8').lower()
    except:
        ch = str(key).lower()

    # Pause Toggle: P Key
    if ch == 'p':
        game_paused = not game_paused
        glutPostRedisplay()
        return

    if game_paused or game_over:
        return

    rad = math.radians(player_yaw)

    # Movement: W (Forward), S (Backward) along facing angle
    if ch == 'w':
        player_pos[0] += math.sin(rad) * player_speed
        player_pos[2] += math.cos(rad) * player_speed
    elif ch == 's':
        player_pos[0] -= math.sin(rad) * player_speed
        player_pos[2] -= math.cos(rad) * player_speed

    # Strafe / Turn: A (Strafe Left / Turn), D (Strafe Right / Turn)
    elif ch == 'a':
        player_pos[0] += math.sin(rad + math.pi/2.0) * player_speed
        player_pos[2] += math.cos(rad + math.pi/2.0) * player_speed
    elif ch == 'd':
        player_pos[0] += math.sin(rad - math.pi/2.0) * player_speed
        player_pos[2] += math.cos(rad - math.pi/2.0) * player_speed

    # Crouch Toggle: C Key
    elif ch == 'c':
        crouching = not crouching

    # Jump Action: Spacebar (b' ' / 0x20)
    elif ch == ' ' or key == b' ':
        if not is_jumping:
            is_jumping = True
            y_velocity = jump_strength

    # Camera Switch: V Key
    elif ch == 'v':
        first_person = not first_person

    # Demo Toggles: M (Moving Walls), T (Platforms)
    elif ch == 'm':
        anim_moving_walls = not anim_moving_walls
    elif ch == 't':
        anim_disappearing_floor = not anim_disappearing_floor

    # Reset Position: R Key
    elif ch == 'r':
        player_pos = [0.0, 1.0, 5.0]
        player_yaw = 0.0
        crouching = False
        is_jumping = False
        consecutive_lava_falls = 0
        lava_alert_timer = 0
        game_over = False

    # ESC Key to Exit
    elif key == b'\x1b':
        try:
            glutLeaveMainLoop()
        except:
            sys.exit(0)

    glutPostRedisplay()

def special_key_listener(key, x, y):
    """
    Handles Arrow Keys (Up/Down for move forward/backward, Left/Right for turn yaw) and Left Ctrl (glutSpecialFunc).
    """
    global player_pos, player_yaw, crouching, game_paused
    if game_paused or game_over:
        return
    rad = math.radians(player_yaw)

    if key == GLUT_KEY_UP:
        player_pos[0] += math.sin(rad) * player_speed
        player_pos[2] += math.cos(rad) * player_speed
    elif key == GLUT_KEY_DOWN:
        player_pos[0] -= math.sin(rad) * player_speed
        player_pos[2] -= math.cos(rad) * player_speed
    elif key == GLUT_KEY_LEFT:
        player_yaw = (player_yaw + 4.5) % 360.0
    elif key == GLUT_KEY_RIGHT:
        player_yaw = (player_yaw - 4.5) % 360.0
    elif key == 114 or key == 115: # GLUT_KEY_CTRL_L or GLUT_KEY_CTRL_R
        crouching = not crouching

    glutPostRedisplay()

def mouse_listener(button, state, x, y):
    """
    Handles mouse clicks (Right Click toggles Camera view) (glutMouseFunc).
    """
    global first_person
    if state == GLUT_DOWN:
        if button == GLUT_RIGHT_BUTTON:
            first_person = not first_person
            glutPostRedisplay()

# -----------------------------------------------------------------------------
# Main Function Entry Point
# -----------------------------------------------------------------------------
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(WINDOW_TITLE)

    load_character_model()

    # Register 100% Allowlisted Lab Callbacks Only
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
