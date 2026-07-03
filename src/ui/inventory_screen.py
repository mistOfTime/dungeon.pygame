# Eclipse Depths - Inventory Screen (rewritten)

from __future__ import annotations
import pygame
from src.core.constants import *
from src.inventory.inventory import (INVENTORY_COLS, INVENTORY_ROWS,
                                      EQUIPMENT_SLOTS, HOTBAR_SIZE)
from src.utils.helpers import draw_bar, clamp

SLOT_SIZE   = 52
SLOT_PAD    = 5
PANEL_BG    = (14, 11, 26, 240)
SLOT_BG     = (24, 20, 40)
SLOT_BORDER = (55, 48, 82)
SLOT_HOVER  = (70, 60, 100)
EQUIP_BG    = (20, 16, 36)
EQUIP_LABEL_COL = (140, 130, 170)

RARITY_GLOW = {
    "Common":    (0,   0,   0,   0),
    "Uncommon":  (30,  200, 80,  60),
    "Rare":      (60,  130, 230, 80),
    "Epic":      (160, 50,  240, 100),
    "Legendary": (255, 165, 0,   120),
    "Mythic":    (220, 50,  80,  140),
}


class InventoryScreen:
    """
    Drag-and-drop inventory.
    - Left-click drag  : move item between slots
    - Right-click      : quick-equip / quick-unequip
    - Double-click     : use consumable
    - Hover            : tooltip
    """

    def __init__(self, screen: pygame.Surface, assets, bus) -> None:
        self.screen  = screen
        self.assets  = assets
        self.bus     = bus
        self.player  = None
        self._font_sm  = assets.font(12)
        self._font_med = assets.font(14)
        self._font_ttl = assets.font(20, bold=True)
        self._font_big = assets.font(16, bold=True)

        # Drag state
        self._drag_item  = None
        self._drag_from  = None   # ("inv", idx) | ("equip", slot_name)
        self._drag_pos   = (0, 0)

        # Tooltip
        self._tooltip_item = None
        self._tooltip_pos  = (0, 0)

        # Double-click detection
        self._last_click_slot = None
        self._last_click_time = 0.0

        # Computed layout (set in _compute_layout)
        self._panel_rect = pygame.Rect(0, 0, 0, 0)
        self._inv_origin = (0, 0)   # top-left of slot grid
        self._eq_origin  = (0, 0)   # top-left of equipment column
        self._stats_origin = (0, 0)
        self._hotbar_origin = (0, 0)
        self._layout_done = False

    def set_player(self, player) -> None:
        self.player = player
        self._layout_done = False

    def _compute_layout(self) -> None:
        sw, sh = self.screen.get_size()

        # Dynamic slot size: shrink if screen is small
        available_w = sw - 40
        available_h = sh - 80

        # Equipment column: label(60) + slot
        eq_col_w  = 60 + SLOT_SIZE + SLOT_PAD
        # Inventory grid
        inv_grid_w = INVENTORY_COLS * (SLOT_SIZE + SLOT_PAD) + SLOT_PAD
        inv_grid_h = INVENTORY_ROWS * (SLOT_SIZE + SLOT_PAD) + SLOT_PAD
        # Stats panel
        stats_w   = 175
        # Hotbar row
        hotbar_h  = SLOT_SIZE + SLOT_PAD * 3 + 16

        total_w = eq_col_w + 12 + inv_grid_w + 12 + stats_w
        total_h = 44 + inv_grid_h + hotbar_h + 10   # title + grid + hotbar

        # If too wide, squeeze stats panel
        if total_w > available_w:
            stats_w = max(140, available_w - eq_col_w - 12 - inv_grid_w - 12 - 8)
            total_w = eq_col_w + 12 + inv_grid_w + 12 + stats_w

        # Centre the panel
        px = max(10, sw // 2 - total_w // 2)
        py = max(10, sh // 2 - total_h // 2)

        self._panel_rect    = pygame.Rect(px - 10, py - 8, total_w + 20, total_h + 16)
        self._eq_origin     = (px, py + 44)
        self._inv_origin    = (px + eq_col_w + 12, py + 44)
        self._stats_origin  = (px + eq_col_w + 12 + inv_grid_w + 12, py + 44)
        self._hotbar_origin = (px + eq_col_w + 12, py + 44 + inv_grid_h + 8)
        self._stats_w       = stats_w
        self._inv_grid_h    = inv_grid_h
        self._layout_done   = True

    # __ Slot rect helpers _____________________________________________________
    def _inv_slot_rect(self, col: int, row: int) -> pygame.Rect:
        ox, oy = self._inv_origin
        return pygame.Rect(ox + col * (SLOT_SIZE + SLOT_PAD) + SLOT_PAD,
                           oy + row * (SLOT_SIZE + SLOT_PAD) + SLOT_PAD,
                           SLOT_SIZE, SLOT_SIZE)

    def _equip_slot_rect(self, idx: int) -> pygame.Rect:
        ox, oy = self._eq_origin
        return pygame.Rect(ox + 56, oy + idx * (SLOT_SIZE + SLOT_PAD) + SLOT_PAD,
                           SLOT_SIZE, SLOT_SIZE)

    def _hotbar_slot_rect(self, idx: int) -> pygame.Rect:
        ox, oy = self._hotbar_origin
        return pygame.Rect(ox + SLOT_PAD + idx * (SLOT_SIZE + SLOT_PAD),
                           oy + SLOT_PAD, SLOT_SIZE, SLOT_SIZE)

    def _pos_to_inv_slot(self, pos) -> int | None:
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                if self._inv_slot_rect(col, row).collidepoint(pos):
                    return row * INVENTORY_COLS + col
        return None

    def _pos_to_equip_slot(self, pos) -> str | None:
        for i, name in enumerate(EQUIPMENT_SLOTS):
            if self._equip_slot_rect(i).collidepoint(pos):
                return name
        return None

    def _pos_to_hotbar_slot(self, pos) -> int | None:
        for i in range(HOTBAR_SIZE):
            if self._hotbar_slot_rect(i).collidepoint(pos):
                return i
        return None

    # __ Events ________________________________________________________________
    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_i):
            self.bus.publish("close_inventory")
            return
        if not self.player:
            return
        if not self._layout_done:
            self._compute_layout()

        if event.type == pygame.MOUSEMOTION:
            self._drag_pos = event.pos
            self._update_tooltip(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._start_drag(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._end_drag(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self._right_click(event.pos)

    def _update_tooltip(self, pos) -> None:
        if not self._layout_done:
            return
        inv = self.player.inventory
        idx = self._pos_to_inv_slot(pos)
        if idx is not None and inv.slots[idx]:
            self._tooltip_item = inv.slots[idx]
            self._tooltip_pos  = pos
            return
        slot_name = self._pos_to_equip_slot(pos)
        if slot_name and inv.equipment.get(slot_name):
            self._tooltip_item = inv.equipment[slot_name]
            self._tooltip_pos  = pos
            return
        self._tooltip_item = None

    def _start_drag(self, pos) -> None:
        if not self._layout_done:
            return
        inv = self.player.inventory
        idx = self._pos_to_inv_slot(pos)
        if idx is not None and inv.slots[idx]:
            self._drag_item = inv.slots[idx]
            self._drag_from = ("inv", idx)
            self._drag_pos  = pos
            return
        slot_name = self._pos_to_equip_slot(pos)
        if slot_name and inv.equipment.get(slot_name):
            self._drag_item = inv.equipment[slot_name]
            self._drag_from = ("equip", slot_name)
            self._drag_pos  = pos

    def _end_drag(self, pos) -> None:
        if not self._drag_item or not self._drag_from:
            self._drag_item = None
            return
        inv = self.player.inventory
        src_type, src_ref = self._drag_from

        dst_inv   = self._pos_to_inv_slot(pos)
        dst_equip = self._pos_to_equip_slot(pos)
        dst_hot   = self._pos_to_hotbar_slot(pos)

        if dst_inv is not None:
            if src_type == "inv":
                inv.swap(src_ref, dst_inv)
            elif src_type == "equip":
                # Move equip item to inventory slot
                old_at_dst = inv.slots[dst_inv]
                inv.slots[dst_inv] = inv.equipment[src_ref]
                inv.equipment[src_ref] = old_at_dst
        elif dst_equip is not None:
            if src_type == "inv":
                # Equip the item
                item = inv.slots[src_ref]
                if item and self._can_equip(item, dst_equip):
                    old = inv.equipment.get(dst_equip)
                    inv.equipment[dst_equip] = item
                    inv.slots[src_ref] = old
            elif src_type == "equip" and src_ref != dst_equip:
                # Swap two equip slots
                inv.equipment[src_ref], inv.equipment[dst_equip] = (
                    inv.equipment[dst_equip], inv.equipment[src_ref])
        elif dst_hot is not None and src_type == "inv":
            # Assign hotbar slot
            inv._hotbar[dst_hot] = inv.slots[src_ref]

        self._drag_item = None
        self._drag_from = None

    def _can_equip(self, item, slot_name: str) -> bool:
        if item.item_type == "weapon" and slot_name == "weapon":
            return True
        if item.item_type == "armor" and item.subtype == slot_name:
            return True
        if item.item_type in ("ring", "necklace") and item.subtype == slot_name:
            return True
        # Also allow matching subtype directly
        if item.subtype == slot_name:
            return True
        return False

    def _right_click(self, pos) -> None:
        if not self._layout_done:
            return
        inv = self.player.inventory
        # Right-click on equip slot _ unequip
        slot_name = self._pos_to_equip_slot(pos)
        if slot_name and inv.equipment.get(slot_name):
            inv.unequip(slot_name)
            return
        # Right-click on inventory slot _ auto-equip
        idx = self._pos_to_inv_slot(pos)
        if idx is not None and inv.slots[idx]:
            item = inv.slots[idx]
            slot = self._resolve_slot(item)
            if slot:
                old = inv.equipment.get(slot)
                inv.equipment[slot] = item
                inv.slots[idx] = old
                self.bus.publish("sfx", {"key": "equip"})

    def _resolve_slot(self, item) -> str | None:
        if item.item_type == "weapon":
            return "weapon"
        if item.item_type == "armor":
            return item.subtype if item.subtype in EQUIPMENT_SLOTS else None
        if item.subtype in EQUIPMENT_SLOTS:
            return item.subtype
        return None

    def update(self, dt: float) -> None:
        if not self._layout_done and self.player:
            self._compute_layout()

    # __ Draw _________________________________________________________________
    def draw(self) -> None:
        if not self.player:
            return
        if not self._layout_done:
            self._compute_layout()

        sw, sh = self.screen.get_size()

        # Full-screen dim
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Main panel
        panel = pygame.Surface(self._panel_rect.size, pygame.SRCALPHA)
        panel.fill(PANEL_BG)
        pygame.draw.rect(panel, (70, 55, 110), panel.get_rect(), 2, border_radius=10)
        self.screen.blit(panel, self._panel_rect.topleft)

        # Title
        title = self._font_ttl.render("INVENTORY", True, (200, 185, 255))
        self.screen.blit(title, (self._panel_rect.x + 14,
                                  self._panel_rect.y + 10))
        # Close hint
        close_txt = self._font_sm.render("I / Esc  _  Close", True, (80, 70, 110))
        self.screen.blit(close_txt, (self._panel_rect.right - close_txt.get_width() - 14,
                                      self._panel_rect.y + 14))

        self._draw_equipment_slots()
        self._draw_inventory_grid()
        self._draw_hotbar_row()
        self._draw_stats_panel()

        # Dragging ghost
        if self._drag_item:
            self._draw_drag_ghost()

        # Tooltip
        if self._tooltip_item and not self._drag_item:
            self._draw_tooltip()

    def _draw_slot(self, rect: pygame.Rect, item, label: str = "",
                   highlight: bool = False, is_dragged: bool = False) -> None:
        bg_col = SLOT_HOVER if highlight else (EQUIP_BG if label else SLOT_BG)
        pygame.draw.rect(self.screen, bg_col, rect, border_radius=6)

        if item and not is_dragged:
            # Rarity glow border
            glow = RARITY_GLOW.get(item.rarity, (0, 0, 0, 0))
            if glow[3] > 0:
                glow_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow, glow_surf.get_rect(), 3,
                                 border_radius=6)
                self.screen.blit(glow_surf, rect.topleft)

            # Item fill
            fill_col = (*item.colour[:3], 180)
            fill_surf = pygame.Surface((rect.width - 6, rect.height - 20),
                                        pygame.SRCALPHA)
            fill_surf.fill(fill_col)
            self.screen.blit(fill_surf, (rect.x + 3, rect.y + 3))

            # Item name (truncated)
            name_txt = self._font_sm.render(item.name[:10], True, WHITE)
            self.screen.blit(name_txt, (rect.x + 3, rect.bottom - 14))

            # Stack count
            if item.stackable and item.stack_size > 1:
                cnt = self._font_sm.render(str(item.stack_size), True, GOLD)
                self.screen.blit(cnt, (rect.right - cnt.get_width() - 3, rect.y + 3))
        elif is_dragged:
            # Show faded slot when item is being dragged from here
            pygame.draw.rect(self.screen, (35, 30, 55, 120), rect, border_radius=6)

        # Slot border
        border_col = (100, 90, 140) if highlight else SLOT_BORDER
        pygame.draw.rect(self.screen, border_col, rect, 1, border_radius=6)

        # Equipment slot label (drawn left of slot)
        if label:
            lbl = self._font_sm.render(label, True, EQUIP_LABEL_COL)
            ox_eq, oy_eq = self._eq_origin
            # Label sits to the left of the slot, right-aligned into 56px
            lx = ox_eq + 54 - lbl.get_width()
            ly_label = rect.centery - lbl.get_height() // 2
            self.screen.blit(lbl, (lx, ly_label))

    def _draw_equipment_slots(self) -> None:
        inv    = self.player.inventory
        mx, my = pygame.mouse.get_pos()
        for i, slot_name in enumerate(EQUIPMENT_SLOTS):
            rect   = self._equip_slot_rect(i)
            item   = inv.equipment.get(slot_name)
            hover  = rect.collidepoint(mx, my)
            is_drg = (self._drag_from == ("equip", slot_name))
            self._draw_slot(rect, item if not is_drg else None,
                            label=slot_name.capitalize()[:6],
                            highlight=hover, is_dragged=is_drg)

    def _draw_inventory_grid(self) -> None:
        inv    = self.player.inventory
        mx, my = pygame.mouse.get_pos()
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                idx    = row * INVENTORY_COLS + col
                rect   = self._inv_slot_rect(col, row)
                item   = inv.slots[idx]
                hover  = rect.collidepoint(mx, my)
                is_drg = (self._drag_from == ("inv", idx))
                self._draw_slot(rect, item if not is_drg else None,
                                highlight=hover, is_dragged=is_drg)

    def _draw_hotbar_row(self) -> None:
        inv    = self.player.inventory
        mx, my = pygame.mouse.get_pos()
        ox, oy = self._hotbar_origin
        lbl    = self._font_sm.render("Hotbar  (1_4):", True, EQUIP_LABEL_COL)
        self.screen.blit(lbl, (ox + SLOT_PAD, oy - 2))
        for i in range(HOTBAR_SIZE):
            rect  = self._hotbar_slot_rect(i)
            item  = inv.hotbar[i]
            hover = rect.collidepoint(mx, my)
            self._draw_slot(rect, item, highlight=hover)
            # Key number
            kn = self._font_sm.render(str(i + 1), True, (100, 90, 140))
            self.screen.blit(kn, (rect.x + 3, rect.y + 3))

    def _draw_stats_panel(self) -> None:
        p   = self.player
        ox, oy = self._stats_origin
        w   = getattr(self, '_stats_w', 175)
        h   = getattr(self, '_inv_grid_h',
                      INVENTORY_ROWS * (SLOT_SIZE + SLOT_PAD) + SLOT_PAD)
        panel  = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((18, 14, 32, 220))
        pygame.draw.rect(panel, (60, 50, 90), panel.get_rect(), 1, border_radius=8)
        self.screen.blit(panel, (ox, oy))

        title = self._font_big.render("CHARACTER", True, (180, 160, 240))
        self.screen.blit(title, (ox + 8, oy + 8))

        lines = [
            ("",                            WHITE),
            (f"Level  {p.level}",           GOLD),
            (f"HP     {int(p.hp)} / {int(p.max_hp)}", (220, 80, 80)),
            (f"Mana   {int(p.mana)} / {int(p.max_mana)}", (80, 130, 240)),
            (f"DMG    {int(p.attack_damage)}", (255, 180, 80)),
            (f"DEF    {int(p.defense)}",     (80, 200, 220)),
            (f"CRIT   {int(p.crit_chance * 100)}%", (255, 220, 50)),
            (f"SPD    {int(p.speed)}",       (80, 220, 120)),
            ("",                            WHITE),
            (f"Gold   {p.stats.gold}",      GOLD),
            (f"Kills  {p.stats.kills}",     (220, 100, 80)),
            (f"Floor  {p.stats.floors}",    (180, 160, 220)),
            ("",                            WHITE),
            (f"XP     {p.xp}/{p.xp_to_next}", (180, 220, 100)),
            (f"Skill pts  {p.skill_points}", (200, 160, 255)),
        ]
        ly = oy + 30
        for text, col in lines:
            if not text:
                ly += 5
                continue
            t = self._font_sm.render(text, True, col)
            self.screen.blit(t, (ox + 10, ly))
            ly += 17

        # XP bar
        from src.utils.helpers import draw_bar
        w2 = getattr(self, '_stats_w', 175)
        draw_bar(self.screen, ox + 8, ly + 4, w2 - 16, 8,
                 p.xp, p.xp_to_next, (180, 220, 100), radius=3)

    def _draw_drag_ghost(self) -> None:
        item = self._drag_item
        x, y = self._drag_pos
        size = SLOT_SIZE
        ghost = pygame.Surface((size, size), pygame.SRCALPHA)
        ghost.fill((*item.colour[:3], 140))
        pygame.draw.rect(ghost, (255, 255, 255, 100), ghost.get_rect(), 1, border_radius=5)
        name_t = self._font_sm.render(item.name[:10], True, WHITE)
        ghost.blit(name_t, (3, size - 14))
        self.screen.blit(ghost, (x - size // 2, y - size // 2))

    def _draw_tooltip(self) -> None:
        item = self._tooltip_item
        if not item:
            return
        mx, my = self._tooltip_pos
        sw, sh = self.screen.get_size()
        lines = [
            (item.name,        (200, 190, 255), True),
            (item.rarity,      item.colour,     False),
            (item.item_type.capitalize() + (f" / {item.subtype}" if item.subtype else ""),
             LIGHT_GREY, False),
            ("",               WHITE, False),
        ]
        s = item.stats
        stat_lines = [
            (f"Damage      {s.damage:.0f}",     s.damage > 0),
            (f"Defense     {s.defense:.0f}",    s.defense > 0),
            (f"HP Bonus    +{s.hp_bonus:.0f}", s.hp_bonus > 0),
            (f"Mana Bonus  +{s.mana_bonus:.0f}",s.mana_bonus > 0),
            (f"Speed       +{s.speed_bonus:.0f}",s.speed_bonus > 0),
            (f"Crit Chance +{s.crit_chance*100:.0f}%", s.crit_chance > 0),
            (f"Atk Speed   +{s.attack_speed:.2f}", s.attack_speed > 0),
            (f"Life Steal  {s.life_steal*100:.0f}%", s.life_steal > 0),
        ]
        for text, visible in stat_lines:
            if visible:
                lines.append((text, (220, 210, 180), False))

        lines.append(("", WHITE, False))
        lines.append((f"Value: {item.value} gold", GOLD, False))
        lines.append((f"Right-click: Equip/Unequip", (100, 90, 130), False))

        padding = 10
        line_h  = 16
        tt_w    = 200
        tt_h    = sum(line_h if l[0] else line_h // 2 for l in lines) + padding * 2

        tx = min(mx + 18, sw - tt_w - 6)
        ty = max(6, min(my - 10, sh - tt_h - 6))

        tt_surf = pygame.Surface((tt_w, tt_h), pygame.SRCALPHA)
        tt_surf.fill((12, 9, 22, 240))
        glow = RARITY_GLOW.get(item.rarity, (80, 75, 110, 0))
        border_col = glow[:3] if glow[3] > 0 else (80, 70, 110)
        pygame.draw.rect(tt_surf, border_col, tt_surf.get_rect(), 2, border_radius=6)
        self.screen.blit(tt_surf, (tx, ty))

        ly = ty + padding
        for text, col, bold in lines:
            if not text:
                ly += line_h // 2
                continue
            f   = self._font_big if bold else self._font_sm
            txt = f.render(text, True, col)
            self.screen.blit(txt, (tx + padding, ly))
            ly += line_h
