import os
import sys
import math
import random
import ctypes
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Base project directory
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable)))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MAIN_LEVEL_DIR = os.path.join(BASE_DIR, "Main level files")

LEVEL_FILES = {
    1: os.path.join(MAIN_LEVEL_DIR, "Level 1 final.py"),
    2: os.path.join(MAIN_LEVEL_DIR, "Level 2 final"),
    3: os.path.join(MAIN_LEVEL_DIR, "Level 3 final")
}

# Window Configurations
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750

# Game States
STATE_LEVEL_1           = 1
STATE_TRANSITION_1_TO_2 = 2
STATE_LEVEL_2           = 3
STATE_TRANSITION_2_TO_3 = 4
STATE_LEVEL_3           = 5
STATE_VICTORY           = 6

current_state = STATE_LEVEL_1

# Level Namespace Modules
lvl1 = None
lvl2 = None
lvl3 = None

# Transition Screen State
transition_timer = 0
transition_particles = []

# Module loader: runs level file in an isolated namespace (no main/glutMainLoop)
def load_level_module(level_num):
    """Loads and executes a level file in an isolated namespace."""
    file_path = LEVEL_FILES.get(level_num)
    if not file_path or not os.path.isfile(file_path):
        base_names = [f"Level {level_num} final", f"Level {level_num}"]
        candidates = []
        exe_dir = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else BASE_DIR
        for folder in [MAIN_LEVEL_DIR, BASE_DIR, exe_dir]:
            for base_name in base_names:
                candidates.append(os.path.join(folder, f"{base_name}.py"))
                candidates.append(os.path.join(folder, base_name))
        
        found = None
        for cand in candidates:
            if os.path.isfile(cand):
                found = cand
                break
        if found:
            file_path = found
        else:
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
    """Initializes and loads namespaces for Level 1, Level 2, and Level 3."""
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

# Transition particle system
def init_transition_particles(count=90):
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

# 2D drawing helpers for transition screens
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
    total_w = sum(glutBitmapWidth(font, ord(ch)) for ch in text_str)
    start_x = max(20, (WINDOW_WIDTH - total_w) / 2.0)
    render_string_2d(start_x, y, text_str, color=color, font=font)

def render_string_bold(x, y, text_str, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18):
    for dx in [-1.0, 0.0, 1.0]:
        for dy in [-1.0, 0.0, 1.0]:
            render_string_2d(x + dx, y + dy, text_str, color=color, font=font)

# Transition screen renderer
def draw_transition_screen(from_lvl, to_lvl):
    """Renders the animated level transition cutscene between levels."""
    
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

    # 1. Background Grid & Cosmic Particles
    pulse = 0.5 + 0.5 * math.sin(transition_timer * 0.05)
    fast_pulse = 0.5 + 0.5 * math.sin(transition_timer * 0.12)

    # Draw Warp Particles
    for p in transition_particles:
        glColor3f(*p['color'])
        glPointSize(p['size'])
        glBegin(GL_POINTS)
        glVertex2f(p['x'], p['y'])
        glEnd()

        # Particle tail line toward center
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

    # Corner Decorative Marks
    for cx, cy in [(30, 30), (WINDOW_WIDTH - 30, 30), (30, WINDOW_HEIGHT - 30), (WINDOW_WIDTH - 30, WINDOW_HEIGHT - 30)]:
        draw_rect_2d(cx - 8, cy - 8, cx + 8, cy + 8, frame_col)

    # 3. Header Banners
    top_y = WINDOW_HEIGHT - 75
    if from_lvl == 1 and to_lvl == 2:
        badge_text = "* * *   LEVEL 1 CLEARED : THE BACKROOMS CONQUERED   * * *"
        badge_color = (0.2, 1.0, 0.5)
        title_text = "DIMENSIONAL WARP >> SECTOR 2: THE ZOMBIE ARENA"
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

    # Decorative Line Under Header
    glBegin(GL_LINES)
    glColor3f(*title_color)
    glVertex2f(80, top_y - 50)
    glVertex2f(WINDOW_WIDTH - 80, top_y - 50)
    glEnd()

    # 4. Central Information Panels
    panel_left = 65
    panel_right = WINDOW_WIDTH - 65
    panel_top = top_y - 75
    panel_bot = 120

    # Panel dark translucent backing
    draw_rect_2d(panel_left, panel_bot, panel_right, panel_top, (0.04, 0.07, 0.12))
    draw_rect_border_2d(panel_left, panel_bot, panel_right, panel_top, (0.15, 0.35, 0.55), line_width=1.5)

    # Narrative Lore & Story Progression
    lore_y = panel_top - 32
    if from_lvl == 1 and to_lvl == 2:
        lore_lines = [
            ("MISSION REPORT:", (1.0, 0.85, 0.2)),
            ("Tung Tung Tung Sahur has successfully leaped through the Backrooms Exit Portal!", (0.9, 0.95, 1.0)),
            ("You survived treacherous lava pits, phasing tiles, and crushing mechanical walls.", (0.8, 0.85, 0.9)),
            ("", (1, 1, 1)),
            ("CURRENT SITUATION (LEVEL 2):", (1.0, 0.4, 0.4)),
            ("- You have emerged inside an abandoned high-security warehouse arena.", (0.9, 0.95, 1.0)),
            ("- The sector is overrun by 10 mutated Zombies!", (1.0, 0.75, 0.3)),
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
    # Vertically center text inside button box (HELVETICA_18 is ~14px tall, baseline offset ~5px)
    render_string_centered(btn_y + (btn_h - 14) // 2 + 5, prompt_label, color=(1.0, 1.0, 1.0), font=GLUT_BITMAP_HELVETICA_18)

    # 6. Hint Bar

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()

# Level state switchers
def start_transition_1_to_2():
    global current_state, transition_timer
    print("\n" + "=" * 70)
    print(" [*] LEVEL 1 CLEAR! Player passed through the Backrooms Exit Portal!")
    print(" [*] Displaying Transition Screen: Escaping to Level 2 (Zombie Arena)...")
    print("=" * 70 + "\n")
    current_state = STATE_TRANSITION_1_TO_2
    transition_timer = 0
    init_transition_particles(90)
    show_cursor()

def enter_level_2():
    global current_state
    print("\n>> Loading Level 2: Zombie Cat Arena...")
    current_state = STATE_LEVEL_2
    if 'reset_arena' in lvl2:
        lvl2['reset_arena']()
    lvl2['mouse_initialized'] = False
    hide_cursor()

def start_transition_2_to_3():
    global current_state, transition_timer
    print("\n" + "=" * 70)
    print(" [*] LEVEL 2 CLEAR! Player collected Catnip & unlocked North Exit Door!")
    print(" [*] Displaying Transition Screen: Entering Level 3 (Boss Fight)...")
    print("=" * 70 + "\n")
    current_state = STATE_TRANSITION_2_TO_3
    transition_timer = 0
    init_transition_particles(90)
    show_cursor()

def enter_level_3():
    global current_state
    print("\n>> Loading Level 3: The Boss Fight (Evil Larry)...")
    current_state = STATE_LEVEL_3
    if 'reset_level_3' in lvl3:
        lvl3['reset_level_3']()
    lvl3['mouse_initialized'] = False
    hide_cursor()

_user32 = ctypes.windll.user32

is_cursor_hidden = False

def hide_cursor():
    """Aggressively hides mouse cursor (referenced from The House of the Jinns)."""
    global is_cursor_hidden
    if not is_cursor_hidden:
        try:
            while _user32.ShowCursor(False) >= 0:
                pass
            is_cursor_hidden = True
        except:
            pass

def show_cursor():
    """Restores mouse cursor visibility (referenced from The House of the Jinns)."""
    global is_cursor_hidden
    if is_cursor_hidden:
        try:
            while _user32.ShowCursor(True) < 0:
                pass
            is_cursor_hidden = False
        except:
            pass

def update_window_dimensions():
    """
    Dynamically captures the actual client window size on Windows (handling resize, maximize, and full screen)
    without using any restricted GLUT functions like glutGet() or glutReshapeFunc().
    """
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
    try:
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
    except Exception as e:
        print(f"[ERROR in master_display]: {e}")

def master_idle():
    global current_state, transition_timer
    try:
        # -------------------------------------------------------------
        # STATE: LEVEL 1 (Backrooms Maze)
        # -------------------------------------------------------------
        if current_state == STATE_LEVEL_1:
            if lvl1 and 'idle' in lvl1:
                lvl1['idle']()

            # Check Level 1 Exit Portal Gate Condition (Portal at X=70, Z=330)
            pos = lvl1.get('player_pos') if lvl1 else None
            if pos:
                px, py, pz = pos[0], pos[1], pos[2]
                dist_to_portal = math.sqrt((px - 70.0)**2 + (pz - 330.0)**2)
                if (64.0 <= px <= 76.0 and pz >= 318.0) or dist_to_portal <= 9.0:
                    start_transition_1_to_2()

        # -------------------------------------------------------------
        # STATE: TRANSITION 1 -> 2
        # -------------------------------------------------------------
        elif current_state == STATE_TRANSITION_1_TO_2:
            transition_timer += 1
            update_transition_particles()
            glutPostRedisplay()

        # -------------------------------------------------------------
        # STATE: LEVEL 2 (Zombie Cat Arena)
        # -------------------------------------------------------------
        elif current_state == STATE_LEVEL_2:
            if lvl2 and 'idle' in lvl2:
                lvl2['idle']()

            # Check Level 2 Glowing North Exit Door Condition (Door at X=0, Z=59)
            pos = lvl2.get('player_pos') if lvl2 else None
            catnip_picked = lvl2.get('catnip_picked_up', False) if lvl2 else False
            if catnip_picked and pos:
                px, py, pz = pos[0], pos[1], pos[2]
                dist_to_door = math.sqrt((px - 0.0)**2 + (pz - 59.0)**2)
                if (abs(px) <= 6.0 and pz >= 52.0) or dist_to_door <= 7.0:
                    start_transition_2_to_3()

        # -------------------------------------------------------------
        # STATE: TRANSITION 2 -> 3
        # -------------------------------------------------------------
        elif current_state == STATE_TRANSITION_2_TO_3:
            transition_timer += 1
            update_transition_particles()
            glutPostRedisplay()

        # -------------------------------------------------------------
        # STATE: LEVEL 3 (Boss Arena)
        # -------------------------------------------------------------
        elif current_state == STATE_LEVEL_3:
            if lvl3 and 'idle' in lvl3:
                lvl3['idle']()
    except Exception as e:
        print(f"[ERROR in master_idle]: {e}")

def master_keyboard(key, x, y):
    global current_state
    try:
        try:
            raw_ch = key.decode('utf-8')
        except:
            raw_ch = str(key)
        ch = raw_ch.lower()

        # Global Quit: ESC or 'q'
        if key == b'\x1b' or ch == 'q':
            print("\n>> Player exited campaign.")
            sys.exit(0)

        # -------------------------------------------------------------
        # TRANSITION STATE KEY HANDLING (Spacebar / Enter to Proceed)
        # -------------------------------------------------------------
        if current_state == STATE_TRANSITION_1_TO_2:
            if ch in (' ', '\r', '\n') or key in (b' ', b'\r', b'\n'):
                enter_level_2()
            return

        elif current_state == STATE_TRANSITION_2_TO_3:
            if ch in (' ', '\r', '\n') or key in (b' ', b'\r', b'\n'):
                enter_level_3()
            return

        # -------------------------------------------------------------
        # LEVEL KEY ROUTING
        # -------------------------------------------------------------
        if current_state == STATE_LEVEL_1:
            if lvl1 and 'keyboard_listener' in lvl1:
                lvl1['keyboard_listener'](key, x, y)

        elif current_state == STATE_LEVEL_2:
            if lvl2 and 'keyboard_listener' in lvl2:
                lvl2['keyboard_listener'](key, x, y)

        elif current_state == STATE_LEVEL_3:
            if lvl3 and 'keyboard_listener' in lvl3:
                lvl3['keyboard_listener'](key, x, y)
    except Exception as e:
        print(f"[ERROR in master_keyboard]: {e}")

def master_special(key, x, y):
    try:
        if current_state == STATE_LEVEL_1:
            if lvl1 and 'special_key_listener' in lvl1:
                lvl1['special_key_listener'](key, x, y)
        elif current_state == STATE_LEVEL_2:
            if lvl2 and 'special_key_listener' in lvl2:
                lvl2['special_key_listener'](key, x, y)
        elif current_state == STATE_LEVEL_3:
            if lvl3 and 'special_key_listener' in lvl3:
                lvl3['special_key_listener'](key, x, y)
    except Exception as e:
        print(f"[ERROR in master_special]: {e}")

def master_mouse(button, state, x, y):
    try:
        # Also allow mouse click on transition screen to proceed
        if state == GLUT_DOWN:
            if current_state == STATE_TRANSITION_1_TO_2:
                enter_level_2()
                return
            elif current_state == STATE_TRANSITION_2_TO_3:
                enter_level_3()
                return

        if current_state == STATE_LEVEL_1:
            if lvl1 and 'mouse_listener' in lvl1:
                lvl1['mouse_listener'](button, state, x, y)
        elif current_state == STATE_LEVEL_2:
            if lvl2 and 'mouse_listener' in lvl2:
                lvl2['mouse_listener'](button, state, x, y)
        elif current_state == STATE_LEVEL_3:
            if lvl3 and 'mouse_listener' in lvl3:
                lvl3['mouse_listener'](button, state, x, y)
    except Exception as e:
        print(f"[ERROR in master_mouse]: {e}")

def master_motion(x, y):
    try:
        if current_state == STATE_LEVEL_1:
            if lvl1 and 'mouse_motion' in lvl1:
                lvl1['mouse_motion'](x, y)
        elif current_state == STATE_LEVEL_2:
            if lvl2 and 'mouse_motion' in lvl2:
                lvl2['mouse_motion'](x, y)
        elif current_state == STATE_LEVEL_3:
            if lvl3 and 'mouse_motion' in lvl3:
                lvl3['mouse_motion'](x, y)
    except Exception as e:
        pass

def master_passive_motion(x, y):
    try:
        if current_state == STATE_LEVEL_1:
            if lvl1 and 'passive_motion' in lvl1:
                lvl1['passive_motion'](x, y)
            elif lvl1 and 'mouse_motion' in lvl1:
                lvl1['mouse_motion'](x, y)
        elif current_state == STATE_LEVEL_2:
            if lvl2 and 'passive_motion' in lvl2:
                lvl2['passive_motion'](x, y)
            elif lvl2 and 'mouse_motion' in lvl2:
                lvl2['mouse_motion'](x, y)
        elif current_state == STATE_LEVEL_3:
            if lvl3 and 'passive_motion' in lvl3:
                lvl3['passive_motion'](x, y)
            elif lvl3 and 'mouse_motion' in lvl3:
                lvl3['mouse_motion'](x, y)
    except Exception as e:
        pass

# Campaign entry point
def run_campaign():
    """Launches the 3-level campaign in a single unified OpenGL window."""
    print("\n9 LIVES: EVIL CAT WORLD - starting campaign...\n")
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"9 Lives")

    init_all_levels()
    hide_cursor()

    glutDisplayFunc(master_display)
    glutIdleFunc(master_idle)
    glutKeyboardFunc(master_keyboard)
    glutSpecialFunc(master_special)
    glutMouseFunc(master_mouse)
    glutMotionFunc(master_motion)
    glutPassiveMotionFunc(master_passive_motion)

    print(">> Game started! Starting Level 1...")
    glutMainLoop()

if __name__ == "__main__":
    run_campaign()
