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
- Left / Right Ctrl     : Crouch (Hitbox drops to 0.8 units)
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
player_pos = [0.0, 1.0, 7.4]     # X, Y, Z coordinates
player_yaw = 0.0                  # Character facing angle in degrees
player_pitch = 0.0                # Pitch angle looking up/down
player_speed = 0.90         # Movement speed factor
crouching = False                 # Crouch state
eye_height = 1.6                  # Standing eye height

# Jump Physics Parameters
is_jumping = False
y_velocity = 0.0
gravity = -0.014
jump_strength = 0.28
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

# Lava Pit & Hazard 3-Strike Tracking
consecutive_lava_falls = 0
lava_alert_timer = 0           # frames to show alert message
hazard_alert_text = "Fell into the lava!"
game_over = False

# Moving Walls Hazard Tracking (Zone 5)
consecutive_wall_hits = 0
wall_invincibility_timer = 0   # frames of invincibility after wall crush hit

# Invincibility / God Mode Cheat Flag (Toggled by '1' Key)
cheat_mode = False

# -----------------------------------------------------------------------------
# Story Screen State & Content
# -----------------------------------------------------------------------------
in_story_screen = True
story_lines = [
    "Tung Tung Tung Sahur has wandered into the Evil Cat World!",
    "Armed with 9 Lives, you must survive the traps and",
    "defeat the wicked cats trying to take over the world."
]
story_char_index = 0
story_timer = 0
total_story_len = sum(len(line) for line in story_lines)

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

def draw_text(x, y, text_str, color=(1.0, 1.0, 1.0)):
    """
    Renders 2D HUD text using GLUT_BITMAP_HELVETICA_18 with optional color parameter.
    """
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
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_bar_2d(x, y, w, h, fill_pct, fill_color, border_color=(0.9, 0.9, 0.9)):
    """
    Renders a 2D health bar with border frame and filled percentage (Level 3 HUD style).
    """
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Border frame
    glLineWidth(1.5)
    glBegin(GL_LINES)
    glColor3f(*border_color)
    glVertex2f(x, y); glVertex2f(x + w, y)
    glVertex2f(x + w, y); glVertex2f(x + w, y + h)
    glVertex2f(x + w, y + h); glVertex2f(x, y + h)
    glVertex2f(x, y + h); glVertex2f(x, y)
    glEnd()

    # Inner health fill
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
    Draws a 100% tightly bound, fully connected solid floor mesh matching the exact widths
    and lengths of the active walkway corridors and chambers (width 11.2 units).
    """
    # 1. Start Hub Floor (X: -6.0 -> +6.0, Z: -0.4 -> 54.4)
    glPushMatrix()
    glTranslatef(0.0, -0.1, 27.0)
    draw_box(12.0, 0.2, 54.8, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
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

    # 2. Junction A / Walkway A Floor (X: -6.0 -> 46.0, Z: 54.4 -> 65.6)
    glPushMatrix()
    glTranslatef(20.0, -0.1, 60.0)
    draw_box(52.0, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 3. Hazard Pit Corridor (Zone 2, X: 34.4 -> 45.6, Z: 65.6 -> 114.4)
    #    Entire floor is lava + rock slabs rendered in draw_hazard_zones()

    # 4. Junction B / Walkway B Floor (X: -46.0 -> +46.0, Z: 114.4 -> 125.6)
    glPushMatrix()
    glTranslatef(0.0, -0.1, 120.0)
    draw_box(92.0, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 5. Disappearing Floor Entry & Exit Connected Ledges (X: -45.6 -> -34.4)
    # Entry Ledge (Z: 125.2 -> 130.8)
    glPushMatrix()
    glTranslatef(-40.0, -0.1, 128.0)
    draw_box(11.2, 0.2, 5.6, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # Exit Ledge (Z: 169.2 -> 174.8)
    glPushMatrix()
    glTranslatef(-40.0, -0.1, 172.0)
    draw_box(11.2, 0.2, 5.6, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 6. Junction C / Walkway C Floor (X: -46.0 -> 25.6, Z: 174.4 -> 185.6)
    glPushMatrix()
    glTranslatef(-10.2, -0.1, 180.0)
    draw_box(71.6, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 7. Laser Gauntlet Corridor Floor (X: 14.4 -> 25.6, Z: 185.6 -> 234.4)
    glPushMatrix()
    glTranslatef(20.0, -0.1, 210.0)
    draw_box(11.2, 0.2, 48.8, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 8. Junction D / Walkway D Floor (X: 14.4 -> 75.6, Z: 234.4 -> 245.6)
    glPushMatrix()
    glTranslatef(45.0, -0.1, 240.0)
    draw_box(61.2, 0.2, 11.2, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    # 9. Moving Walls & Exit Chamber Floor (X: 64.4 -> 75.6, Z: 245.6 -> 340.0)
    glPushMatrix()
    glTranslatef(70.0, -0.1, 292.8)
    draw_box(11.2, 0.2, 94.4, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
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
    wall(13.8, 3.5, 65.6, 41.2, 7.0, 0.8)           # South Wall (X: -6.4 -> 34.4, clear entry to Zone 2 at X: 34.4->45.6)
    wall(26.0, 3.5, 54.4, 40.0, 7.0, 0.8)           # North Wall extended (X: 6.0 -> 46.0, fully closes pathway gap)

    # 3. Hazard Pit Corridor Walls (Z: 54 -> 120)
    wall(34.4, 3.5, 90.2, 0.8, 7.0, 49.2)           # West Wall (Z: 65.6 -> 114.8, clear walkway from Junction A)
    wall(45.6, 3.5, 87.0, 0.8, 7.0, 66.0)           # East Wall extended back to Z: 54.0 (fully connects to North Wall)

    # 4. Turn 2 Junction Walls (Connected to Long Backrooms Corridor B)
    wall(45.6, 3.5, 120.0, 0.8, 7.0, 12.0)          # East end cap of Junction B
    wall(5.8, 3.5, 125.6, 80.4, 7.0, 0.8)           # North Wall (X: -34.4 -> +46.0, clear entry to Zone 3 at X: -45.6->-34.4)
    wall(-5.8, 3.5, 114.4, 80.4, 7.0, 0.8)          # South Wall (X: -46.0 -> +34.4, clear exit from Lava Pit at X: 34.4->45.6)

    # 5. Disappearing Chamber Walls (Z: 114 -> 181)
    wall(-45.6, 3.5, 147.5, 0.8, 7.0, 67.0)          # West Wall extended (X: -45.6, Z: 114.0 -> 181.0, connects to South Wall)
    wall(-34.4, 3.5, 147.2, 0.8, 7.0, 56.0)          # East Wall (X: -34.4)

    # 6. Turn 3 Junction Walls (Connected to Corridor C)
    wall(-45.6, 3.5, 180.0, 0.8, 7.0, 12.0)          # West end cap of Junction C
    wall(-15.8, 3.5, 185.6, 60.4, 7.0, 0.8)          # North Wall (X: -46.0 -> 14.4, clear entry to Zone 4 at X: 14.4->25.6)
    wall(-4.5, 3.5, 174.4, 61.0, 7.0, 0.8)           # South Wall extended (X: -35.0 -> 26.0, closes East corner gap)

    # 7. Laser Gauntlet Corridor Walls (Z: 177 -> 246)
    wall(14.4, 3.5, 215.5, 0.8, 7.0, 61.0)           # West Wall extended (Z: 185.0 -> 246.0, fully closes West corner cap)
    wall(25.6, 3.5, 210.0, 0.8, 7.0, 66.0)           # East Wall extended (Z: 177.0 -> 243.0, overlaps with Junctions C & D)

    # 8. Turn 4 Junction Walls (Connected to Corridor D)
    wall(50.8, 3.5, 234.4, 50.4, 7.0, 0.8)          # South Wall (X: 25.6 -> 76.0, clear walkway at X: 14.4->25.6)
    wall(39.8, 3.5, 245.6, 51.6, 7.0, 0.8)          # North Wall extended (X: 14.0 -> 65.6, fully closes Junction D gap)

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
    # 2B. 3D VOLCANIC LAVA SPIKES
    # -----------------------------------------------------------------
    def draw_lava_spike(x, y, z, base_w=0.35, height=1.5):
        """
        Renders a sharp 3D obsidian/magma spike rising from the lava.
        """
        glPushMatrix()
        glTranslatef(x, y, z)
        c_base = (0.16, 0.12, 0.14)
        c_tip  = (1.00, 0.40, 0.00)
        glBegin(GL_TRIANGLES)
        # Front face
        glColor3f(*c_base); glVertex3f(-base_w, 0.0,  base_w)
        glColor3f(*c_base); glVertex3f( base_w, 0.0,  base_w)
        glColor3f(*c_tip);  glVertex3f( 0.0, height,  0.0)
        # Right face
        glColor3f(*c_base); glVertex3f( base_w, 0.0,  base_w)
        glColor3f(*c_base); glVertex3f( base_w, 0.0, -base_w)
        glColor3f(*c_tip);  glVertex3f( 0.0, height,  0.0)
        # Back face
        glColor3f(*c_base); glVertex3f( base_w, 0.0, -base_w)
        glColor3f(*c_base); glVertex3f(-base_w, 0.0, -base_w)
        glColor3f(*c_tip);  glVertex3f( 0.0, height,  0.0)
        # Left face
        glColor3f(*c_base); glVertex3f(-base_w, 0.0, -base_w)
        glColor3f(*c_base); glVertex3f(-base_w, 0.0,  base_w)
        glColor3f(*c_tip);  glVertex3f( 0.0, height,  0.0)
        glEnd()
        glPopMatrix()

    # Clusters of sharp lava spikes sticking up throughout the lava pit
    for z_spk in range(int(ZSTART) + 3, int(ZEND) - 3, 4):
        draw_lava_spike(CX - 4.2, 0.1, float(z_spk),        0.40, 1.8)
        draw_lava_spike(CX - 2.5, 0.1, float(z_spk) + 1.5,  0.30, 1.4)
        draw_lava_spike(CX + 2.5, 0.1, float(z_spk) + 0.8,  0.32, 1.5)
        draw_lava_spike(CX + 4.2, 0.1, float(z_spk) + 2.2,  0.42, 1.9)

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

# -----------------------------------------------------------------------------
# Disappearing Platform Chamber Constants & Rendering
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
    """
    Draws Section 3 (X: -40, Z: 120 -> 180): Deep abyss gap bridged by color-coded platform tiles.
    Uses module-level DISAPPEARING_TILE_COORDS and TILE_COLORS.
    """
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
            glLineWidth(1.5)
            glBegin(GL_LINES)
            for dx in [-1.4, 1.4]:
                for dz in [-2.0, 2.0]:
                    glVertex3f(dx, -0.2, dz)
                    glVertex3f(dx, 0.2, dz)
            glEnd()
            
        glPopMatrix()

# -----------------------------------------------------------------------------
# Laser Gauntlet Constants & Rendering (Section 4, X: 14.4 -> 25.6, Z: 180 -> 240)
# -----------------------------------------------------------------------------
LASER_BEAMS = [
    (192.0, 2.2,  COLOR_LASER_RED, "Laser 1 (Z: 192.0, Y: 2.2) - High Beam (Crouch Under)"),
    (202.0, 0.65, COLOR_LASER_RED, "Laser 2 (Z: 202.0, Y: 0.65) - Low Beam (Jump Over)"),
    (212.0, 2.2,  COLOR_LASER_RED, "Laser 3 (Z: 212.0, Y: 2.2) - High Beam (Crouch Under)"),
    (222.0, 0.65, COLOR_LASER_RED, "Laser 4 (Z: 222.0, Y: 0.65) - Low Beam (Jump Over)"),
    (232.0, 1.8,  COLOR_LASER_RED, "Laser 5 (Z: 232.0, Y: 1.8) - Mid-High Beam (Crouch Dodge)")
]

def draw_laser_emitters():
    """
    Draws Section 4 (X: 14.4 -> 25.6, Z: 180 -> 240): Crouch & Jump horizontal laser beams.
    Renders all 5 red laser beams with side emitter boxes and thick glowing red lines.
    """
    for pz, py, color_rgb, desc in LASER_BEAMS:
        # Left side emitter box
        glPushMatrix()
        glTranslatef(14.7, py, pz)
        draw_box(0.6, 0.8, 0.8, color_top=(0.3, 0.3, 0.35), color_side=(0.2, 0.2, 0.25))
        glTranslatef(0.35, 0.0, 0.0)
        draw_box(0.1, 0.4, 0.4, color_top=color_rgb, color_side=color_rgb)
        glPopMatrix()

        # Right side emitter box
        glPushMatrix()
        glTranslatef(25.3, py, pz)
        draw_box(0.6, 0.8, 0.8, color_top=(0.3, 0.3, 0.35), color_side=(0.2, 0.2, 0.25))
        glTranslatef(-0.35, 0.0, 0.0)
        draw_box(0.1, 0.4, 0.4, color_top=color_rgb, color_side=color_rgb)
        glPopMatrix()

        # Outer thick glowing red beam line
        glLineWidth(6.0)
        glColor3f(*color_rgb)
        glBegin(GL_LINES)
        glVertex3f(15.0, py, pz); glVertex3f(25.0, py, pz)
        glEnd()

        # Inner bright white core line
        glLineWidth(2.0)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(15.0, py, pz); glVertex3f(25.0, py, pz)
        glEnd()

# -----------------------------------------------------------------------------
# Moving Walls Constants (Section 5, X: 64.4 -> 75.6, Z: 240 -> 300)
# Wall Pair data: (z_center, phase_multiplier)
#   phase_multiplier = 1.0 means same phase as offset; -1.0 means inverted phase
# -----------------------------------------------------------------------------
MOVING_WALL_PAIRS = [
    (260.0,  1.0),   # Wall Pair 1: same phase
    (275.0, -1.0),   # Wall Pair 2: inverted phase (closes when Pair 1 opens)
    (290.0,  1.0),   # Wall Pair 3: same phase as Pair 1
]
MOVING_WALL_CX = 70.0      # corridor centre X
MOVING_WALL_BLOCK_W = 3.0  # width of each wall block
MOVING_WALL_REST_L = 65.5  # left block rest X
MOVING_WALL_REST_R = 74.5  # right block rest X

def draw_moving_walls():
    """
    Draws Section 5 (X: 64.4 -> 75.6, Z: 240 -> 300): 3 shifting wall pairs
    with prominent hazard caution stripe edges.
    """
    for wz, phase in MOVING_WALL_PAIRS:
        offset = moving_walls_offset * phase

        # Left crushing wall block
        left_x = MOVING_WALL_REST_L + offset
        glPushMatrix()
        glTranslatef(left_x, 3.0, wz)
        draw_box(MOVING_WALL_BLOCK_W, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
        # Hazard caution stripe on the crushing inner edge (right side of left block)
        glTranslatef(MOVING_WALL_BLOCK_W / 2.0 - 0.1, 0.0, 0.0)
        draw_box(0.2, 5.6, 7.8, color_top=COLOR_HAZARD_STRIPE, color_side=(0.7, 0.55, 0.0))
        glPopMatrix()

        # Right crushing wall block
        right_x = MOVING_WALL_REST_R - offset
        glPushMatrix()
        glTranslatef(right_x, 3.0, wz)
        draw_box(MOVING_WALL_BLOCK_W, 5.8, 8.0, color_top=(0.35, 0.30, 0.25), color_side=(0.25, 0.20, 0.15))
        # Hazard caution stripe on the crushing inner edge (left side of right block)
        glTranslatef(-(MOVING_WALL_BLOCK_W / 2.0 - 0.1), 0.0, 0.0)
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
    glLineWidth(line_width)
    glBegin(GL_LINES)
    glVertex2f(x1, y1); glVertex2f(x2, y1)
    glVertex2f(x2, y1); glVertex2f(x2, y2)
    glVertex2f(x2, y2); glVertex2f(x1, y2)
    glVertex2f(x1, y2); glVertex2f(x1, y1)
    glEnd()

def update_window_dimensions():
    """
    Queries current GLUT window dimensions and updates global WINDOW_WIDTH / WINDOW_HEIGHT.
    Ensures perfect centering when the game is maximized or full-screened.
    """
    global WINDOW_WIDTH, WINDOW_HEIGHT
    cur_w = glutGet(GLUT_WINDOW_WIDTH)
    cur_h = glutGet(GLUT_WINDOW_HEIGHT)
    if cur_w > 0 and cur_h > 0:
        WINDOW_WIDTH, WINDOW_HEIGHT = cur_w, cur_h

def reshape_listener(w, h):
    """
    GLUT reshape callback when window size changes (fullscreen, maximize, resize).
    """
    global WINDOW_WIDTH, WINDOW_HEIGHT
    if w > 0 and h > 0:
        WINDOW_WIDTH, WINDOW_HEIGHT = w, h
        glViewport(0, 0, w, h)
        glutPostRedisplay()

def draw_story_screen():
    """
    Renders a centered cinematic Story UI Screen with glassmorphism panel,
    theme-matching cyan/gold colors, typewriter text, and pulsing start prompt.
    Automatically stays dynamically centered on full screen / window resize.
    """
    update_window_dimensions()

    glClearColor(0.03, 0.04, 0.07, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # 1. Background Ambient Grid
    glLineWidth(1.0)
    glColor3f(0.08, 0.10, 0.16)
    glBegin(GL_LINES)
    for gx in range(0, WINDOW_WIDTH, 40):
        glVertex2f(gx, 0); glVertex2f(gx, WINDOW_HEIGHT)
    for gy in range(0, WINDOW_HEIGHT, 40):
        glVertex2f(0, gy); glVertex2f(WINDOW_WIDTH, gy)
    glEnd()

    # 2. Centered Story UI Container Panel Box
    panel_w, panel_h = 680, 360
    px1 = (WINDOW_WIDTH - panel_w) // 2
    px2 = px1 + panel_w
    py1 = (WINDOW_HEIGHT - panel_h) // 2
    py2 = py1 + panel_h

    # Dark Slate Inner Glass Box
    draw_rect_2d(px1, py1, px2, py2, (0.07, 0.08, 0.13))

    # Outer Cyan & Gold Dual Accent Borders
    draw_rect_border_2d(px1, py1, px2, py2, (0.0, 0.75, 0.95), line_width=2.5)
    draw_rect_border_2d(px1 + 4, py1 + 4, px2 - 4, py2 - 4, (1.0, 0.7, 0.2), line_width=1.0)

    # 3. Header Title (Fiery Orange / Amber Gold)
    title_str = "★  9 LIVES: EVIL CAT WORLD  ★"
    t_w = len(title_str) * 9.2
    t_start_x = (WINDOW_WIDTH - t_w) // 2
    title_y = py2 - 48

    # Title Glow Shadow
    glColor3f(0.3, 0.1, 0.0)
    glRasterPos2f(t_start_x + 1, title_y - 1)
    for ch in title_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(1.0, 0.45, 0.15)
    glRasterPos2f(t_start_x, title_y)
    for ch in title_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    # Divider Accent Line under Title
    glColor3f(0.0, 0.75, 0.95)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex2f(px1 + 40, py2 - 62)
    glVertex2f(px2 - 40, py2 - 62)
    glEnd()

    # 4. Typewriter Story Body Text Lines (Vertically & Horizontally Centered inside Panel)
    chars_left = story_char_index
    body_center_y = py1 + 175  # Vertical center of panel

    # 3 lines spacing offsets: +35, -5, -45
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

    # 5. Pulsing Bottom Prompt Button Bar
    prompt_str = "PRESS SPACE OR ENTER TO START"
    # Measure exact GLUT pixel width for 100% precise horizontal centering
    p_w = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(ch)) for ch in prompt_str)
    p_start_x = (WINDOW_WIDTH - p_w) // 2
    prompt_y = py1 + 35

    pulse_val = 0.5 + 0.5 * math.sin(story_timer * 0.08)

    # Symmetrical prompt button box dimensions (24px horizontal, 18px vertical padding)
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
    """
    Main OpenGL Display Callback.
    """
    update_window_dimensions()

    if in_story_screen:
        draw_story_screen()
        return

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
    # Blink/flash character during wall invincibility frames (visible every other 10 frames)
    if wall_invincibility_timer > 0:
        if (wall_invincibility_timer // 10) % 2 == 0:
            draw_character()
        # else: skip drawing = blink effect
    else:
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

    # Render Clean HUD Overlay (Top-Left Corner) - Level 3 Health Bar Style
    remaining_lives = max(0, 9 - consecutive_lava_falls)
    player_pct = remaining_lives / 9.0

    # Color transition based on remaining health percentage (Green -> Yellow -> Red)
    if player_pct > 0.5:
        bar_color = (0.1, 0.9, 0.2)    # Bright Green
    elif player_pct > 0.25:
        bar_color = (1.0, 0.8, 0.0)    # Warning Yellow
    else:
        bar_color = (1.0, 0.15, 0.15)  # Danger Red

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

    draw_text(15, 20, "Controls: WASD/Arrows: Move/Turn | SPACE: Jump | Ctrl: Crouch | V: Camera | P: Pause | C: God Mode | R: Reset")

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
# Strict hitboxes matching exact visual rock size (3.6x4.2 slab -> half_x=1.8, half_z=2.1)
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
    """
    Checks whether the player collides with any of the 5 laser beams in Section 4 (X: 14.4->25.6, Z: 180->240).
    The player can freely CROUCH or JUMP by their choice to dodge any laser beam.
    If the player is crouching OR jumping, the laser is safely dodged.
    Laser positions remain unchanged.
    """
    global player_pos, player_yaw, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over

    if cheat_mode:
        return False

    px, py, pz = player_pos[0], player_pos[1], player_pos[2]

    # Only check inside Laser Gauntlet corridor (X: 14.4 -> 25.6, Z: 180 -> 240)
    if not (14.4 <= px <= 25.6 and 180.0 <= pz <= 240.0):
        return False

    # Safe dodge if player is EITHER crouching OR jumping (or elevated off ground)
    player_is_dodging = crouching or is_jumping or (py > ground_y + 0.15)

    for lz, ly, color_rgb, desc in LASER_BEAMS:
        # Z hit window (~0.7 units around laser beam)
        if abs(pz - lz) <= 0.7:
            # If the player is NOT dodging (neither crouching nor jumping), the laser hits!
            if not player_is_dodging:
                consecutive_lava_falls += 1
                hazard_alert_text = "Hit by Laser! (Crouch 'CTRL' or Jump 'SPACE' to dodge)"
                lava_alert_timer = 180
                if consecutive_lava_falls >= 9:
                    game_over = True
                # Respawn at Laser Gauntlet entrance
                player_pos = [20.0, 1.0, 182.0]
                player_yaw = 0.0
                is_jumping = False
                y_velocity = 0.0
                return True
    return False

def check_moving_wall_collisions():
    """
    Checks whether the player is pinched/crushed between moving wall pairs in Zone 5.
    For each wall pair, calculates the dynamic gap. If the player's X falls outside the
    safe open gap between the left and right walls, a pinch/crush hit occurs.
    - Grants 60 invincibility frames after a hit (blink effect).
    - Tracks consecutive_wall_hits; 3 consecutive hits respawns at Zone 5 entry.
    - Feeds into global hazard strike / game_over system.
    """
    global player_pos, player_yaw, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over
    global consecutive_wall_hits, wall_invincibility_timer

    if cheat_mode:
        return False

    # Skip if invincibility frames are active (just got hit)
    if wall_invincibility_timer > 0:
        return False

    px, pz = player_pos[0], player_pos[2]

    # Only check inside Moving Walls corridor (X: 64.4 -> 75.6, Z: 240 -> 300)
    if not (64.4 <= px <= 75.6 and 240.0 <= pz <= 300.0):
        # Safely crossed past all walls — reset consecutive wall hits
        if pz > 298.0 and consecutive_wall_hits > 0:
            consecutive_wall_hits = 0
        return False

    for wz, phase in MOVING_WALL_PAIRS:
        # Z-span check: player within ~4.0 units of wall pair center (each wall block is 8.0 deep)
        if abs(pz - wz) < 4.0:
            offset = moving_walls_offset * phase

            # Calculate dynamic wall edge positions
            left_inner_edge = (MOVING_WALL_REST_L + offset) + MOVING_WALL_BLOCK_W / 2.0
            right_inner_edge = (MOVING_WALL_REST_R - offset) - MOVING_WALL_BLOCK_W / 2.0

            # Player is crushed if their X position overlaps with either wall block
            if px <= left_inner_edge or px >= right_inner_edge:
                # --- CRUSH HIT ---
                consecutive_wall_hits += 1
                consecutive_lava_falls += 1
                hazard_alert_text = "Crushed by Moving Walls!"
                lava_alert_timer = 180
                wall_invincibility_timer = 60  # ~1 second of invincibility blink

                if consecutive_lava_falls >= 9:
                    game_over = True

                if consecutive_wall_hits >= 3:
                    # 3 consecutive wall hits: respawn at Zone 5 entry
                    player_pos = [70.0, 1.0, 245.0]
                    player_yaw = 0.0
                    consecutive_wall_hits = 0
                else:
                    # Push player back to corridor centre to escape the pinch
                    player_pos[0] = MOVING_WALL_CX

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
    """
    Checks whether the player is inside the Disappearing Floor tile field (Zone 3: Z=135.0->165.0).
    If the player steps on a vanished tile OR steps into empty void space (not on an active tile)
    while at floor level, deducts a lifeline, displays hazard alert, and respawns on the safe entry walkway.
    """
    global player_pos, player_yaw, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over

    if cheat_mode:
        return False

    px, py, pz = player_pos[0], player_pos[1], player_pos[2]

    # Only check inside the tile field gap (X: -45.6 -> -34.4, Z: 135.0 -> 165.0)
    if not (-45.6 <= px <= -34.4 and 135.0 <= pz <= 165.0):
        return False

    # Safe if player is airborne jumping high above the floor
    if py > ground_y + 0.15:
        return False

    # Check if player is standing on any active platform
    if not is_on_active_disappearing_tile(px, pz):
        # Stepped on a vanished tile OR into the void gap!
        consecutive_lava_falls += 1
        hazard_alert_text = "Fell into the void!"
        lava_alert_timer = 180
        if consecutive_lava_falls >= 9:
            game_over = True
        # Respawn safely on the solid entry walkway before the tile gap
        player_pos = [-40.0, 1.0, 128.0]
        player_yaw = 0.0
        is_jumping = False
        y_velocity = 0.0
        return True

    return False

def update_player_physics():
    """
    Handles player jumping physics, gravity update, floor/stepping-box collision,
    lava fall 3-strike detection, and disappearing floor hazard collision.
    """
    global player_pos, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text, game_over

    if is_jumping:
        player_pos[1] += y_velocity
        y_velocity += gravity

        # --- Landing on a stepping stone box ---
        if on_stepping_box() and y_velocity <= 0 and player_pos[1] <= STEP_TOP_Y:
            player_pos[1] = STEP_TOP_Y
            is_jumping = False
            y_velocity = 0.0
            return

        # --- Sinking into ground ---
        if player_pos[1] <= ground_y:
            if in_lava_pit():
                if not cheat_mode:
                    # Fell into lava — penalise
                    consecutive_lava_falls += 1
                    hazard_alert_text = "Fell into the lava!"
                    lava_alert_timer = 180          # show alert ~3 s at 60 fps
                    if consecutive_lava_falls >= 9:
                        game_over = True
                    # Respawn at lava section entry
                    player_pos = [40.0, 1.0, 65.0]
                    player_yaw = 0.0
                else:
                    player_pos[1] = ground_y
            else:
                player_pos[1] = ground_y
            is_jumping = False
            y_velocity = 0.0
    else:
        # On stepping box: keep player at box top height
        if on_stepping_box():
            player_pos[1] = STEP_TOP_Y
        # Detect stepping outside rock size into lava while not jumping
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

    # --- Check Disappearing Floor Hazard Collision ---
    check_disappearing_floor()

    # --- Check Laser Beam Hazard Collision ---
    check_laser_collisions()

    # --- Check Moving Wall Pinch/Crush Collision ---
    check_moving_wall_collisions()

    # Tick alert display timer
    if lava_alert_timer > 0:
        lava_alert_timer -= 1

def idle():
    """
    Idle Callback: Updates story typewriter, physics, and scaffolding animations.
    Uses strictly allowlisted GLUT callbacks (glutDisplayFunc, glutIdleFunc, glutKeyboardFunc, glutSpecialFunc, glutMouseFunc).
    """
    global story_timer, story_char_index, in_story_screen
    global moving_walls_offset, moving_walls_dir, platform_timer, disappearing_tiles_active
    global wall_invincibility_timer

    if in_story_screen:
        story_timer += 1
        if story_timer % 2 == 0 and story_char_index < total_story_len:
            story_char_index += 1
        glutPostRedisplay()
        return

    if game_paused or game_over:
        glutPostRedisplay()
        return

    update_player_physics()

    # Tick wall invincibility blink timer
    if wall_invincibility_timer > 0:
        wall_invincibility_timer -= 1

    if anim_moving_walls:
        moving_walls_offset += 0.05 * moving_walls_dir
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
def is_valid_walkway_position(x, z):
    """
    Returns True if (x, z) is inside any valid playable maze corridor segment.
    Prevents player from phasing through walls into outside void space.
    """
    # 1. Start Hub (X: -5.5 -> +5.5, Z: 0.0 -> 54.4)
    if -5.5 <= x <= 5.5 and 0.0 <= z <= 54.4:
        return True

    # 2. Junction A (X: -5.5 -> 45.0, Z: 54.8 -> 65.2)
    if -5.5 <= x <= 45.0 and 54.8 <= z <= 65.2:
        return True

    # 3. Hazard Lava Pit Corridor (X: 34.8 -> 45.2, Z: 54.8 -> 125.2)
    if 34.8 <= x <= 45.2 and 54.8 <= z <= 125.2:
        return True

    # 4. Junction B (X: -45.2 -> 45.2, Z: 114.8 -> 125.2)
    if -45.2 <= x <= 45.2 and 114.8 <= z <= 125.2:
        return True

    # 5. Disappearing Floor Chamber (X: -45.2 -> -34.8, Z: 114.8 -> 185.2)
    if -45.2 <= x <= -34.8 and 114.8 <= z <= 185.2:
        return True

    # 6. Junction C (X: -45.2 -> 25.2, Z: 174.8 -> 185.2)
    if -45.2 <= x <= 25.2 and 174.8 <= z <= 185.2:
        return True

    # 7. Laser Gauntlet Corridor (X: 14.8 -> 25.2, Z: 174.8 -> 245.2)
    if 14.8 <= x <= 25.2 and 174.8 <= z <= 245.2:
        return True

    # 8. Junction D (X: 14.8 -> 75.2, Z: 234.8 -> 245.2)
    if 14.8 <= x <= 75.2 and 234.8 <= z <= 245.2:
        return True

    # 9. Moving Walls & Exit Chamber (X: 64.8 -> 75.2, Z: 234.8 -> 339.6)
    if 64.8 <= x <= 75.2 and 234.8 <= z <= 339.6:
        return True

    return False

def try_move_player(dx, dz):
    """
    Attempts to move player by (dx, dz) with smooth wall sliding response.
    Prevents player from phasing through any wall.
    """
    new_x = player_pos[0] + dx
    new_z = player_pos[2] + dz

    # 1. Try full movement
    if is_valid_walkway_position(new_x, new_z):
        player_pos[0] = new_x
        player_pos[2] = new_z
    # 2. Slide along X axis only
    elif is_valid_walkway_position(new_x, player_pos[2]):
        player_pos[0] = new_x
    # 3. Slide along Z axis only
    elif is_valid_walkway_position(player_pos[0], new_z):
        player_pos[2] = new_z

def reset_game():
    """
    Restores player position, facing angle, physics state, hazard counters, alerts,
    and game over/paused states back to initial start level defaults.
    """
    global player_pos, player_yaw, crouching, first_person, is_jumping, y_velocity
    global consecutive_lava_falls, lava_alert_timer, hazard_alert_text
    global consecutive_wall_hits, wall_invincibility_timer, cheat_mode, game_over, game_paused
    global moving_walls_offset, moving_walls_dir

    player_pos = [0.0, 1.0, 7.4]
    player_yaw = 0.0
    crouching = False
    is_jumping = False
    y_velocity = 0.0
    consecutive_lava_falls = 0
    lava_alert_timer = 0
    hazard_alert_text = "Fell into the lava!"
    consecutive_wall_hits = 0
    wall_invincibility_timer = 0
    cheat_mode = False
    game_over = False
    game_paused = False
    moving_walls_offset = 0.0
    moving_walls_dir = 1.0

def keyboard_listener(key, x, y):
    """
    Handles WASD, Spacebar, C, V, P, M, T, R, and ESC keys (glutKeyboardFunc).
    """
    global in_story_screen, player_pos, player_yaw, crouching, first_person, anim_moving_walls, anim_disappearing_floor
    global is_jumping, y_velocity, game_paused
    global consecutive_lava_falls, lava_alert_timer, game_over
    global consecutive_wall_hits, wall_invincibility_timer, cheat_mode, hazard_alert_text

    try:
        ch = key.decode('utf-8').lower()
    except:
        ch = str(key).lower()

    # Story screen skip / start transition
    if in_story_screen:
        if ch in (' ', '\r', '\n') or key in (b' ', b'\r', b'\n'):
            in_story_screen = False
            glutPostRedisplay()
        return

    # Game Restart: R Key (r / R) — Always active (Game Over, Paused, or Playing)
    if ch == 'r':
        reset_game()
        glutPostRedisplay()
        return

    # God Mode / Invincibility Cheat Toggle: C Key (c/C)
    if ch == 'c':
        cheat_mode = not cheat_mode
        glutPostRedisplay()
        return

    # Pause Toggle: P Key
    if ch == 'p':
        game_paused = not game_paused
        glutPostRedisplay()
        return

    # ESC Key to Exit
    if key == b'\x1b':
        try:
            glutLeaveMainLoop()
        except:
            sys.exit(0)

    if game_paused or game_over:
        return

    rad = math.radians(player_yaw)

    # Movement: W (Forward), S (Backward) along facing angle
    if ch == 'w':
        try_move_player(math.sin(rad) * player_speed, math.cos(rad) * player_speed)
    elif ch == 's':
        try_move_player(-math.sin(rad) * player_speed, -math.cos(rad) * player_speed)

    # Strafe / Turn: A (Strafe Left / Turn), D (Strafe Right / Turn)
    elif ch == 'a':
        try_move_player(math.sin(rad + math.pi/2.0) * player_speed, math.cos(rad + math.pi/2.0) * player_speed)
    elif ch == 'd':
        try_move_player(math.sin(rad - math.pi/2.0) * player_speed, math.cos(rad - math.pi/2.0) * player_speed)

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

    glutPostRedisplay()

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
        try_move_player(math.sin(rad) * player_speed, math.cos(rad) * player_speed)
    elif key == GLUT_KEY_DOWN:
        try_move_player(-math.sin(rad) * player_speed, -math.cos(rad) * player_speed)
    elif key == GLUT_KEY_LEFT:
        player_yaw = (player_yaw + 4.5) % 360.0
    elif key == GLUT_KEY_RIGHT:
        player_yaw = (player_yaw - 4.5) % 360.0
    elif key in (114, 115): # GLUT_KEY_CTRL_L or GLUT_KEY_CTRL_R (Ctrl Key Crouch Toggle)
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
    glutReshapeFunc(reshape_listener)
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
