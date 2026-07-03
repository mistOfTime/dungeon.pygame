# Eclipse Depths - Game Over Screen

from __future__ import annotations
import pygame
import math
from src.core.constants import *
from src.ui.main_menu import Button


class GameOverScreen:
    def __init__(self, screen: pygame.Surface, assets, bus) -> None:
        self.screen  = screen
        self.assets  = assets
        self.bus     = bus
        self._t      = 0.0
        self._font_title = assets.font(44, bold=True)
        self._font_body  = assets.font(16)
        self._font_btn   = assets.font(17)
        sw, sh = screen.get_size()
        bw, bh = 200, 42
        bx     = sw // 2 - bw // 2
        self._buttons = [
            Button(bx, sh//2 + 80,  bw, bh, "New Run",    self._font_btn),
            Button(bx, sh//2 + 136, bw, bh, "Main Menu",  self._font_btn,
                   colour=(60, 35, 35), hover_colour=(100, 50, 50)),
        ]

    def handle_event(self, event: pygame.Event) -> None:
        for i, btn in enumerate(self._buttons):
            if btn.handle_event(event):
                if i == 0:
                    self.bus.publish("new_game")
                else:
                    self.bus.publish("goto_main_menu")

    def update(self, dt: float) -> None:
        self._t += dt

    def draw(self) -> None:
        sw, sh = self.screen.get_size()
        # Animated dark background
        self.screen.fill((8, 5, 12))
        # Blood vignette
        for r in range(5, 0, -1):
            vsurf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            alpha = int(40 * (6 - r))
            pygame.draw.rect(vsurf, (120, 0, 0, alpha),
                             vsurf.get_rect().inflate(-r*80, -r*50))
            self.screen.blit(vsurf, (0, 0))

        t = self._t
        alpha = min(255, int(t * 120))
        title = self._font_title.render("YOU DIED", True, (200, 30, 30))
        title.set_alpha(alpha)
        self.screen.blit(title, (sw//2 - title.get_width()//2,
                                  sh//2 - 140 + int(math.sin(t) * 3)))

        sub = self._font_body.render("The depths have claimed you...", True, (160, 80, 80))
        sub.set_alpha(min(255, int((t - 0.5) * 200)))
        self.screen.blit(sub, (sw//2 - sub.get_width()//2, sh//2 - 60))

        for btn in self._buttons:
            btn.draw(self.screen)
