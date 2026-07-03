# Eclipse Depths - Camera

from __future__ import annotations
import pygame
import math
import random
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, CAMERA_SMOOTHING, CAMERA_SHAKE_DECAY


class Camera:
    """Smooth-follow camera with shake support."""

    def __init__(self, screen_w: int = SCREEN_WIDTH, screen_h: int = SCREEN_HEIGHT) -> None:
        self.screen_w  = screen_w
        self.screen_h  = screen_h
        self.x         = 0.0
        self.y         = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self._shake    = 0.0          # current magnitude
        self._shake_x  = 0.0
        self._shake_y  = 0.0
        self.zoom      = 1.0
        self._zoom_target = 1.0

    # __ Public API _________________________________________________________
    def follow(self, entity) -> None:
        """Set the entity whose centre the camera should track."""
        self._target_x = entity.rect.centerx - self.screen_w / 2
        self._target_y = entity.rect.centery - self.screen_h / 2

    def shake(self, magnitude: float = 8.0) -> None:
        self._shake = max(self._shake, magnitude)

    def set_zoom(self, z: float) -> None:
        self._zoom_target = max(0.5, min(2.0, z))

    def update(self, dt: float) -> None:
        factor = min(1.0, CAMERA_SMOOTHING * dt)
        self.x += (self._target_x - self.x) * factor
        self.y += (self._target_y - self.y) * factor

        # Zoom smoothing
        self.zoom += (self._zoom_target - self.zoom) * factor

        # Shake
        if self._shake > 0:
            angle = random.uniform(0, math.tau)
            self._shake_x = math.cos(angle) * self._shake
            self._shake_y = math.sin(angle) * self._shake
            self._shake  -= CAMERA_SHAKE_DECAY * dt
            if self._shake < 0:
                self._shake = 0.0
                self._shake_x = 0.0
                self._shake_y = 0.0
        else:
            self._shake_x = 0.0
            self._shake_y = 0.0

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Return a screen-space rect from a world-space rect."""
        return pygame.Rect(
            int(rect.x - self.x + self._shake_x),
            int(rect.y - self.y + self._shake_y),
            rect.width,
            rect.height,
        )

    def apply_pos(self, x: float, y: float) -> tuple[int, int]:
        return (int(x - self.x + self._shake_x),
                int(y - self.y + self._shake_y))

    def world_pos(self, screen_x: int, screen_y: int) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        return (screen_x + self.x - self._shake_x,
                screen_y + self.y - self._shake_y)

    @property
    def offset(self) -> tuple[float, float]:
        return (self.x - self._shake_x, self.y - self._shake_y)
