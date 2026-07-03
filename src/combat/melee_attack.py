# Eclipse Depths - Melee attack hitbox

from __future__ import annotations
import pygame


class MeleeAttack(pygame.sprite.Sprite):
    """Short-lived hitbox for melee swings."""

    def __init__(self, x: float, y: float, facing_x: float, facing_y: float,
                 damage: float, reach: int = 40, arc_half: int = 50,
                 lifetime: float = 0.12, owner: str = "player",
                 knockback: float = 5.0, combo: int = 1) -> None:
        super().__init__()
        self.damage    = damage
        self.owner     = owner
        self.knockback = knockback
        self.combo     = combo
        self._age      = 0.0
        self.lifetime  = lifetime
        self.alive     = True

        # Position hitbox in front of attacker
        hx = int(x + facing_x * reach)
        hy = int(y + facing_y * reach)
        size = 36 + combo * 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        alpha = 120 if owner == "player" else 80
        pygame.draw.circle(self.image, (255, 255, 100, alpha), (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=(hx, hy))

        # Direction for knockback
        self._fx = facing_x
        self._fy = facing_y

    def update(self, dt: float, walls=None) -> None:
        self._age += dt
        if self._age >= self.lifetime:
            self.alive = False
            self.kill()

    def knockback_vec(self) -> pygame.math.Vector2:
        return pygame.math.Vector2(self._fx, self._fy) * self.knockback
