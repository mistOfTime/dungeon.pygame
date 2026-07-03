# Eclipse Depths - Loot Drop sprite

from __future__ import annotations
import pygame
import math
from src.items.item_data import (generate_weapon, generate_armor,
                                  generate_accessory, make_consumable, Item)


class LootDrop(pygame.sprite.Sprite):
    """World item that the player can walk over to pick up."""

    def __init__(self, x: float, y: float, item: Item | None = None,
                 gold: int = 0, assets=None) -> None:
        super().__init__()
        self.item      = item
        self.value     = gold
        self.item_type = "gold" if item is None else "item"
        self._age      = 0.0
        self._float_offset = 0.0

        w = h = 20
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        if self.item_type == "gold":
            pygame.draw.circle(self.image, (255, 215, 0), (w//2, h//2), w//2 - 1)
            pygame.draw.circle(self.image, (255, 240, 100), (w//2 - 3, h//2 - 3), 3)
        else:
            col = item.colour if item else (200, 200, 200)
            pygame.draw.rect(self.image, col, (2, 2, w-4, h-4), border_radius=3)
            pygame.draw.rect(self.image, (255,255,255,100), (2,2,w-4,h-4), 1, border_radius=3)

        self._base_y = y
        self.rect    = self.image.get_rect(center=(int(x), int(y)))

    def update(self, dt: float) -> None:
        self._age += dt
        self._float_offset = math.sin(self._age * 3.0) * 3.0
        self.rect.centery = int(self._base_y + self._float_offset)

    # __ Factory methods ______________________________________________________
    @classmethod
    def gold(cls, x, y, amount: int) -> "LootDrop":
        drop = cls(x, y, gold=amount)
        drop.value = amount
        return drop

    @classmethod
    def weapon(cls, x, y, floor: int = 1) -> "LootDrop":
        item = generate_weapon(floor)
        return cls(x, y, item=item)

    @classmethod
    def armor(cls, x, y, floor: int = 1) -> "LootDrop":
        item = generate_armor(floor)
        return cls(x, y, item=item)

    @classmethod
    def accessory(cls, x, y, floor: int = 1) -> "LootDrop":
        item = generate_accessory(floor)
        return cls(x, y, item=item)

    @classmethod
    def consumable(cls, x, y, cid: str = "health_potion") -> "LootDrop":
        import random
        options = ["health_potion", "mana_potion", "stamina_potion", "bomb"]
        item = make_consumable(random.choice(options))
        return cls(x, y, item=item)
