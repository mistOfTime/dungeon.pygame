# Eclipse Depths - HUD (fixed layout)

from __future__ import annotations
import pygame
import math
from src.core.constants import *
from src.utils.helpers import draw_bar, clamp


class Notification:
    def __init__(self, text: str, colour: tuple, font: pygame.font.Font,
                 duration: float = 2.5) -> None:
        self.text     = text
        self.colour   = colour
        self.duration = duration
        self.life     = duration
        self.font     = font
        self._surf    = font.render(text, True, colour)

    def update(self, dt: float) -> bool:
        self.life -= dt
        return self.life > 0

    def draw(self, surface: pygame.Surface, y: int) -> None:
        alpha = int(clamp(self.life / max(self.duration * 0.4, 0.01), 0, 1) * 220)
        self._surf.set_alpha(alpha)
        x = surface.get_width() // 2 - self._surf.get_width() // 2
        surface.blit(self._surf, (x, y))


class HUD:
    """
    Layout (1280×720 example):
    ┌─────────────────────────────────────────────────────────────────────┐
    │ [Floor N  Gold: NNN]                              [Minimap 140×140] │
    │                                  [Boss bar + name]                  │
    │                                                                      │
    │  (notifications centred mid-screen)                                 │
    │                                                                      │
    │ HP ████░  22/100     [Combo x3!]         [Hotbar 1 2 3 4]           │
    │ MP ████░  40/80      [Z][X][C][V] spells                            │
    │ ST ████░  80/100                                                    │
    │ XP ████░  Lv 3                                                      │
    │ [controls hint]                                                      │
    └─────────────────────────────────────────────────────────────────────┘
    """

    MINIMAP_SIZE  = 140
    BAR_W         = 180
    BAR_H         = 13
    BAR_X         = 14
    BOTTOM_BASE   = 0   # computed relative to sh

    def __init__(self, screen: pygame.Surface, assets, bus, player) -> None:
        self.screen  = screen
        self.assets  = assets
        self.player  = player
        self.bus     = bus
        self._world  = None

        self._font_sm  = assets.font(11)
        self._font_med = assets.font(14)
        self._font_big = assets.font(22, bold=True)
        self._font_lbl = assets.font(12)

        self._notifications: list[Notification] = []
        self._combo_display  = 0
        self._combo_alpha    = 0.0
        self._boss_name      = ""
        self._boss_hp        = 0.0
        self._boss_max_hp    = 1.0

        bus.subscribe("notification",  self._on_notification)
        bus.subscribe("boss_spawn",    self._on_boss_spawn)
        bus.subscribe("player_attack", self._on_combo)

    def set_world(self, world) -> None:
        self._world = world

    def _on_notification(self, data):
        if data:
            n = Notification(data.get("text", ""), data.get("colour", WHITE),
                             self._font_med)
            self._notifications.append(n)

    def _on_boss_spawn(self, data):
        if data:
            self._boss_name   = data.get("name", "Boss")
            self._boss_hp     = 1.0
            self._boss_max_hp = 1.0

    def _on_combo(self, data):
        if data:
            self._combo_display = data.get("combo", 1)
            self._combo_alpha   = 1.2

    def handle_event(self, event: pygame.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        self._notifications = [n for n in self._notifications if n.update(dt)]
        self._combo_alpha   = max(0.0, self._combo_alpha - dt)

        # Track boss HP
        if self._world:
            from src.bosses.base_boss import BaseBoss
            boss_found = False
            for e in self._world.enemy_group:
                if isinstance(e, BaseBoss):
                    self._boss_hp     = e.hp
                    self._boss_max_hp = e.max_hp
                    self._boss_name   = e.STATS["name"]
                    boss_found = True
                    break
            if not boss_found and self._boss_hp > 0:
                self._boss_hp = 0.0

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self) -> None:
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        p  = self.player

        # ── Bottom-left panel background ─────────────────────────────────────
        panel_h = 90
        panel_w = self.BAR_W + 80
        panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((8, 6, 18, 200))
        pygame.draw.rect(panel, (50, 44, 78), panel.get_rect(), 1, border_radius=6)
        self.screen.blit(panel, (0, sh - panel_h))

        by = sh - panel_h + 8   # top of first bar

        # HP bar
        lbl = self._font_sm.render(f"HP  {int(p.hp)}/{int(p.max_hp)}", True, (220, 100, 100))
        self.screen.blit(lbl, (self.BAR_X, by))
        draw_bar(self.screen, self.BAR_X, by + 13, self.BAR_W, self.BAR_H,
                 p.hp, p.max_hp, (200, 50, 50), radius=4)
        by += 27

        # Mana bar
        lbl = self._font_sm.render(f"MP  {int(p.mana)}/{int(p.max_mana)}", True, (100, 140, 240))
        self.screen.blit(lbl, (self.BAR_X, by))
        draw_bar(self.screen, self.BAR_X, by + 13, self.BAR_W, self.BAR_H,
                 p.mana, p.max_mana, (50, 100, 220), radius=4)
        by += 27

        # Stamina bar
        lbl = self._font_sm.render(f"ST  {int(p.stamina)}/{int(p.max_stamina)}", True, (100, 210, 120))
        self.screen.blit(lbl, (self.BAR_X, by))
        draw_bar(self.screen, self.BAR_X, by + 13, self.BAR_W, self.BAR_H,
                 p.stamina, p.max_stamina, (50, 180, 80), radius=4)

        # XP bar (very bottom of panel)
        xp_y = sh - 12
        draw_bar(self.screen, 0, xp_y, panel_w, 6,
                 p.xp, p.xp_to_next, (200, 180, 40), bg=(20, 18, 34), radius=2)
        lv_lbl = self._font_sm.render(f"Lv {p.level}  XP {p.xp}/{p.xp_to_next}", True, GOLD)
        self.screen.blit(lv_lbl, (self.BAR_X, sh - panel_h + panel_h - 20))

        # ── Spell slots (bottom centre-left) ─────────────────────────────────
        self._draw_spell_slots(sw, sh)

        # ── Hotbar (bottom centre) ────────────────────────────────────────────
        self._draw_hotbar(sw, sh)

        # ── Combo counter ─────────────────────────────────────────────────────
        if self._combo_alpha > 0 and self._combo_display > 1:
            alpha = int(clamp(self._combo_alpha / 1.2, 0, 1) * 255)
            combo_txt = self._font_big.render(f"× {self._combo_display}  COMBO!", True, (255, 200, 50))
            combo_txt.set_alpha(alpha)
            scale = 1.0 + (self._combo_alpha / 1.2) * 0.3
            scaled = pygame.transform.scale(
                combo_txt,
                (int(combo_txt.get_width() * scale), int(combo_txt.get_height() * scale)))
            self.screen.blit(scaled,
                             (sw // 2 - scaled.get_width() // 2, sh // 2 - 80))

        # ── Boss health bar ───────────────────────────────────────────────────
        if self._boss_name and self._boss_hp > 0:
            bw, bh = min(500, sw - 80), 22
            bx     = sw // 2 - bw // 2
            by2    = 34
            # Background
            bg = pygame.Surface((bw + 4, bh + 24), pygame.SRCALPHA)
            bg.fill((10, 5, 18, 210))
            pygame.draw.rect(bg, (120, 40, 40), bg.get_rect(), 1, border_radius=6)
            self.screen.blit(bg, (bx - 2, by2 - 18))
            name_txt = self._font_med.render(self._boss_name, True, (255, 180, 180))
            self.screen.blit(name_txt, (bx + bw // 2 - name_txt.get_width() // 2, by2 - 16))
            draw_bar(self.screen, bx, by2, bw, bh,
                     self._boss_hp, max(self._boss_max_hp, 1), DARK_RED, radius=5)
            pct = self._boss_hp / max(self._boss_max_hp, 1)
            pct_txt = self._font_sm.render(f"{int(pct * 100)}%", True, WHITE)
            self.screen.blit(pct_txt, (bx + bw // 2 - pct_txt.get_width() // 2, by2 + 4))

        # ── Floor / gold top-right ────────────────────────────────────────────
        info_bg = pygame.Surface((180, 22), pygame.SRCALPHA)
        info_bg.fill((8, 6, 18, 180))
        self.screen.blit(info_bg, (sw - 182, 6))
        info = self._font_lbl.render(
            f"Floor {p.stats.floors}    Gold: {p.stats.gold}", True, GOLD)
        self.screen.blit(info, (sw - info.get_width() - 14, 8))

        # ── Minimap ───────────────────────────────────────────────────────────
        if self._world:
            self._draw_minimap(sw)

        # ── Notifications ─────────────────────────────────────────────────────
        ny = sh // 2 - 130
        for n in reversed(self._notifications[-5:]):
            n.draw(self.screen, ny)
            ny -= 22

        # ── Controls hint ─────────────────────────────────────────────────────
        hint = self._font_sm.render(
            "WASD: Move   Space: Dodge   LMB: Attack   RMB: Ranged   "
            "Z/X/C/V: Spells   E: Interact   I/M/Q: Menus", True, (55, 50, 75))
        self.screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 10))

    # ── Spell slots ───────────────────────────────────────────────────────────
    def _draw_spell_slots(self, sw: int, sh: int) -> None:
        if not self._world:
            return
        sm      = self._world.spell_manager
        slot_w  = 52
        slot_h  = 52
        pad     = 4
        total_w = 4 * (slot_w + pad)
        # Place to the left of hotbar; hotbar is centred
        hotbar_w = 4 * (52 + 4)
        hb_x     = sw // 2 - hotbar_w // 2
        sx0      = hb_x - total_w - 16
        sy       = sh - slot_h - 14

        SPELL_COLS = {
            "fireball":     (255, 100, 30),
            "ice_blast":    (100, 200, 255),
            "lightning":    (220, 220, 50),
            "poison_cloud": (80, 200, 80),
            "heal":         (100, 255, 120),
            "magic_shield": (100, 150, 255),
            "dash_spell":   (200, 100, 255),
        }
        KEY_LABELS = ["Z", "X", "C", "V"]

        from src.spells.spell_manager import SPELLS
        for i, sid in enumerate(sm.equipped):
            sx  = sx0 + i * (slot_w + pad)
            cd  = sm.get_cooldown_progress(i)
            col = SPELL_COLS.get(sid, (160, 100, 200)) if sid else (30, 26, 48)

            # Background
            pygame.draw.rect(self.screen, (20, 16, 36),
                             (sx, sy, slot_w, slot_h), border_radius=6)
            pygame.draw.rect(self.screen, (55, 48, 80),
                             (sx, sy, slot_w, slot_h), 1, border_radius=6)

            if sid:
                # Colour fill (dim if on cooldown)
                fill_a = 180 if cd >= 1.0 else int(60 + cd * 120)
                fill   = pygame.Surface((slot_w - 4, slot_h // 2), pygame.SRCALPHA)
                fill.fill((*col[:3], fill_a))
                self.screen.blit(fill, (sx + 2, sy + 2))

                name = SPELLS[sid]["name"].split()[0][:7]
                ntxt = self._font_sm.render(name, True, col if cd >= 1.0 else MID_GREY)
                self.screen.blit(ntxt, (sx + slot_w // 2 - ntxt.get_width() // 2,
                                         sy + slot_h // 2 - 4))

                # Cooldown overlay
                if cd < 1.0:
                    cd_h  = int((1.0 - cd) * slot_h)
                    cd_surf = pygame.Surface((slot_w - 4, cd_h), pygame.SRCALPHA)
                    cd_surf.fill((0, 0, 0, 160))
                    self.screen.blit(cd_surf, (sx + 2, sy + 2))
                    cd_txt = self._font_sm.render(
                        f"{SPELLS[sid]['cooldown'] * (1 - cd):.1f}s", True, (200, 200, 200))
                    self.screen.blit(cd_txt, (sx + slot_w // 2 - cd_txt.get_width() // 2,
                                              sy + slot_h // 2 + 6))

            # Key label
            kt = self._font_sm.render(KEY_LABELS[i], True, (80, 72, 110))
            self.screen.blit(kt, (sx + 3, sy + 3))

    # ── Hotbar ────────────────────────────────────────────────────────────────
    def _draw_hotbar(self, sw: int, sh: int) -> None:
        slot_w  = 52
        slot_h  = 52
        pad     = 4
        total_w = 4 * (slot_w + pad)
        hx      = sw // 2 - total_w // 2
        hy      = sh - slot_h - 14

        for i in range(4):
            sx   = hx + i * (slot_w + pad)
            item = self.player.inventory.hotbar[i]

            pygame.draw.rect(self.screen, (20, 16, 36),
                             (sx, hy, slot_w, slot_h), border_radius=6)
            pygame.draw.rect(self.screen, (60, 54, 90),
                             (sx, hy, slot_w, slot_h), 1, border_radius=6)

            if item:
                fill = pygame.Surface((slot_w - 4, slot_h - 4), pygame.SRCALPHA)
                fill.fill((*item.colour[:3], 170))
                self.screen.blit(fill, (sx + 2, hy + 2))
                ntxt = self._font_sm.render(item.name[:8], True, WHITE)
                self.screen.blit(ntxt, (sx + 3, hy + slot_h - 14))
                if item.stackable and item.stack_size > 1:
                    cnt = self._font_sm.render(str(item.stack_size), True, GOLD)
                    self.screen.blit(cnt, (sx + slot_w - cnt.get_width() - 3, hy + 3))

            kn = self._font_sm.render(str(i + 1), True, (80, 72, 110))
            self.screen.blit(kn, (sx + 3, hy + 3))

    # ── Minimap ───────────────────────────────────────────────────────────────
    def _draw_minimap(self, sw: int) -> None:
        w    = self._world
        ms   = self.MINIMAP_SIZE
        mx   = sw - ms - 10
        my   = 36

        mm   = pygame.Surface((ms, ms), pygame.SRCALPHA)
        mm.fill((8, 6, 16, 200))
        pygame.draw.rect(mm, (60, 55, 90), mm.get_rect(), 1, border_radius=4)

        gen     = w.dungeon
        sx      = ms / (gen.grid_w * TILE_SIZE)
        sy_s    = ms / (gen.grid_h * TILE_SIZE)

        ROOM_COLS = {
            "spawn":    (80, 120, 200),
            "boss":     (200, 50,  50),
            "treasure": (200, 170, 50),
            "shop":     (80, 200, 120),
            "exit":     (80, 220, 140),
            "elite":    (180, 80,  80),
            "puzzle":   (200, 140, 60),
            "secret":   (140, 80, 200),
            "normal":   (55,  50,  70),
        }

        for room in gen.rooms:
            rr   = room.world_rect()
            rmx  = int(rr.x * sx)
            rmy  = int(rr.y * sy_s)
            rmw  = max(3, int(rr.width  * sx))
            rmh  = max(3, int(rr.height * sy_s))
            col  = ROOM_COLS.get(room.room_type, (55, 50, 70))
            if room.visited:
                pygame.draw.rect(mm, col, (rmx, rmy, rmw, rmh), border_radius=2)
                pygame.draw.rect(mm, (100, 90, 130), (rmx, rmy, rmw, rmh), 1, border_radius=2)
            else:
                pygame.draw.rect(mm, (20, 18, 30), (rmx, rmy, rmw, rmh), border_radius=2)

        ppx = int(w.player.pos.x * sx)
        ppy = int(w.player.pos.y * sy_s)
        pygame.draw.circle(mm, (255, 255, 255), (ppx, ppy), 3)
        pygame.draw.circle(mm, (100, 200, 255), (ppx, ppy), 2)

        self.screen.blit(mm, (mx, my))
