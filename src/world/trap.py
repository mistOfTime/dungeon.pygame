# Eclipse Depths - Floor Trap

from __future__ import annotations
import pygame
from src.utils.timer import Timer


class Trap(pygame.sprite.Sprite):
    """Pressure plate trap that damages the player on contact."""

    DAMAGE = 12.0
    COOLDOWN = 2.0

    def __init__(self, x: float, y: float, assets, bus) -> None:
        super().__init__()
        self.bus       = bus
        self.triggered = False
        self._cd       = Timer(self.COOLDOWN)
        self._flash    = Timer(0.2)
        self._visible  = True

        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self._draw(False)
        self.rect  = self.image.get_rect(center=(int(x), int(y)))

    def _draw(self, active: bool) -> None:
        self.image.fill((0, 0, 0, 0))
        col  = (200, 50, 50) if active else (160, 40, 40)
        col2 = (255, 100, 50) if active else (100, 30, 30)
        w, h = self.image.get_size()
        # Spikes
        for i in range(3):
            sx = 4 + i * 8
            pygame.draw.polygon(self.image, col,
                                 [(sx, h-4), (sx+4, h-4), (sx+2, 4 if active else 10)])
        pygame.draw.rect(self.image, col2, (2, h-6, w-4, 4), border_radius=1)

    def update(self, dt: float, player) -> None:
        self._cd.update(dt)
        self._flash.update(dt)

        if self._cd.done and self.rect.colliderect(player.hitbox):
            player.take_damage(self.DAMAGE)
            self.bus.publish("sfx", {"key": "trap_trigger"})
            self.bus.publish("particle_burst", {
                "pos":    self.rect.center,
                "colour": (220, 60, 60),
                "count":  10,
            })
            self._cd.start()
            self._flash.start()
            self._draw(True)
        else:
            if self._flash.done:
                self._draw(False)
