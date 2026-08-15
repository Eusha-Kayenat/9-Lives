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
player_yaw = 0.0                  # Facing angle in degrees (0 = along +Z)
player_pitch = 0.0                # Pitch angle looking up/down
player_speed = 0.45               # Movement speed factor
crouching = False                 # Crouch state
eye_height = 1.6                  # Standing eye height

# Jump Physics Parameters
is_jumping = False
y_velocity = 0.0
gravity = -0.016
jump_strength = 0.36
ground_y = 1.0                    # Floor level Y height

# Camera Settings
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

    # 3. Hazard Pit Chamber Floor (X: 34.4 -> 45.6, Z: 60 -> 120, smoothly bridging around pits)
    glPushMatrix()
    glTranslatef(40.0, -0.1, 74.0)
    draw_box(11.2, 0.2, 16.0, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(40.0, -0.1, 98.0)
    draw_box(11.2, 0.2, 16.0, color_top=COLOR_FLOOR, color_side=COLOR_FLOOR_SIDE)
    glPopMatrix()

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
    wall(19.6, 3.5, 65.6, 52.8, 7.0, 0.8)           # North Wall (X: -6.4 -> 46.0)
    wall(20.4, 3.5, 54.4, 28.8, 7.0, 0.8)           # South Wall (X: 6.4 -> 34.8)

    # 3. Hazard Pit Corridor Walls (Z: 60 -> 120)
    wall(34.4, 3.5, 84.4, 0.8, 7.0, 60.8)           # West Wall
    wall(45.6, 3.5, 92.8, 0.8, 7.0, 54.4)           # East Wall

    # 4. Turn 2 Junction Walls (Connected to Long Backrooms Corridor B)
    wall(45.6, 3.5, 120.0, 0.8, 7.0, 12.0)          # East end cap of Junction B
    wall(0.0, 3.5, 125.6, 92.0, 7.0, 0.8)           # North Wall (X: -46.0 -> +46.0)
    wall(0.0, 3.5, 114.4, 69.6, 7.0, 0.8)           # South Wall (X: -34.8 -> +34.8)

    # 5. Disappearing Chamber Walls (Z: 120 -> 180)
    wall(-45.6, 3.5, 150.0, 0.8, 7.0, 62.0)          # West Wall (X: -45.6)
    wall(-34.4, 3.5, 147.2, 0.8, 7.0, 56.0)          # East Wall (X: -34.4)

    # 6. Turn 3 Junction Walls (Connected to Corridor C)
    wall(-45.6, 3.5, 180.0, 0.8, 7.0, 12.0)          # West end cap of Junction C
    wall(-10.0, 3.5, 185.6, 72.0, 7.0, 0.8)          # North Wall (X: -46.0 -> 26.0)
    wall(-10.0, 3.5, 174.4, 50.0, 7.0, 0.8)          # South Wall (X: -34.4 -> 15.6)

    # 7. Laser Gauntlet Corridor Walls (Z: 180 -> 240)
    wall(14.4, 3.5, 210.0, 0.8, 7.0, 50.0)           # West Wall
    wall(25.6, 3.5, 210.0, 0.8, 7.0, 62.0)           # East Wall

    # 8. Turn 4 Junction Walls (Connected to Corridor D)
    wall(45.0, 3.5, 234.4, 62.0, 7.0, 0.8)          # South Wall (X: 14.4 -> 76.0)
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
    Draws Section 2 (X: 40, Z: 60 -> 120): Recessed lava hazard pits.
    """
    glPushMatrix()
    glTranslatef(40.0, -1.5, 86.0)
    draw_box(10.0, 3.0, 8.0, color_top=(0.05, 0.05, 0.05), color_side=(0.15, 0.05, 0.05))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(40.0, -2.8, 86.0)
    draw_box(9.6, 0.1, 7.6, color_top=COLOR_LAVA, color_side=(0.7, 0.1, 0.0))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(40.0, -1.5, 110.0)
    draw_box(10.0, 3.0, 8.0, color_top=(0.05, 0.05, 0.05), color_side=(0.15, 0.05, 0.05))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(40.0, -2.8, 110.0)
    draw_box(9.6, 0.1, 7.6, color_top=COLOR_LAVA, color_side=(0.7, 0.1, 0.0))
    glPopMatrix()

    for pz in [81.5, 90.5, 105.5, 114.5]:
        glPushMatrix()
        glTranslatef(40.0, 0.03, pz)
        draw_box(10.0, 0.04, 0.6, color_top=COLOR_HAZARD_STRIPE, color_side=(0.6, 0.5, 0.0))
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
    Configures perspective projection and positions camera in 1st or 3rd person mode.
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

        target_x = cam_x + math.sin(rad_yaw) * math.cos(rad_pitch)
        target_y = cam_y + math.sin(rad_pitch)
        target_z = cam_z + math.cos(rad_yaw) * math.cos(rad_pitch)

        gluLookAt(cam_x, cam_y, cam_z,
                  target_x, target_y, target_z,
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
    draw_text(15, WINDOW_HEIGHT - 130, f"State: {'CROUCHING (Hitbox Height = 0.8)' if crouching else 'STANDING (Hitbox Height = 1.6)'}")
    draw_text(15, 20, "Controls: WASD/Arrows: Move/Turn | SPACE: Jump | C/Ctrl: Crouch | V: Camera | R: Reset")

    glutSwapBuffers()

# -----------------------------------------------------------------------------
# Physics & Animation Loop
# -----------------------------------------------------------------------------
def update_player_physics():
    """
    Handles player jumping physics, gravity update, and floor collision.
    """
    global player_pos, is_jumping, y_velocity

    if is_jumping:
        player_pos[1] += y_velocity
        y_velocity += gravity
        if player_pos[1] <= ground_y:
            player_pos[1] = ground_y
            is_jumping = False
            y_velocity = 0.0

def idle():
    """
    Idle Callback: Updates player physics and scaffolding animations.
    """
    global moving_walls_offset, moving_walls_dir, platform_timer, disappearing_tiles_active

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
def keyboard_listener(key, x, y):
    """
    Handles WASD, Spacebar, C, V, M, T, R, and ESC keys.
    """
    global player_pos, player_yaw, crouching, first_person, anim_moving_walls, anim_disappearing_floor
    global is_jumping, y_velocity

    try:
        ch = key.decode('utf-8').lower()
    except:
        ch = str(key).lower()

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

    # Jump Action: Spacebar
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

    # ESC Key to Exit
    elif key == b'\x1b':
        try:
            glutLeaveMainLoop()
        except:
            sys.exit(0)

    glutPostRedisplay()

def special_key_listener(key, x, y):
    """
    Handles Arrow Keys (Up/Down for move forward/backward, Left/Right for turn yaw) and Left Ctrl.
    """
    global player_pos, player_yaw, crouching
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
    Handles mouse clicks (Right Click toggles Camera view).
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

    # Register GLUT Callbacks
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
