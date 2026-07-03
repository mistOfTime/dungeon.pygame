# Eclipse Depths - Utility helpers

from __future__ import annotations
import math
import random
import pygame
from typing import Any


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def distance(ax: float, ay: float, bx: float, by: float) -> float:
    return math.hypot(bx - ax, by - ay)


def normalise(dx: float, dy: float) -> tuple[float, float]:
    mag = math.hypot(dx, dy)
    if mag == 0:
        return 0.0, 0.0
    return dx / mag, dy / mag


def angle_to(ax: float, ay: float, bx: float, by: float) -> float:
    return math.atan2(by - ay, bx - ax)


def random_colour(base: tuple, variance: int = 30) -> tuple:
    return tuple(clamp(c + random.randint(-variance, variance), 0, 255) for c in base[:3])


def draw_bar(surface: pygame.Surface, x: int, y: int, w: int, h: int,
             value: float, maximum: float, fg: tuple, bg: tuple = (40, 40, 50),
             border: tuple | None = (0, 0, 0), radius: int = 3) -> None:
    ratio = clamp(value / maximum, 0, 1) if maximum else 0
    pygame.draw.rect(surface, bg,  (x, y, w, h), border_radius=radius)
    if ratio > 0:
        pygame.draw.rect(surface, fg, (x, y, int(w * ratio), h), border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, (x, y, w, h), 1, border_radius=radius)


def weighted_choice(options: list[tuple[Any, float]]) -> Any:
    """Pick from [(value, weight), ...] pairs."""
    total  = sum(w for _, w in options)
    r      = random.uniform(0, total)
    for val, w in options:
        r -= w
        if r <= 0:
            return val
    return options[-1][0]


def screen_fade(surface: pygame.Surface, alpha: int, colour: tuple = (0, 0, 0)) -> None:
    overlay = pygame.Surface(surface.get_size())
    overlay.fill(colour)
    overlay.set_alpha(alpha)
    surface.blit(overlay, (0, 0))
