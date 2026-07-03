# Eclipse Depths - Floating damage numbers

from __future__ import annotations
import pygame
from src.utils.helpers import clamp


class DamageNumber:
    __slots__ = ("x","y","text","colour","life","max_life","vy","font","is_crit")

    def __init__(self, x: float, y: float, text: str,
                 colour: tuple, font: pygame.font.Font,
                 is_crit: bool = False) -> None:
        self.x        = float(x)
        self.y        = float(y)
        self.text     = text
        self.colour   = colour
        self.is_crit  = is_crit
        self.max_life = 1.0 if not is_crit else 1.4
        self.life     = self.max_life
        self.vy       = -60.0 if not is_crit else -90.0
        self.font     = font

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.y    += self.vy * dt
        self.vy   += 20 * dt
        return self.life > 0

    def draw(self, surface: pygame.Surface, cam_ox: float, cam_oy: float) -> None:
        alpha  = int(clamp(self.life / self.max_life, 0, 1) * 255)
        size   = 14 if not self.is_crit else 20
        text_surf = self.font.render(self.text, True, self.colour)
        if self.is_crit:
            outline = self.font.render(self.text, True, (0, 0, 0))
            sx = int(self.x - cam_ox) - text_surf.get_width()//2
            sy = int(self.y - cam_oy)
            for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
                surface.blit(outline, (sx+ddx, sy+ddy))
        text_surf.set_alpha(alpha)
        sx = int(self.x - cam_ox) - text_surf.get_width()//2
        sy = int(self.y - cam_oy)
        surface.blit(text_surf, (sx, sy))


class DamageNumberManager:
    def __init__(self, assets) -> None:
        self._numbers: list[DamageNumber] = []
        self._font_normal = assets.font(14)
        self._font_crit   = assets.font(20, bold=True)

    def add(self, x: float, y: float, value: int,
            colour: tuple = (255, 220, 80), is_crit: bool = False) -> None:
        text = str(value) if not is_crit else f"★{value}"
        font = self._font_crit if is_crit else self._font_normal
        self._numbers.append(DamageNumber(x, y, text, colour, font, is_crit))

    def update(self, dt: float) -> None:
        self._numbers = [n for n in self._numbers if n.update(dt)]

    def draw(self, surface: pygame.Surface, camera) -> None:
        ox, oy = camera.offset
        for n in self._numbers:
            n.draw(surface, ox, oy)
