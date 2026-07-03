# Eclipse Depths - Enemy sprite drawing functions

import pygame
import math


def _shadow(surface, w, h):
    s = pygame.Surface((w, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 55), (2, 1, w - 4, 6))
    surface.blit(s, (0, h - 5))


def draw_slime(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    _shadow(surface, w, h)
    bob = int(math.sin(t * 4) * 2)
    # Body
    body_col = (50, 210, 90)
    pygame.draw.ellipse(surface, (30, 140, 60), (3, 8 + bob, w - 6, h - 12))
    pygame.draw.ellipse(surface, body_col, (4, 6 + bob, w - 8, h - 14))
    # Shine blob
    pygame.draw.ellipse(surface, (120, 255, 150, 160), (7, 7 + bob, 8, 5))
    # Eyes
    pygame.draw.circle(surface, (10, 60, 20), (w // 2 - 4, h // 2 - 1 + bob), 3)
    pygame.draw.circle(surface, (10, 60, 20), (w // 2 + 4, h // 2 - 1 + bob), 3)
    pygame.draw.circle(surface, (200, 255, 200), (w // 2 - 3, h // 2 - 2 + bob), 1)
    pygame.draw.circle(surface, (200, 255, 200), (w // 2 + 5, h // 2 - 2 + bob), 1)
    # Mouth
    pygame.draw.arc(surface, (10, 80, 30),
                    pygame.Rect(w // 2 - 4, h // 2 + 2 + bob, 8, 5), 3.14, 0, 2)
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_goblin(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    _shadow(surface, w, h)
    skin = (100, 160, 60)
    dark = (65, 110, 35)
    # Legs
    pygame.draw.rect(surface, dark, (w // 2 - 7, h - 10, 5, 8), border_radius=2)
    pygame.draw.rect(surface, dark, (w // 2 + 2, h - 10, 5, 8), border_radius=2)
    # Body / tunic
    pygame.draw.ellipse(surface, (90, 70, 40), (w // 2 - 8, h // 2, 16, h // 2 - 4))
    pygame.draw.ellipse(surface, (120, 95, 55), (w // 2 - 7, h // 2 + 2, 14, h // 2 - 8))
    # Arms
    pygame.draw.ellipse(surface, skin, (1, h // 2, 6, 10))
    pygame.draw.ellipse(surface, skin, (w - 7, h // 2, 6, 10))
    # Hands with claws
    for cx, cy in [(2, h // 2 + 8), (w - 3, h // 2 + 8)]:
        pygame.draw.circle(surface, skin, (cx, cy), 3)
        pygame.draw.line(surface, (200, 200, 180), (cx - 1, cy + 2), (cx - 2, cy + 5), 1)
        pygame.draw.line(surface, (200, 200, 180), (cx + 1, cy + 2), (cx + 2, cy + 5), 1)
    # Head
    pygame.draw.circle(surface, skin, (w // 2, h // 2 - 2), 9)
    # Ears (pointy)
    pygame.draw.polygon(surface, skin, [(w // 2 - 9, h // 2 - 4),
                                         (w // 2 - 14, h // 2 - 10),
                                         (w // 2 - 6, h // 2 - 1)])
    pygame.draw.polygon(surface, skin, [(w // 2 + 9, h // 2 - 4),
                                         (w // 2 + 14, h // 2 - 10),
                                         (w // 2 + 6, h // 2 - 1)])
    # Eyes
    pygame.draw.circle(surface, (255, 60, 30), (w // 2 - 3, h // 2 - 3), 2)
    pygame.draw.circle(surface, (255, 60, 30), (w // 2 + 3, h // 2 - 3), 2)
    pygame.draw.circle(surface, (255, 200, 50), (w // 2 - 2, h // 2 - 4), 1)
    pygame.draw.circle(surface, (255, 200, 50), (w // 2 + 4, h // 2 - 4), 1)
    # Nose
    pygame.draw.circle(surface, dark, (w // 2, h // 2), 2)
    # Teeth
    pygame.draw.rect(surface, (240, 240, 220), (w // 2 - 3, h // 2 + 3, 3, 3))
    pygame.draw.rect(surface, (240, 240, 220), (w // 2 + 1, h // 2 + 3, 3, 3))
    # Mohawk
    pygame.draw.polygon(surface, (40, 30, 10),
                         [(w // 2 - 3, h // 2 - 10),
                          (w // 2, h // 2 - 18),
                          (w // 2 + 3, h // 2 - 10)])
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_skeleton(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    _shadow(surface, w, h)
    bone = (215, 215, 195)
    dark_bone = (160, 160, 140)
    # Legs (bones)
    pygame.draw.rect(surface, bone, (w // 2 - 6, h - 12, 4, 10), border_radius=2)
    pygame.draw.rect(surface, bone, (w // 2 + 2, h - 12, 4, 10), border_radius=2)
    pygame.draw.circle(surface, bone, (w // 2 - 4, h - 12), 3)
    pygame.draw.circle(surface, bone, (w // 2 + 4, h - 12), 3)
    # Ribcage
    for i in range(4):
        y = h // 2 + i * 4
        pygame.draw.line(surface, bone, (w // 2 - 7, y), (w // 2 + 7, y), 2)
        pygame.draw.line(surface, dark_bone, (w // 2 - 7, y + 1), (w // 2 + 7, y + 1), 1)
    # Spine
    pygame.draw.line(surface, bone, (w // 2, h // 3), (w // 2, h - 12), 2)
    # Arms (bone style)
    pygame.draw.line(surface, bone, (w // 2 - 7, h // 2 + 2), (2, h // 2 + 8), 3)
    pygame.draw.line(surface, bone, (w // 2 + 7, h // 2 + 2), (w - 2, h // 2 + 8), 3)
    pygame.draw.circle(surface, bone, (2, h // 2 + 8), 3)
    pygame.draw.circle(surface, bone, (w - 2, h // 2 + 8), 3)
    # Skull
    pygame.draw.circle(surface, bone, (w // 2, h // 4 + 2), 9)
    pygame.draw.ellipse(surface, bone, (w // 2 - 7, h // 4 - 3, 14, 8))
    # Jaw
    pygame.draw.rect(surface, dark_bone, (w // 2 - 5, h // 4 + 5, 10, 5), border_radius=2)
    # Eye sockets
    pygame.draw.circle(surface, (20, 20, 30), (w // 2 - 3, h // 4 + 1), 3)
    pygame.draw.circle(surface, (20, 20, 30), (w // 2 + 3, h // 4 + 1), 3)
    # Glowing eyes
    pygame.draw.circle(surface, (80, 200, 255), (w // 2 - 3, h // 4 + 1), 2)
    pygame.draw.circle(surface, (80, 200, 255), (w // 2 + 3, h // 4 + 1), 2)
    # Teeth
    for tx in range(w // 2 - 4, w // 2 + 5, 2):
        pygame.draw.rect(surface, bone, (tx, h // 4 + 7, 2, 3))
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_archer(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    _shadow(surface, w, h)
    skin = (200, 160, 110)
    cloth = (130, 100, 50)
    # Legs
    pygame.draw.rect(surface, (80, 60, 30), (w // 2 - 6, h - 10, 5, 8), border_radius=2)
    pygame.draw.rect(surface, (80, 60, 30), (w // 2 + 1, h - 10, 5, 8), border_radius=2)
    # Body
    pygame.draw.ellipse(surface, cloth, (w // 2 - 8, h // 2, 16, h // 2 - 4))
    # Quiver on back
    pygame.draw.rect(surface, (100, 70, 30), (w - 7, h // 2 - 4, 5, 14), border_radius=2)
    for ay in range(h // 2 - 2, h // 2 + 8, 3):
        pygame.draw.line(surface, (200, 180, 80), (w - 5, ay), (w - 5, ay + 2), 1)
    # Bow in left hand
    pygame.draw.arc(surface, (120, 90, 40),
                    pygame.Rect(2, h // 2 - 6, 8, 14), -0.8, 0.8, 2)
    pygame.draw.line(surface, (200, 200, 180), (5, h // 2 - 5), (5, h // 2 + 8), 1)
    # Arms
    pygame.draw.ellipse(surface, skin, (2, h // 2, 7, 9))
    pygame.draw.ellipse(surface, skin, (w - 9, h // 2, 7, 9))
    # Head
    pygame.draw.circle(surface, skin, (w // 2, h // 2 - 3), 8)
    # Hood
    pygame.draw.ellipse(surface, (100, 80, 40), (w // 2 - 7, h // 2 - 11, 14, 9))
    # Eyes
    pygame.draw.circle(surface, (50, 40, 30), (w // 2 - 3, h // 2 - 4), 2)
    pygame.draw.circle(surface, (50, 40, 30), (w // 2 + 3, h // 2 - 4), 2)
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_bat(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    flap = math.sin(t * 8) * 4
    # Wings
    wing_col = (70, 40, 100)
    pygame.draw.polygon(surface, wing_col,
                         [(w // 2, h // 2),
                          (0, h // 2 - 6 + int(flap)),
                          (2, h // 2 + 4)])
    pygame.draw.polygon(surface, wing_col,
                         [(w // 2, h // 2),
                          (w, h // 2 - 6 + int(flap)),
                          (w - 2, h // 2 + 4)])
    pygame.draw.polygon(surface, (90, 55, 130),
                         [(w // 2, h // 2),
                          (4, h // 2 - 3 + int(flap)),
                          (w // 2 - 4, h // 2 + 2)])
    pygame.draw.polygon(surface, (90, 55, 130),
                         [(w // 2, h // 2),
                          (w - 4, h // 2 - 3 + int(flap)),
                          (w // 2 + 4, h // 2 + 2)])
    # Body
    pygame.draw.ellipse(surface, (55, 35, 75), (w // 2 - 5, h // 2 - 5, 10, 10))
    pygame.draw.ellipse(surface, (75, 50, 100), (w // 2 - 4, h // 2 - 6, 8, 8))
    # Eyes
    pygame.draw.circle(surface, (255, 50, 50), (w // 2 - 2, h // 2 - 3), 2)
    pygame.draw.circle(surface, (255, 50, 50), (w // 2 + 2, h // 2 - 3), 2)
    pygame.draw.circle(surface, (255, 200, 50), (w // 2 - 1, h // 2 - 4), 1)
    pygame.draw.circle(surface, (255, 200, 50), (w // 2 + 3, h // 2 - 4), 1)
    # Ears
    pygame.draw.polygon(surface, (55, 35, 75),
                         [(w // 2 - 4, h // 2 - 6),
                          (w // 2 - 6, h // 2 - 11),
                          (w // 2 - 1, h // 2 - 6)])
    pygame.draw.polygon(surface, (55, 35, 75),
                         [(w // 2 + 4, h // 2 - 6),
                          (w // 2 + 6, h // 2 - 11),
                          (w // 2 + 1, h // 2 - 6)])
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_wizard(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    _shadow(surface, w, h)
    robe = (80, 60, 180)
    dark_robe = (50, 35, 120)
    # Robe base
    pygame.draw.ellipse(surface, dark_robe, (4, h // 3, w - 8, h * 2 // 3 - 4))
    pygame.draw.ellipse(surface, robe, (5, h // 3 - 2, w - 10, h * 2 // 3 - 6))
    # Rune/star on robe
    cx, cy = w // 2, h * 2 // 3
    pygame.draw.circle(surface, (150, 100, 255), (cx, cy), 4)
    for star_a in range(0, 360, 60):
        sx = cx + int(math.cos(math.radians(star_a)) * 4)
        sy = cy + int(math.sin(math.radians(star_a)) * 4)
        pygame.draw.line(surface, (200, 150, 255), (cx, cy), (sx, sy), 1)
    # Staff in right hand
    pygame.draw.line(surface, (120, 90, 50), (w - 4, h // 4), (w - 4, h - 4), 2)
    # Orb on staff
    orb_r = 5
    pygame.draw.circle(surface, (100, 60, 200), (w - 4, h // 4), orb_r)
    pygame.draw.circle(surface, (180, 130, 255), (w - 4, h // 4), orb_r - 1)
    pygame.draw.circle(surface, (220, 200, 255), (w - 5, h // 4 - 2), 2)
    # Arms
    pygame.draw.ellipse(surface, robe, (1, h // 3 + 2, 7, 10))
    pygame.draw.ellipse(surface, robe, (w - 8, h // 3 + 2, 7, 10))
    # Head
    pygame.draw.circle(surface, (200, 170, 130), (w // 2, h // 3 - 2), 8)
    # Beard
    pygame.draw.ellipse(surface, (220, 220, 210), (w // 2 - 4, h // 3 + 3, 8, 6))
    # Hat
    pygame.draw.polygon(surface, dark_robe,
                         [(w // 2, h // 3 - 16),
                          (w // 2 - 9, h // 3 - 5),
                          (w // 2 + 9, h // 3 - 5)])
    pygame.draw.ellipse(surface, robe, (w // 2 - 11, h // 3 - 7, 22, 5))
    # Eyes
    pygame.draw.circle(surface, (180, 120, 255), (w // 2 - 3, h // 3 - 2), 2)
    pygame.draw.circle(surface, (180, 120, 255), (w // 2 + 3, h // 3 - 2), 2)
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_ghost(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    bob = math.sin(t * 2) * 3
    # Ghost body glow
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (150, 180, 255, 60), (0, int(bob), w, h - 4))
    surface.blit(glow, (0, 0))
    # Body
    pygame.draw.ellipse(surface, (180, 200, 255, 200), (3, 2 + int(bob), w - 6, h * 2 // 3))
    # Wavy bottom
    for i in range(3):
        bx = 3 + i * (w - 6) // 3
        by = 2 + int(bob) + h * 2 // 3 - 4
        pygame.draw.ellipse(surface, (180, 200, 255, 200), (bx, by, (w - 6) // 3, 8))
    # Eyes (glowing)
    pygame.draw.ellipse(surface, (20, 20, 60), (w // 2 - 7, h // 3 + int(bob), 6, 7))
    pygame.draw.ellipse(surface, (20, 20, 60), (w // 2 + 1, h // 3 + int(bob), 6, 7))
    pygame.draw.ellipse(surface, (100, 150, 255), (w // 2 - 6, h // 3 + 1 + int(bob), 4, 5))
    pygame.draw.ellipse(surface, (100, 150, 255), (w // 2 + 2, h // 3 + 1 + int(bob), 4, 5))
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_spider(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    _shadow(surface, w, h)
    body_col = (60, 30, 15)
    # Legs
    for i in range(4):
        leg_y = h // 2 + (i - 2) * 5
        angle = math.sin(t * 5 + i) * 0.3
        # Left legs
        lx = w // 2 - 8
        pygame.draw.line(surface, body_col, (lx, leg_y),
                         (lx - 10 - int(math.cos(angle) * 4),
                          leg_y + 6 + int(math.sin(angle) * 3)), 2)
        # Right legs
        rx = w // 2 + 8
        pygame.draw.line(surface, body_col, (rx, leg_y),
                         (rx + 10 + int(math.cos(angle) * 4),
                          leg_y + 6 + int(math.sin(angle) * 3)), 2)
    # Abdomen
    pygame.draw.ellipse(surface, (80, 40, 20), (w // 2 - 7, h // 2 + 2, 14, 10))
    pygame.draw.ellipse(surface, (100, 55, 25), (w // 2 - 6, h // 2 + 3, 12, 8))
    # Hourglass mark
    pygame.draw.polygon(surface, (220, 40, 40),
                         [(w // 2, h // 2 + 5), (w // 2 - 3, h // 2 + 8),
                          (w // 2 + 3, h // 2 + 8)])
    # Head
    pygame.draw.circle(surface, body_col, (w // 2, h // 2 - 2), 7)
    pygame.draw.circle(surface, (90, 50, 25), (w // 2, h // 2 - 2), 6)
    # 6 eyes
    for ex, ey in [(-4, -5), (0, -6), (4, -5), (-5, -2), (5, -2), (0, -2)]:
        pygame.draw.circle(surface, (255, 50, 50),
                           (w // 2 + ex, h // 2 + ey), 1)
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_dark_knight(surface: pygame.Surface, t: float = 0, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    _shadow(surface, w, h)
    armor = (45, 38, 65)
    highlight = (80, 65, 110)
    trim = (180, 140, 255)
    # Legs (armoured)
    for lx in [w // 2 - 7, w // 2 + 2]:
        pygame.draw.rect(surface, armor, (lx, h - 13, 6, 11), border_radius=2)
        pygame.draw.rect(surface, highlight, (lx + 1, h - 13, 4, 5), border_radius=1)
    # Body armour
    pygame.draw.rect(surface, armor, (w // 2 - 10, h // 3, 20, h // 2), border_radius=3)
    pygame.draw.rect(surface, highlight, (w // 2 - 9, h // 3 + 1, 18, h // 4), border_radius=2)
    # Chest plate symbol
    pygame.draw.rect(surface, trim, (w // 2 - 3, h // 3 + 4, 6, 8), border_radius=1)
    # Pauldrons (shoulder armour)
    pygame.draw.ellipse(surface, armor, (w // 2 - 13, h // 3, 8, 6))
    pygame.draw.ellipse(surface, armor, (w // 2 + 5, h // 3, 8, 6))
    pygame.draw.ellipse(surface, highlight, (w // 2 - 12, h // 3, 6, 4))
    pygame.draw.ellipse(surface, highlight, (w // 2 + 6, h // 3, 6, 4))
    # Arms
    pygame.draw.rect(surface, armor, (w // 2 - 14, h // 3 + 4, 6, 12), border_radius=2)
    pygame.draw.rect(surface, armor, (w // 2 + 8, h // 3 + 4, 6, 12), border_radius=2)
    # Sword
    pygame.draw.rect(surface, (200, 200, 220), (w // 2 + 13, h // 3 - 8, 3, 20), border_radius=1)
    pygame.draw.rect(surface, trim, (w // 2 + 10, h // 3 + 2, 9, 3))
    # Shield
    pygame.draw.polygon(surface, armor,
                         [(w // 2 - 16, h // 3 + 2),
                          (w // 2 - 11, h // 3 - 2),
                          (w // 2 - 11, h // 3 + 12),
                          (w // 2 - 16, h // 3 + 16)])
    pygame.draw.polygon(surface, trim,
                         [(w // 2 - 15, h // 3 + 3),
                          (w // 2 - 12, h // 3 + 1),
                          (w // 2 - 12, h // 3 + 11),
                          (w // 2 - 15, h // 3 + 14)])
    # Helmet
    pygame.draw.rect(surface, armor, (w // 2 - 9, h // 4 - 5, 18, 14), border_radius=4)
    pygame.draw.rect(surface, highlight, (w // 2 - 8, h // 4 - 4, 16, 6), border_radius=3)
    # Visor slit
    pygame.draw.rect(surface, (0, 0, 0), (w // 2 - 6, h // 4 + 2, 12, 3))
    # Glowing visor eyes
    pygame.draw.circle(surface, (150, 80, 255), (w // 2 - 3, h // 4 + 3), 2)
    pygame.draw.circle(surface, (150, 80, 255), (w // 2 + 3, h // 4 + 3), 2)
    # Helmet plume
    for py_i in range(4):
        pygame.draw.ellipse(surface, trim,
                            (w // 2 - 3, h // 4 - 9 - py_i * 2, 6, 5))
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 160))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
