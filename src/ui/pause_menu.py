# Eclipse Depths - Pause Menu

from __future__ import annotations
import pygame
from src.core.constants import *
from src.ui.main_menu import Button


class PauseMenu:
    def __init__(self, screen: pygame.Surface, assets, bus) -> None:
        self.screen = screen
        self.assets = assets
        self.bus    = bus
        self._font  = assets.font(22, bold=True)
        self._font_btn = assets.font(17)

        sw, sh = screen.get_size()
        bw, bh = 220, 44
        bx     = sw // 2 - bw // 2

        self._buttons = [
            Button(bx, sh//2 - 60, bw, bh, "Resume",       self._font_btn),
            Button(bx, sh//2 - 4,  bw, bh, "Settings",     self._font_btn),
            Button(bx, sh//2 + 52, bw, bh, "Save & Quit",  self._font_btn),
            Button(bx, sh//2 + 108,bw, bh, "Main Menu",    self._font_btn,
                   colour=(70, 40, 40), hover_colour=(110, 55, 55)),
        ]
        self._actions = ["resume", "open_settings", "quit_to_menu_save", "goto_main_menu"]

    def handle_event(self, event: pygame.Event) -> None:
        for i, btn in enumerate(self._buttons):
            if btn.handle_event(event):
                if self._actions[i] == "quit_to_menu_save":
                    self.bus.publish("save_and_quit")
                    self.bus.publish("goto_main_menu")
                else:
                    self.bus.publish(self._actions[i])

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        sw, sh = self.screen.get_size()
        # Dim overlay
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Panel
        pw, ph = 280, 320
        px, py = sw//2 - pw//2, sh//2 - ph//2
        panel  = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((20, 16, 35, 230))
        pygame.draw.rect(panel, (80, 60, 120), panel.get_rect(), 2, border_radius=10)
        self.screen.blit(panel, (px, py))

        title = self._font.render("PAUSED", True, (200, 170, 255))
        self.screen.blit(title, (sw//2 - title.get_width()//2, py + 20))

        for btn in self._buttons:
            btn.draw(self.screen)
