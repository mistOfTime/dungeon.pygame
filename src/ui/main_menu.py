# Eclipse Depths - Main Menu (cinematic dungeon background)

from __future__ import annotations
import pygame
import math
import random
from src.core.constants import *


# __ Button ____________________________________________________________________
class Button:
    def __init__(self, x, y, w, h, text, font,
                 colour=(28, 22, 45), hover_colour=(55, 42, 88),
                 text_colour=(220, 210, 255), border_colour=(90, 70, 130)) -> None:
        self.rect         = pygame.Rect(x, y, w, h)
        self.text         = text
        self.font         = font
        self.colour       = colour
        self.hover_colour = hover_colour
        self.text_colour  = text_colour
        self.border_colour= border_colour
        self._hovered     = False
        self._press_anim  = 0.0   # 0..1 press scale

    def handle_event(self, event: pygame.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._press_anim = 1.0
                return True
        return False

    def update(self, dt: float) -> None:
        if self._press_anim > 0:
            self._press_anim = max(0.0, self._press_anim - dt * 6)

    def draw(self, surface: pygame.Surface) -> None:
        scale  = 1.0 - self._press_anim * 0.04
        rw     = int(self.rect.width  * scale)
        rh     = int(self.rect.height * scale)
        rx     = self.rect.centerx - rw // 2
        ry     = self.rect.centery - rh // 2
        r      = pygame.Rect(rx, ry, rw, rh)

        bg = self.hover_colour if self._hovered else self.colour
        # Shadow
        shadow = pygame.Surface((rw + 4, rh + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), shadow.get_rect(), border_radius=8)
        surface.blit(shadow, (rx - 2, ry + 3))
        # Body
        pygame.draw.rect(surface, bg, r, border_radius=7)
        # Top shine
        shine = pygame.Surface((rw - 4, rh // 2), pygame.SRCALPHA)
        shine.fill((255, 255, 255, 12 if not self._hovered else 22))
        surface.blit(shine, (rx + 2, ry + 2))
        # Border
        border_col = (130, 100, 200) if self._hovered else self.border_colour
        pygame.draw.rect(surface, border_col, r, 1, border_radius=7)
        # Text
        txt = self.font.render(self.text, True,
                               (255, 255, 255) if self._hovered else self.text_colour)
        surface.blit(txt, txt.get_rect(center=r.center))


# __ Background renderer _______________________________________________________
class MenuBackground:
    """
    Draws a full cinematic dungeon background:
    - Stone floor with slab grid and mortar
    - Stone walls with brick pattern and cracks
    - Two lit wall torches with flickering light
    - Distant doorway arch at centre
    - Drifting dust particles in torch light
    - Vignette + depth fog
    """

    FLOOR  = (44, 38, 52)
    FLOOR2 = (36, 31, 44)
    MORTAR = (26, 21, 34)
    WALL_F = (32, 27, 42)
    WALL_B = (22, 18, 30)
    WALL_H = (52, 44, 64)
    STONE_VAR = 6

    def __init__(self, sw: int, sh: int) -> None:
        self.sw   = sw
        self.sh   = sh
        self._rng = random.Random(42)
        self._t   = 0.0
        # Dust particles
        self._dust = [self._make_dust() for _ in range(60)]
        # Pre-build static stone surface
        self._stone_surf = pygame.Surface((sw, sh))
        self._build_stone()

    def _make_dust(self) -> dict:
        rng = self._rng
        return {
            "x":   rng.uniform(0, self.sw),
            "y":   rng.uniform(0, self.sh),
            "vx":  rng.uniform(-6, 6),
            "vy":  rng.uniform(-12, -4),
            "life":rng.uniform(0.5, 3.0),
            "max_life": rng.uniform(1.5, 4.0),
            "r":   rng.randint(1, 2),
            "col": (rng.randint(180, 220), rng.randint(160, 200), rng.randint(100, 150)),
        }

    def _vary(self, base: tuple) -> tuple:
        v = self.STONE_VAR
        r = self._rng
        return (
            min(255, max(0, base[0] + r.randint(-v, v))),
            min(255, max(0, base[1] + r.randint(-v, v))),
            min(255, max(0, base[2] + r.randint(-v, v))),
        )

    def _build_stone(self) -> None:
        sw, sh = self.sw, self.sh
        s      = self._stone_surf
        rng    = self._rng

        # Sky/void at very top
        for y in range(sh // 3):
            alpha = int(y / (sh // 3) * 40)
            pygame.draw.line(s, (2 + alpha//8, 1 + alpha//10, 4 + alpha//6), (0, y), (sw, y))

        # __ Back wall (upper 55% of screen) __________________________________
        wall_bottom = int(sh * 0.58)
        TILE = 36
        cols = sw // TILE + 2
        rows = wall_bottom // (TILE // 2) + 2

        for row in range(rows):
            for col in range(cols):
                offset = (row % 2) * (TILE // 2)
                x = col * TILE - offset
                y = row * (TILE // 2)
                bc = self._vary(self.WALL_F)
                # Block face
                pygame.draw.rect(s, bc, (x + 1, y + 1, TILE - 2, TILE // 2 - 2))
                # Top highlight
                pygame.draw.line(s, self.WALL_H, (x + 1, y + 1), (x + TILE - 2, y + 1))
                # Mortar
                pygame.draw.rect(s, self.WALL_B, (x, y, TILE, TILE // 2), 1)
                # Random crack
                if rng.random() < 0.05:
                    cx1 = x + rng.randint(4, TILE - 4)
                    cy1 = y + rng.randint(2, TILE // 2 - 2)
                    pygame.draw.line(s, (18, 14, 24),
                                     (cx1, cy1),
                                     (cx1 + rng.randint(-6, 6), cy1 + rng.randint(-4, 4)), 1)
                # Mossy stain
                if rng.random() < 0.025:
                    mx = x + rng.randint(2, TILE - 6)
                    my = y + rng.randint(1, TILE // 2 - 4)
                    pygame.draw.ellipse(s, (30, 55, 28), (mx, my, 6, 3))

        # __ Floor (lower 42% of screen) _______________________________________
        FT = 40   # floor tile size
        floor_top = wall_bottom
        frows = (sh - floor_top) // FT + 2
        fcols = sw // FT + 2

        for row in range(frows):
            for col in range(fcols):
                fx = col * FT
                fy = floor_top + row * FT
                depth_dark = int(row * 6)
                fc = self._vary((
                    max(0, self.FLOOR[0] - depth_dark),
                    max(0, self.FLOOR[1] - depth_dark),
                    max(0, self.FLOOR[2] - depth_dark),
                ))
                pygame.draw.rect(s, fc, (fx + 1, fy + 1, FT - 2, FT - 2))
                # Half-tile sub-slabs
                half = FT // 2
                sc2 = self._vary(self.FLOOR2)
                pygame.draw.rect(s, sc2, (fx + 1, fy + 1, half - 1, half - 1))
                pygame.draw.rect(s, sc2, (fx + half + 1, fy + half + 1, half - 2, half - 2))
                # Mortar
                pygame.draw.rect(s, self.MORTAR, (fx, fy, FT, FT), 1)
                pygame.draw.line(s, self.MORTAR, (fx + half, fy), (fx + half, fy + FT))
                pygame.draw.line(s, self.MORTAR, (fx, fy + half), (fx + FT, fy + half))
                # Floor crack
                if rng.random() < 0.04:
                    cx = fx + rng.randint(3, FT - 3)
                    cy = fy + rng.randint(3, FT - 3)
                    pygame.draw.line(s, (22, 18, 28),
                                     (cx, cy),
                                     (cx + rng.randint(-5, 5), cy + rng.randint(-5, 5)), 1)

        # __ Floor/wall join: deep shadow strip _______________________________
        join = pygame.Surface((sw, 10), pygame.SRCALPHA)
        for i in range(10):
            pygame.draw.line(join, (0, 0, 0, 80 - i * 7), (0, i), (sw, i))
        s.blit(join, (0, wall_bottom - 4))

        # __ Left pillar _______________________________________________________
        self._draw_pillar(s, int(sw * 0.12), wall_bottom, 44, sh - wall_bottom + 4)
        # __ Right pillar ______________________________________________________
        self._draw_pillar(s, int(sw * 0.78), wall_bottom, 44, sh - wall_bottom + 4)

        # __ Central archway ___________________________________________________
        self._draw_arch(s, sw // 2, wall_bottom)

    def _draw_pillar(self, s, x, y, w, h) -> None:
        rng = self._rng
        # Shaft
        for row in range(h // 18 + 1):
            var = rng.randint(-4, 4)
            bc  = (max(0, 40 + var), max(0, 34 + var), max(0, 52 + var))
            pygame.draw.rect(s, bc, (x, y + row * 18, w, 17))
            pygame.draw.line(s, (20, 16, 28), (x, y + row * 18), (x + w, y + row * 18))
            pygame.draw.line(s, (58, 50, 72), (x, y + row * 18 + 1), (x + w, y + row * 18 + 1))
        pygame.draw.rect(s, (22, 18, 30), (x, y, w, h), 1)
        # Capital (top block)
        pygame.draw.rect(s, (52, 44, 66), (x - 4, y - 8, w + 8, 10), border_radius=2)
        pygame.draw.rect(s, (68, 58, 82), (x - 2, y - 7, w + 4, 3))
        # Base
        pygame.draw.rect(s, (52, 44, 66), (x - 4, y + h - 8, w + 8, 10), border_radius=2)

    def _draw_arch(self, s, cx, base_y) -> None:
        rng = self._rng
        aw  = 160   # arch width
        ah  = 220   # arch height
        ax  = cx - aw // 2
        ay  = base_y - ah

        # Dark void inside arch
        pygame.draw.ellipse(s, (4, 3, 8),
                            (ax + 6, ay + 30, aw - 12, ah - 10))
        pygame.draw.rect(s, (4, 3, 8),
                         (ax + 6, ay + 80, aw - 12, ah - 80))

        # Arch stones (voussoirs)
        for i in range(11):
            angle_start = math.pi + i * (math.pi / 10)
            angle_end   = math.pi + (i + 1) * (math.pi / 10)
            # Inner arc
            pts_inner = []
            pts_outer = []
            inner_r = aw // 2 - 6
            outer_r = aw // 2 + 14
            for a in [angle_start, (angle_start+angle_end)/2, angle_end]:
                pts_inner.append((cx + int(math.cos(a) * inner_r),
                                   base_y + int(math.sin(a) * inner_r)))
                pts_outer.append((cx + int(math.cos(a) * outer_r),
                                   base_y + int(math.sin(a) * outer_r)))
            quad = pts_inner + list(reversed(pts_outer))
            var = rng.randint(-5, 5)
            sc  = (max(0, 38 + var), max(0, 32 + var), max(0, 50 + var))
            if len(quad) >= 3:
                pygame.draw.polygon(s, sc, quad)
                pygame.draw.polygon(s, (20, 16, 28), quad, 1)

        # Left jamb
        pygame.draw.rect(s, (35, 30, 46), (ax, base_y - ah + 60, 20, ah - 60))
        pygame.draw.rect(s, (22, 18, 30), (ax, base_y - ah + 60, 20, ah - 60), 1)
        # Right jamb
        pygame.draw.rect(s, (35, 30, 46), (ax + aw - 20, base_y - ah + 60, 20, ah - 60))
        pygame.draw.rect(s, (22, 18, 30), (ax + aw - 20, base_y - ah + 60, 20, ah - 60), 1)

        # Keystone
        kx, ky = cx - 14, base_y - ah + 28
        pygame.draw.polygon(s, (55, 46, 70),
                            [(cx, ky), (cx - 14, ky + 28), (cx + 14, ky + 28)])
        pygame.draw.polygon(s, (80, 68, 98),
                            [(cx, ky + 4), (cx - 10, ky + 26), (cx + 10, ky + 26)])
        pygame.draw.polygon(s, (22, 18, 30),
                            [(cx, ky), (cx - 14, ky + 28), (cx + 14, ky + 28)], 1)

    def update(self, dt: float) -> None:
        self._t += dt
        # Update dust
        for d in self._dust:
            d["x"]   += d["vx"] * dt + math.sin(self._t * 0.8 + d["y"] * 0.01) * 0.4
            d["y"]   += d["vy"] * dt
            d["life"] -= dt
            if d["life"] <= 0:
                # Respawn near torch positions
                nd = self._make_dust()
                torch_side = random.choice([-1, 1])
                nd["x"] = self.sw * (0.22 if torch_side < 0 else 0.78) + random.uniform(-30, 30)
                nd["y"] = self.sh * 0.45 + random.uniform(-20, 20)
                d.update(nd)

    def draw(self, surface: pygame.Surface) -> None:
        t   = self._t
        sw, sh = self.sw, self.sh
        wall_bottom = int(sh * 0.58)

        # 1. Static stone
        surface.blit(self._stone_surf, (0, 0))

        # 2. Torch glow _ subtle, small, warm
        flicker_l = 0.88 + 0.12 * math.sin(t * 7.3 + 0.1)
        flicker_r = 0.88 + 0.12 * math.sin(t * 6.8 + 1.2)
        torch_lx  = int(sw * 0.22)
        torch_rx  = int(sw * 0.78)
        torch_y   = wall_bottom - 40

        self._draw_torch_glow(surface, torch_lx, torch_y, flicker_l)
        self._draw_torch_glow(surface, torch_rx, torch_y, flicker_r)

        # 3. Torch sprites
        self._draw_torch_sprite(surface, torch_lx, torch_y, t)
        self._draw_torch_sprite(surface, torch_rx, torch_y, t + 0.5)

        # 4. Archway inner glow _ very faint, deep inside arch only
        glow_alpha = int(8 + 6 * math.sin(t * 1.4))
        arch_glow  = pygame.Surface((100, 140), pygame.SRCALPHA)
        for r in range(50, 0, -5):
            a = int(glow_alpha * (1 - r / 50))
            pygame.draw.ellipse(arch_glow, (60, 30, 120, a),
                                (50 - r, 70 - r, r * 2, r * 2))
        surface.blit(arch_glow, (sw // 2 - 50, wall_bottom - 200),
                     special_flags=pygame.BLEND_RGBA_ADD)

        # 5. Dust particles _ very small and faint
        for d in self._dust:
            ratio = d["life"] / d["max_life"]
            alpha = int(clamp(ratio, 0, 1) * 55)
            if alpha < 4:
                continue
            ds = pygame.Surface((d["r"]*2+2, d["r"]*2+2), pygame.SRCALPHA)
            pygame.draw.circle(ds, (*d["col"], alpha), (d["r"]+1, d["r"]+1), d["r"])
            surface.blit(ds, (int(d["x"]) - d["r"], int(d["y"]) - d["r"]))

        # 6. Depth fog at bottom
        fog = pygame.Surface((sw, 90), pygame.SRCALPHA)
        for fy in range(90):
            a = int(fy * 2.2)
            pygame.draw.line(fog, (4, 3, 8, a), (0, fy), (sw, fy))
        surface.blit(fog, (0, sh - 90))

        # 7. Top vignette
        top_fog = pygame.Surface((sw, 80), pygame.SRCALPHA)
        for fy in range(80):
            a = int((80 - fy) * 2.0)
            pygame.draw.line(top_fog, (2, 1, 6, a), (0, fy), (sw, fy))
        surface.blit(top_fog, (0, 0))

        # 8. Side vignettes
        for side_x, direction in [(0, 1), (sw - 70, -1)]:
            side_fog = pygame.Surface((70, sh), pygame.SRCALPHA)
            for fx in range(70):
                dist = fx if direction == 1 else 69 - fx
                a    = int((70 - dist) * 2.2)
                pygame.draw.line(side_fog, (2, 1, 6, a), (fx, 0), (fx, sh))
            surface.blit(side_fog, (side_x, 0))

    def _draw_torch_glow(self, surface, cx, cy, flicker) -> None:
        """Subtle warm glow _ just a soft halo on the wall/floor nearby."""
        radius = 70   # much smaller than before
        r = int(radius * flicker)
        glow = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        for i in range(r, 0, -4):
            frac  = i / r
            # Very low alpha _ just tints the stone warm
            alpha = int(18 * (1 - frac) * flicker)
            col   = (int(255 * flicker), int(140 * frac * flicker), 20, alpha)
            pygame.draw.ellipse(glow, col,
                                (r - i + 2, int(r - i * 0.65) + 2,
                                 i * 2, int(i * 1.3)))
        surface.blit(glow, (cx - r - 2, cy - int(r * 0.65) - 2),
                     special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_torch_sprite(self, surface, cx, cy, t) -> None:
        # Bracket
        pygame.draw.rect(surface, (60, 48, 30), (cx - 3, cy, 6, 14), border_radius=2)
        pygame.draw.rect(surface, (80, 65, 40), (cx - 5, cy + 12, 10, 4), border_radius=2)
        # Handle
        pygame.draw.rect(surface, (80, 65, 40), (cx - 2, cy + 4, 4, 10))
        # Flame layers (animated)
        for i, (fc, fr, fy_off) in enumerate([
            ((255, 60,  10), 5, 0),
            ((255, 130, 20), 4, -3),
            ((255, 210, 80), 3, -6),
            ((255, 240,180), 2, -9),
        ]):
            flicker_off = int(math.sin(t * 12 + i * 1.5) * 2)
            fs = pygame.Surface((fr*2+2, fr*2+2), pygame.SRCALPHA)
            pygame.draw.circle(fs, (*fc, 220), (fr+1, fr+1), fr)
            surface.blit(fs, (cx - fr - 1 + flicker_off, cy + fy_off - fr))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


# __ Main Menu _________________________________________________________________
class MainMenu:
    def __init__(self, screen: pygame.Surface, assets, bus) -> None:
        self.screen  = screen
        self.assets  = assets
        self.bus     = bus
        self._t      = 0.0
        self._fade_in = 1.5   # seconds of fade-in

        sw, sh = screen.get_size()

        # Fonts
        self._font_title = assets.font(54, bold=True)
        self._font_sub   = assets.font(15)
        self._font_btn   = assets.font(17)
        self._font_small = assets.font(12)

        # Background
        self._bg = MenuBackground(sw, sh)

        # Button layout _ right side panel
        bw, bh  = 220, 42
        bx      = sw - bw - 60
        by_start= sh // 2 - 40
        gap     = bh + 10

        BUTTON_DEFS = [
            ("New Game",  "new_game",       (30, 22, 50), (60, 44, 100)),
            ("Continue",  "continue_game",  (22, 30, 50), (44, 60, 100)),
            ("Load Game", "load_game",      (28, 28, 48), (55, 55, 95)),
            ("Settings",  "open_settings",  (28, 28, 48), (55, 55, 95)),
            ("Credits",   "open_credits",   (28, 28, 48), (55, 55, 95)),
            ("Quit",      "quit_game",      (50, 22, 22), (100, 40, 40)),
        ]
        self._buttons = []
        self._actions = []
        for i, (label, action, col, hcol) in enumerate(BUTTON_DEFS):
            btn = Button(bx, by_start + i * gap, bw, bh, label,
                         self._font_btn,
                         colour=col, hover_colour=hcol,
                         border_colour=(80, 65, 110))
            self._buttons.append(btn)
            self._actions.append(action)

        # Title glow layers
        self._title_y_offset = 0.0

    def handle_event(self, event: pygame.Event) -> None:
        for i, btn in enumerate(self._buttons):
            if btn.handle_event(event):
                self.bus.publish(self._actions[i])

    def update(self, dt: float) -> None:
        self._t += dt
        self._fade_in = max(0.0, self._fade_in - dt)
        self._bg.update(dt)
        self._title_y_offset = math.sin(self._t * 0.7) * 3.0
        for btn in self._buttons:
            btn.update(dt)

    def draw(self) -> None:
        sw, sh = self.screen.get_size()

        # Background
        self._bg.draw(self.screen)

        # __ Right-side semi-transparent panel ________________________________
        panel_w = 310
        panel_h = len(self._buttons) * 52 + 80
        panel_x = sw - panel_w - 40
        panel_y = sh // 2 - panel_h // 2
        panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((6, 4, 12, 190))
        pygame.draw.rect(panel, (60, 44, 90, 160), panel.get_rect(), 1, border_radius=12)
        # Decorative top line
        pygame.draw.line(panel, (120, 80, 200, 180), (20, 0), (panel_w - 20, 0), 2)
        self.screen.blit(panel, (panel_x, panel_y))

        # __ Buttons ___________________________________________________________
        for btn in self._buttons:
            btn.draw(self.screen)

        # __ Title (left side over dungeon bg) ________________________________
        title_cx = int(sw * 0.32)
        title_cy = int(sh * 0.26 + self._title_y_offset)

        # Render title first to know its size
        title_surf = self._font_title.render("ECLIPSE DEPTHS", True, (220, 185, 255))
        sub_surf   = self._font_sub.render("A Roguelike Dungeon Crawler  _  by mistOfTime",
                                            True, (170, 155, 210))
        tag_surf   = self._font_small.render("The darkness hungers. Will you descend_",
                                              True, (120, 105, 160))

        # Dark backing panel behind all title text
        pad   = 18
        box_w = max(title_surf.get_width(), sub_surf.get_width(), tag_surf.get_width()) + pad*2
        box_h = title_surf.get_height() + sub_surf.get_height() + tag_surf.get_height() + pad*2 + 20
        box_x = title_cx - box_w // 2
        box_y = title_cy - pad

        backing = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        backing.fill((4, 3, 10, 200))
        pygame.draw.rect(backing, (55, 38, 88, 180), backing.get_rect(), 1, border_radius=10)
        # Thin gold top line
        pygame.draw.line(backing, (140, 100, 200, 160), (16, 0), (box_w - 16, 0), 2)
        self.screen.blit(backing, (box_x, box_y))

        # Shadow then title
        shadow_surf = self._font_title.render("ECLIPSE DEPTHS", True, (10, 6, 22))
        self.screen.blit(shadow_surf,
                     (title_cx - shadow_surf.get_width()//2 + 2, title_cy + 2))
        self.screen.blit(title_surf,
                     (title_cx - title_surf.get_width()//2, title_cy))

        # Decorative separator line
        line_y = title_cy + title_surf.get_height() + 4
        line_w = title_surf.get_width() - 20
        pygame.draw.line(self.screen, (90, 65, 140),
                         (title_cx - line_w//2, line_y),
                         (title_cx + line_w//2, line_y), 1)

        # Subtitle
        self.screen.blit(sub_surf,
                     (title_cx - sub_surf.get_width()//2, line_y + 8))

        # Tagline
        t2 = self._t
        tag_alpha = int(160 + 60 * math.sin(t2 * 0.9))
        tag_surf.set_alpha(tag_alpha)
        self.screen.blit(tag_surf,
                     (title_cx - tag_surf.get_width()//2,
                      line_y + sub_surf.get_height() + 14))

        # __ Version bottom-right ______________________________________________
        ver = self._font_small.render("v1.0.0", True, (50, 42, 72))
        self.screen.blit(ver, (sw - ver.get_width() - 10, sh - 16))

        # __ Fade-in overlay ___________________________________________________
        if self._fade_in > 0:
            alpha = int((self._fade_in / 1.5) * 255)
            fade  = pygame.Surface((sw, sh))
            fade.fill((0, 0, 0))
            fade.set_alpha(alpha)
            self.screen.blit(fade, (0, 0))
