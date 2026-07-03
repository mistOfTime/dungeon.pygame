# Eclipse Depths - Quest Log

from __future__ import annotations
import pygame
from src.core.constants import *


class QuestLogScreen:
    def __init__(self, screen: pygame.Surface, assets, bus) -> None:
        self.screen     = screen
        self.assets     = assets
        self.bus        = bus
        self._qm        = None
        self._font      = assets.font(13)
        self._font_title= assets.font(20, bold=True)
        self._font_h    = assets.font(15, bold=True)
        self._scroll    = 0

    def set_quest_manager(self, qm) -> None:
        self._qm = qm

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.bus.publish("close_quest_log")
        if event.type == pygame.MOUSEWHEEL:
            self._scroll = max(0, self._scroll - event.y * 20)

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        sw, sh = self.screen.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        title = self._font_title.render("QUEST LOG", True, (220, 200, 100))
        self.screen.blit(title, (sw//2 - title.get_width()//2, 18))

        if not self._qm:
            return

        pw, ph = 700, sh - 100
        px, py = sw//2 - pw//2, 60
        panel  = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((12, 10, 24, 220))
        pygame.draw.rect(panel, (70, 60, 100), panel.get_rect(), 1, border_radius=8)
        self.screen.blit(panel, (px, py))

        y = py + 10 - self._scroll
        TYPES = [("main", "Main Quests", (200, 170, 80)),
                 ("side", "Side Quests", (80, 170, 200)),
                 ("daily","Daily",        (80, 220, 120)),
                 ("achievement","Achievements",(180, 120, 220))]

        for qtype, label, col in TYPES:
            quests = self._qm.get_active_by_type(qtype)
            if not quests:
                continue
            if py + 10 <= y <= py + ph:
                h_txt = self._font_h.render(label, True, col)
                self.screen.blit(h_txt, (px + 12, y))
            y += 24

            for q in quests:
                if py + 10 <= y <= py + ph:
                    done_col = (100, 220, 100) if q.completed else WHITE
                    prog = f"[{q.progress}/{q.target}]"
                    txt  = self._font.render(f"• {q.title} {prog} – {q.description}", True, done_col)
                    self.screen.blit(txt, (px + 20, y))
                    # Progress bar
                    from src.utils.helpers import draw_bar
                    draw_bar(self.screen, px + pw - 110, y + 2, 90, 8,
                             q.progress, q.target, (80, 200, 120))
                y += 20

            y += 8

        hint = self._font.render("Q / Esc – Close", True, MID_GREY)
        self.screen.blit(hint, (sw//2 - hint.get_width()//2, sh - 22))
