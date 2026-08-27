# 🐈 9 Lives

**A 3-act 3D adventure built from scratch in raw OpenGL — no game engine, just math, patience, and a cat with nine chances to get it right.**

You play as **tung tung tung sahur**, escaping a Backrooms-style maze, surviving a zombie siege, and finally facing down a boss named **Evil Larry** — all rendered with hand-written matrix transforms, custom collision, and zero external physics or rendering libraries.

---

## 🎮 The Three Acts

### Level 1 — *Foundations of Movement*
A sprawling, **100% seamlessly connected** maze — no loading zones, no invisible walls, every corridor physically joins the next.

> Start Hub → Corner Turn → Hazard Pits → Long Backrooms Corridor → Disappearing Floor Void → Laser Gauntlet → Moving Walls → Exit Portal

- Full 3D movement with jump physics, crouching, and wall-sliding collision
- Environmental hazards: molten lava pits, timed disappearing platforms, sweeping laser emitters, and walls that physically close in on you
- Toggle between first-person and third-person on the fly

### Level 2 — *Combat, Projectiles & Tactical Crates*
The maze gives way to an arena. Zombies are inbound.

- Manual aim-and-shoot combat — nothing auto-fires, every grenade is on you
- Crates you can hide behind that block both movement **and** line-of-sight (real raycasting, not a simple distance check)
- Defeat 10 zombies to unlock **Catnip** — a second weapon that *charms* rather than kills
- A crosshair that turns red the instant you're actually on target

### Level 3 — *The Boss Fight*
Evil Larry has two health bars — one for HP, one for his ash shield — and he's not fighting alone.

- Minion "Small Larries" swarm while the shield holds
- Charm them with Catnip and they'll turn on their own boss, chipping the shield down section by section
- The instant the shield breaks, every remaining minion vanishes — the fight becomes a straight duel

---

## 🕹️ Controls

| Action | Key |
|---|---|
| Move | `W` `A` `S` `D` |
| Look | Mouse |
| Jump | `Space` |
| Crouch | `Ctrl` |
| Camera Toggle (1st / 3rd person) | `V` / Right-click |
| Fire weapon | Left-click |
| Switch weapon (Gun ↔ Catnip) | `F` |
| Pause | `P` |
| Reset | `R` |
| Quit | `Esc` |

---

## 🛠️ Built With

Pure **PyOpenGL** — `GL`, `GLUT`, and `GLU` only. Every wall, hazard, weapon arc, and boss health bar is hand-built from primitive shapes and manual transforms, with custom-written collision detection, projectile physics, and camera systems throughout — no physics engine, no external rendering framework.

## 🚀 Running the Game

```bash
pip install PyOpenGL PyOpenGL_accelerate
python Level_1_final.py
```

Clear a level, then move on to `Level_2_final.py` and `Level_3_final.py` to continue the story.

---

*A CSE423 Computer Graphics project — built one `glTranslatef` at a time.*
