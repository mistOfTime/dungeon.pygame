# Eclipse Depths - Projectile

from __future__ import annotations
import pygame
import math
from src.utils.helpers import normalise


class Projectile(pygame.sprite.Sprite):
    """Generic projectile used by player ranged attacks, enemy attacks, and spells."""

    def __init__(self, x: float, y: float, dx: float, dy: float,
                 speed: float, damage: float, owner: str,
                 colour: tuple = (255, 200, 50), radius: int = 5,
                 lifetime: float = 2.0, piercing: bool = False,
                 knockback: float = 3.0, spell_id: str = "") -> None:
        super().__init__()
        self.pos       = pygame.math.Vector2(x, y)
        dx, dy         = normalise(dx, dy)
        self.vel       = pygame.math.Vector2(dx * speed, dy * speed)
        self.damage    = damage
        self.owner     = owner     # "player" | "enemy"
        self.colour    = colour
        self.radius    = radius
        self.lifetime  = lifetime
        self._age      = 0.0
        self.piercing  = piercing
        self.knockback = knockback
        self.spell_id  = spell_id
        self.alive     = True

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, colour, (radius, radius), radius)
        # Glow ring
        pygame.draw.circle(self.image, (*colour[:3], 100), (radius, radius), radius + 2, 2)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, dt: float, walls: list[pygame.Rect]) -> None:
        self._age += dt
        if self._age >= self.lifetime:
            self.alive = False
            self.kill()
            return

        self.pos += self.vel * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        for wall in walls:
            if self.rect.colliderect(wall):
                self.alive = False
                self.kill()
                return

    def knockback_vec(self) -> pygame.math.Vector2:
        if self.vel.length() > 0:
            return self.vel.normalize() * self.knockback
        return pygame.math.Vector2(0, 0)
