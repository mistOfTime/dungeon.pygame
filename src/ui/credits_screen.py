# Eclipse Depths - Credits Screen

from __future__ import annotations
import pygame
from src.core.constants import *


CREDITS_TEXT = """
ECLIPSE DEPTHS

A Roguelike Dungeon Crawler

_____________________
CREATED BY
_____________________
  mistOfTime

_____________________
DEVELOPMENT
_____________________
Programming & Design
  Eclipse Depths Team

_____________________
TECHNOLOGY
_____________________
Python 3.13+
Pygame Community Edition
Custom Particle Engine
A* Pathfinding

_____________________
ASSETS
_____________________
Art  _ Kenney.nl / CraftPix / itch.io
Audio _ Kenney Audio / Freesound

_____________________
SPECIAL THANKS
_____________________
The Pygame Community
All open-source contributors

_____________________

Thank you for playing!
"""


class CreditsScreen:
    def __init__(self, screen: pygame.Surface, assets, bus) -> None:
        self.screen = screen
        self.assets = assets
        self.bus    = bus
        self._font  = assets.font(15)
        self._y     = float(screen.get_height())
        self._lines = CREDITS_TEXT.strip().split("\n")

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.bus.publish("close_credits")
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bus.publish("close_credits")

    def update(self, dt: float) -> None:
        self._y -= 40 * dt
        total_h = len(self._lines) * 22
        if self._y < -total_h:
            self.bus.publish("close_credits")

    def draw(self) -> None:
        sw, sh = self.screen.get_size()
        self.screen.fill((6, 4, 14))
        y = int(self._y)
        for line in self._lines:
            if not line.strip():
                y += 14
                continue
            col = (200, 170, 255) if line.startswith("_") else (
                  (255, 215, 0)  if line.isupper() and len(line) > 4 else
                  (180, 180, 200))
            txt = self._font.render(line, True, col)
            self.screen.blit(txt, (sw//2 - txt.get_width()//2, y))
            y  += 22

        hint = self._font.render("Click or Esc to return", True, MID_GREY)
        self.screen.blit(hint, (sw//2 - hint.get_width()//2, sh - 22))
