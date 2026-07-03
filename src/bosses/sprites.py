# Eclipse Depths - Boss sprite drawing functions

import pygame
import math


def draw_skeleton_king(surface: pygame.Surface, t: float = 0,
                       phase: int = 1, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    bone = (225, 220, 200)
    crown_col = (255, 200, 40)
    cape_col = (140, 20, 20) if phase == 1 else (200, 30, 30)
    # Cape
    pygame.draw.ellipse(surface, cape_col, (3, h // 3, w - 6, h * 2 // 3))
    pygame.draw.ellipse(surface, (100, 15, 15), (4, h // 3 + 2, w - 8, h * 2 // 3 - 4))
    # Ribcage
    for i in range(5):
        y = h // 2 + i * 5
        pygame.draw.line(surface, bone, (w // 2 - 10, y), (w // 2 + 10, y), 2)
    # Spine
    pygame.draw.line(surface, bone, (w // 2, h // 3), (w // 2, h - 10), 2)
    # Arms with bones
    for side in [-1, 1]:
        ax = w // 2 + side * 9
        pygame.draw.line(surface, bone, (ax, h // 2), (w // 2 + side * 18, h // 2 + 10), 3)
        pygame.draw.circle(surface, bone, (w // 2 + side * 18, h // 2 + 10), 3)
        # Claw fingers
        for f_i in range(3):
            fx = w // 2 + side * (17 + f_i)
            pygame.draw.line(surface, bone, (fx, h // 2 + 10),
                             (fx + side * 3, h // 2 + 14), 1)
    # Skull
    pygame.draw.circle(surface, bone, (w // 2, h // 4 + 2), 12)
    pygame.draw.ellipse(surface, bone, (w // 2 - 10, h // 4 - 4, 20, 10))
    # Jaw
    pygame.draw.rect(surface, (180, 175, 155), (w // 2 - 7, h // 4 + 7, 14, 7), border_radius=2)
    for tx in range(w // 2 - 6, w // 2 + 6, 3):
        pygame.draw.rect(surface, bone, (tx, h // 4 + 9, 2, 4))
    # Eye sockets with glow
    glow_col = (255, 100, 50) if phase == 1 else (255, 50, 200)
    pygame.draw.circle(surface, (20, 15, 30), (w // 2 - 4, h // 4 + 1), 4)
    pygame.draw.circle(surface, (20, 15, 30), (w // 2 + 4, h // 4 + 1), 4)
    pygame.draw.circle(surface, glow_col, (w // 2 - 4, h // 4 + 1), 3)
    pygame.draw.circle(surface, glow_col, (w // 2 + 4, h // 4 + 1), 3)
    pygame.draw.circle(surface, (255, 255, 200), (w // 2 - 4, h // 4), 1)
    pygame.draw.circle(surface, (255, 255, 200), (w // 2 + 4, h // 4), 1)
    # Crown
    crown_pts = [(w // 2 - 10, h // 4 - 10),
                 (w // 2 - 7, h // 4 - 16),
                 (w // 2 - 4, h // 4 - 11),
                 (w // 2, h // 4 - 18),
                 (w // 2 + 4, h // 4 - 11),
                 (w // 2 + 7, h // 4 - 16),
                 (w // 2 + 10, h // 4 - 10)]
    pygame.draw.lines(surface, crown_col, False, crown_pts, 3)
    pygame.draw.line(surface, crown_col,
                     (w // 2 - 10, h // 4 - 10), (w // 2 + 10, h // 4 - 10), 3)
    # Jewels on crown
    for jx, jc in [(w // 2 - 7, (255, 50, 50)),
                   (w // 2, (80, 200, 255)),
                   (w // 2 + 7, (255, 50, 50))]:
        pygame.draw.circle(surface, jc, (jx, h // 4 - 11), 2)
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 180))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_fire_dragon(surface: pygame.Surface, t: float = 0,
                     phase: int = 1, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    scale_col = (200, 70, 20)
    belly_col = (240, 140, 40)
    dark_scale = (140, 40, 10)
    # Tail
    tail_pts = [(w // 2 + 5, h - 6),
                (w * 3 // 4, h - 10 + int(math.sin(t * 2) * 4)),
                (w - 4, h - 20 + int(math.sin(t * 2 + 1) * 3)),
                (w - 2, h - 30)]
    pygame.draw.lines(surface, scale_col, False, tail_pts, 5)
    pygame.draw.lines(surface, dark_scale, False, tail_pts, 2)
    # Wings
    wing_flap = int(math.sin(t * 3) * 6)
    pygame.draw.polygon(surface, (160, 50, 15),
                         [(w // 2 - 4, h // 3),
                          (0, h // 3 - 14 + wing_flap),
                          (4, h // 3 + 6),
                          (w // 2 - 8, h // 3 + 4)])
    pygame.draw.polygon(surface, (160, 50, 15),
                         [(w // 2 + 4, h // 3),
                          (w, h // 3 - 14 + wing_flap),
                          (w - 4, h // 3 + 6),
                          (w // 2 + 8, h // 3 + 4)])
    # Wing membrane lines
    for i in range(3):
        pygame.draw.line(surface, (120, 35, 10),
                         (w // 2 - 4, h // 3),
                         (2 + i * 4, h // 3 - 10 + wing_flap), 1)
        pygame.draw.line(surface, (120, 35, 10),
                         (w // 2 + 4, h // 3),
                         (w - 2 - i * 4, h // 3 - 10 + wing_flap), 1)
    # Body
    pygame.draw.ellipse(surface, scale_col, (w // 2 - 12, h // 3, 24, h // 2))
    pygame.draw.ellipse(surface, dark_scale, (w // 2 - 11, h // 3, 22, h // 2), 2)
    # Scale pattern
    for i in range(3):
        pygame.draw.arc(surface, dark_scale,
                        pygame.Rect(w // 2 - 10, h // 3 + 6 + i * 8, 20, 10),
                        0, math.pi, 1)
    # Belly
    pygame.draw.ellipse(surface, belly_col, (w // 2 - 7, h // 3 + 4, 14, h // 2 - 8))
    # Belly segments
    for i in range(4):
        pygame.draw.line(surface, (200, 110, 30),
                         (w // 2 - 6, h // 3 + 8 + i * 6),
                         (w // 2 + 6, h // 3 + 8 + i * 6), 1)
    # Neck
    pygame.draw.ellipse(surface, scale_col, (w // 2 - 6, h // 4 - 4, 12, 12))
    # Head
    pygame.draw.ellipse(surface, scale_col, (w // 2 - 12, h // 5 - 6, 24, 14))
    pygame.draw.ellipse(surface, dark_scale, (w // 2 - 12, h // 5 - 6, 24, 14), 1)
    # Snout
    pygame.draw.ellipse(surface, scale_col, (w // 2 - 8, h // 5 + 2, 16, 8))
    # Nostrils
    pygame.draw.circle(surface, (100, 30, 10), (w // 2 - 3, h // 5 + 5), 2)
    pygame.draw.circle(surface, (100, 30, 10), (w // 2 + 3, h // 5 + 5), 2)
    # Eyes
    eye_col = (255, 200, 0) if phase < 3 else (255, 80, 200)
    pygame.draw.ellipse(surface, (20, 10, 5),
                        (w // 2 - 8, h // 5 - 4, 6, 7))
    pygame.draw.ellipse(surface, (20, 10, 5),
                        (w // 2 + 2, h // 5 - 4, 6, 7))
    pygame.draw.ellipse(surface, eye_col,
                        (w // 2 - 7, h // 5 - 3, 4, 5))
    pygame.draw.ellipse(surface, eye_col,
                        (w // 2 + 3, h // 5 - 3, 4, 5))
    pygame.draw.circle(surface, (0, 0, 0), (w // 2 - 5, h // 5 - 1), 1)
    pygame.draw.circle(surface, (0, 0, 0), (w // 2 + 5, h // 5 - 1), 1)
    # Horns
    pygame.draw.polygon(surface, dark_scale,
                         [(w // 2 - 8, h // 5 - 4),
                          (w // 2 - 12, h // 5 - 14),
                          (w // 2 - 5, h // 5 - 4)])
    pygame.draw.polygon(surface, dark_scale,
                         [(w // 2 + 8, h // 5 - 4),
                          (w // 2 + 12, h // 5 - 14),
                          (w // 2 + 5, h // 5 - 4)])
    # Fire breath (phase 2+)
    if phase >= 2:
        fire_alpha = int(abs(math.sin(t * 6)) * 180) + 60
        for fi in range(5):
            fx = w // 2 - 4 + fi * 2
            fs = pygame.Surface((6, 10), pygame.SRCALPHA)
            fc = (255, 100 + fi * 20, 20, fire_alpha)
            pygame.draw.ellipse(fs, fc, (0, 0, 6, 10))
            surface.blit(fs, (fx, h // 5 + 8 + fi * 3))
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 180))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_ancient_golem(surface: pygame.Surface, t: float = 0,
                       phase: int = 1, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    stone = (110, 95, 75)
    dark_stone = (70, 60, 45)
    glow = (100, 220, 140) if phase == 1 else (220, 100, 50)
    crack = (50, 40, 30)
    # Feet
    pygame.draw.rect(surface, dark_stone, (w // 2 - 14, h - 10, 11, 8), border_radius=2)
    pygame.draw.rect(surface, dark_stone, (w // 2 + 3, h - 10, 11, 8), border_radius=2)
    # Legs
    pygame.draw.rect(surface, stone, (w // 2 - 12, h - 22, 9, 14), border_radius=3)
    pygame.draw.rect(surface, stone, (w // 2 + 3, h - 22, 9, 14), border_radius=3)
    # Body _ large block
    pygame.draw.rect(surface, stone, (w // 2 - 15, h // 3 + 4, 30, h // 2 - 4), border_radius=4)
    pygame.draw.rect(surface, dark_stone, (w // 2 - 15, h // 3 + 4, 30, h // 2 - 4), 2, border_radius=4)
    # Body highlight
    pygame.draw.rect(surface, (135, 120, 95),
                     (w // 2 - 13, h // 3 + 6, 26, 8), border_radius=3)
    # Cracks on body
    pygame.draw.line(surface, crack, (w // 2 - 8, h // 3 + 12), (w // 2 - 3, h // 3 + 22), 1)
    pygame.draw.line(surface, crack, (w // 2 + 5, h // 3 + 10), (w // 2 + 9, h // 3 + 20), 1)
    # Glowing rune on chest
    pygame.draw.circle(surface, glow, (w // 2, h // 3 + h // 4), 6)
    pygame.draw.circle(surface, (200, 255, 220) if phase == 1 else (255, 200, 100),
                       (w // 2, h // 3 + h // 4), 3)
    for ra in range(0, 360, 45):
        rx = w // 2 + int(math.cos(math.radians(ra + t * 60)) * 8)
        ry = h // 3 + h // 4 + int(math.sin(math.radians(ra + t * 60)) * 8)
        pygame.draw.circle(surface, glow, (rx, ry), 1)
    # Arms (massive)
    pygame.draw.rect(surface, stone, (w // 2 - 26, h // 3 + 6, 12, 20), border_radius=3)
    pygame.draw.rect(surface, stone, (w // 2 + 14, h // 3 + 6, 12, 20), border_radius=3)
    # Fists
    pygame.draw.rect(surface, dark_stone,
                     (w // 2 - 28, h // 3 + 22, 14, 10), border_radius=3)
    pygame.draw.rect(surface, dark_stone,
                     (w // 2 + 14, h // 3 + 22, 14, 10), border_radius=3)
    # Head (cube-ish)
    pygame.draw.rect(surface, stone, (w // 2 - 12, h // 4 - 8, 24, 18), border_radius=4)
    pygame.draw.rect(surface, dark_stone, (w // 2 - 12, h // 4 - 8, 24, 18), 2, border_radius=4)
    pygame.draw.rect(surface, (135, 120, 95), (w // 2 - 11, h // 4 - 7, 22, 6), border_radius=2)
    # Eyes (glowing slots)
    pygame.draw.rect(surface, (20, 15, 10), (w // 2 - 9, h // 4 - 2, 7, 5))
    pygame.draw.rect(surface, (20, 15, 10), (w // 2 + 2, h // 4 - 2, 7, 5))
    pygame.draw.rect(surface, glow, (w // 2 - 8, h // 4 - 1, 5, 3))
    pygame.draw.rect(surface, glow, (w // 2 + 3, h // 4 - 1, 5, 3))
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 180))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_shadow_knight(surface: pygame.Surface, t: float = 0,
                       phase: int = 1, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    # Shadow aura
    aura_r = int(14 + math.sin(t * 3) * 3)
    aura_s = pygame.Surface((w, h), pygame.SRCALPHA)
    aura_col = (80, 30, 140, 60) if phase == 1 else (150, 30, 80, 80)
    pygame.draw.ellipse(aura_s, aura_col, (w // 2 - aura_r, h // 2 - aura_r,
                                            aura_r * 2, aura_r * 2))
    surface.blit(aura_s, (0, 0))
    armor = (40, 32, 60)
    highlight = (75, 60, 105)
    trim = (200, 100, 255) if phase == 1 else (255, 80, 120)
    # Legs
    for lx in [w // 2 - 8, w // 2 + 2]:
        pygame.draw.rect(surface, armor, (lx, h - 14, 7, 12), border_radius=2)
        pygame.draw.rect(surface, highlight, (lx + 1, h - 14, 5, 5), border_radius=1)
    # Cloak flowing behind
    cloak_pts = [(w // 2 - 10, h // 3 + 4),
                 (w // 2 - 14, h - 6 + int(math.sin(t * 2) * 4)),
                 (w // 2 + 14, h - 6 + int(math.sin(t * 2 + 1) * 4)),
                 (w // 2 + 10, h // 3 + 4)]
    pygame.draw.polygon(surface, (25, 15, 45), cloak_pts)
    pygame.draw.polygon(surface, (40, 20, 70), cloak_pts, 1)
    # Body armour
    pygame.draw.rect(surface, armor, (w // 2 - 11, h // 3, 22, h // 2 - 2), border_radius=3)
    pygame.draw.rect(surface, highlight, (w // 2 - 10, h // 3 + 2, 20, h // 4), border_radius=2)
    pygame.draw.rect(surface, trim, (w // 2 - 3, h // 3 + 5, 6, 10), border_radius=1)
    # Pauldrons
    pygame.draw.ellipse(surface, armor, (w // 2 - 15, h // 3 - 1, 9, 7))
    pygame.draw.ellipse(surface, armor, (w // 2 + 6, h // 3 - 1, 9, 7))
    pygame.draw.ellipse(surface, highlight, (w // 2 - 14, h // 3, 7, 4))
    pygame.draw.ellipse(surface, highlight, (w // 2 + 7, h // 3, 7, 4))
    # Arms
    pygame.draw.rect(surface, armor, (w // 2 - 15, h // 3 + 4, 6, 13), border_radius=2)
    pygame.draw.rect(surface, armor, (w // 2 + 9, h // 3 + 4, 6, 13), border_radius=2)
    # Dark sword (phase 2 = flaming)
    pygame.draw.rect(surface, (160, 160, 190),
                     (w // 2 + 14, h // 4 - 10, 3, 22), border_radius=1)
    pygame.draw.rect(surface, trim, (w // 2 + 11, h // 4 + 3, 9, 3))
    if phase >= 2:
        for fi in range(4):
            flame_s = pygame.Surface((4, 6), pygame.SRCALPHA)
            fc = (255, 100, 50, int(abs(math.sin(t * 8 + fi)) * 200))
            pygame.draw.ellipse(flame_s, fc, (0, 0, 4, 6))
            surface.blit(flame_s, (w // 2 + 13 + fi, h // 4 - 12 - fi * 2))
    # Helmet
    pygame.draw.rect(surface, armor, (w // 2 - 10, h // 4 - 6, 20, 14), border_radius=4)
    pygame.draw.rect(surface, highlight, (w // 2 - 9, h // 4 - 5, 18, 6), border_radius=3)
    pygame.draw.rect(surface, (0, 0, 0), (w // 2 - 7, h // 4 + 2, 14, 3))
    pygame.draw.circle(surface, trim, (w // 2 - 3, h // 4 + 3), 2)
    pygame.draw.circle(surface, trim, (w // 2 + 3, h // 4 + 3), 2)
    for pi in range(3):
        pygame.draw.ellipse(surface, trim,
                            (w // 2 - 2, h // 4 - 10 - pi * 3, 4, 5))
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 180))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_abyss_mage(surface: pygame.Surface, t: float = 0,
                    phase: int = 1, hit: bool = False) -> None:
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))
    # Void aura
    aura_s = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(3):
        r = int(20 - i * 4 + math.sin(t * 2 + i) * 3)
        a = 40 - i * 10
        pygame.draw.ellipse(aura_s, (60, 20, 100, a),
                            (w // 2 - r, h // 2 - r, r * 2, r * 2))
    surface.blit(aura_s, (0, 0))
    robe = (50, 20, 90)
    dark_robe = (30, 10, 60)
    glow_col = (160, 80, 255) if phase == 1 else (255, 80, 180)
    # Flowing robe
    robe_pts = [(w // 2 - 12, h // 3 + 4),
                (w // 2 - 14, h - 4 + int(math.sin(t * 1.5) * 5)),
                (w // 2 + 14, h - 4 + int(math.sin(t * 1.5 + 1) * 5)),
                (w // 2 + 12, h // 3 + 4)]
    pygame.draw.polygon(surface, dark_robe, robe_pts)
    pygame.draw.polygon(surface, robe, robe_pts, 2)
    # Robe body
    pygame.draw.ellipse(surface, dark_robe, (w // 2 - 12, h // 3, 24, h // 2))
    pygame.draw.ellipse(surface, robe, (w // 2 - 11, h // 3 + 2, 22, h // 2 - 4))
    # Constellation / rune pattern on robe
    cx, cy = w // 2, h // 2 + 4
    for star_a in range(0, 360, 45):
        sx = cx + int(math.cos(math.radians(star_a + t * 40)) * 7)
        sy = cy + int(math.sin(math.radians(star_a + t * 40)) * 7)
        pygame.draw.circle(surface, glow_col, (sx, sy), 1)
    pygame.draw.circle(surface, glow_col, (cx, cy), 3)
    # Orbiting void orbs
    for oi in range(2):
        ox = w // 2 + int(math.cos(t * 2 + oi * math.pi) * 14)
        oy = h // 2 + int(math.sin(t * 2 + oi * math.pi) * 8)
        pygame.draw.circle(surface, glow_col, (ox, oy), 4)
        pygame.draw.circle(surface, (255, 220, 255), (ox, oy), 2)
    # Arms (reaching pose)
    pygame.draw.ellipse(surface, robe, (1, h // 3 + 4, 8, 12))
    pygame.draw.ellipse(surface, robe, (w - 9, h // 3 + 4, 8, 12))
    # Hands with magic glow
    pygame.draw.circle(surface, (180, 140, 220), (4, h // 3 + 14), 4)
    pygame.draw.circle(surface, (180, 140, 220), (w - 4, h // 3 + 14), 4)
    pygame.draw.circle(surface, glow_col, (4, h // 3 + 14), 2)
    pygame.draw.circle(surface, glow_col, (w - 4, h // 3 + 14), 2)
    # Head
    pygame.draw.circle(surface, (170, 140, 200), (w // 2, h // 4), 10)
    pygame.draw.circle(surface, (200, 175, 225), (w // 2, h // 4), 9)
    # Void hood
    pygame.draw.ellipse(surface, dark_robe, (w // 2 - 10, h // 4 - 12, 20, 14))
    pygame.draw.arc(surface, robe,
                    pygame.Rect(w // 2 - 10, h // 4 - 12, 20, 14), 0, math.pi, 2)
    # Void mask (face is partially hidden)
    pygame.draw.ellipse(surface, (10, 5, 20, 200),
                        (w // 2 - 7, h // 4 - 3, 14, 10))
    # Glowing eyes _ multiple for void look
    for ex, ey in [(-3, 0), (3, 0)]:
        pygame.draw.circle(surface, (0, 0, 0), (w // 2 + ex, h // 4 + ey), 3)
        pygame.draw.circle(surface, glow_col, (w // 2 + ex, h // 4 + ey), 2)
        pygame.draw.circle(surface, (255, 255, 255), (w // 2 + ex, h // 4 + ey - 1), 1)
    # Third eye (phase 2)
    if phase >= 2:
        pygame.draw.circle(surface, (0, 0, 0), (w // 2, h // 4 - 4), 3)
        pygame.draw.circle(surface, (255, 50, 200), (w // 2, h // 4 - 4), 2)
    if hit:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((255, 255, 255, 180))
        surface.blit(f, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
