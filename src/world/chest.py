# Eclipse Depths - Treasure Chest

from __future__ import annotations
import pygame
import random
from src.items.item_data import generate_weapon, generate_armor, generate_accessory, make_consumable
from src.world.loot_drop import LootDrop


class Chest(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, assets, bus, floor: int = 1,
                 rare: bool = True) -> None:
        super().__init__()
        self.assets  = assets
        self.bus     = bus
        self.floor   = floor
        self.rare    = rare
        self.opened  = False

        self.image   = self._make_image(False)
        self.rect    = self.image.get_rect(center=(int(x), int(y)))

    def _make_image(self, opened: bool) -> pygame.Surface:
        w, h = 28, 24
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        base_col = (180, 140, 60) if not opened else (100, 80, 40)
        lid_col  = (220, 180, 80) if not opened else (120, 90, 50)
        # Body
        pygame.draw.rect(surf, base_col, (2, h//2, w-4, h//2 - 2), border_radius=3)
        # Lid
        pygame.draw.rect(surf, lid_col, (2, 2, w-4, h//2), border_radius=3)
        # Lock
        if not opened:
            pygame.draw.circle(surf, (200, 170, 50), (w//2, h//2 + 2), 4)
            pygame.draw.circle(surf, (255, 215, 0),  (w//2, h//2 + 2), 2)
        # Border
        pygame.draw.rect(surf, (100, 80, 30), (2, 2, w-4, h-4), 1, border_radius=3)
        return surf

    def open(self, player, loot_group: pygame.sprite.Group) -> None:
        if self.opened:
            return
        self.opened  = True
        self.image   = self._make_image(True)

        # Generate loot based on rarity
        drops = []
        if self.rare:
            rolls = random.randint(2, 4)
            roll_funcs = [
                lambda: LootDrop.weapon(self.rect.centerx, self.rect.centery, self.floor),
                lambda: LootDrop.armor(self.rect.centerx, self.rect.centery, self.floor),
                lambda: LootDrop.accessory(self.rect.centerx, self.rect.centery, self.floor),
            ]
            for _ in range(rolls):
                drop = random.choice(roll_funcs)()
                drops.append(drop)
            drops.append(LootDrop.gold(self.rect.centerx, self.rect.centery,
                                        random.randint(10, 40)))
        else:
            drops.append(LootDrop.consumable(self.rect.centerx, self.rect.centery))
            drops.append(LootDrop.gold(self.rect.centerx, self.rect.centery,
                                        random.randint(3, 15)))

        import math
        for i, drop in enumerate(drops):
            angle  = i * (math.tau / max(len(drops), 1))
            drop.rect.center = (
                self.rect.centerx + int(math.cos(angle) * 30),
                self.rect.centery + int(math.sin(angle) * 30),
            )
            drop._base_y = drop.rect.centery
            loot_group.add(drop)

        self.bus.publish("sfx", {"key": "chest_open"})
        self.bus.publish("particle_burst", {
            "pos":    self.rect.center,
            "colour": (255, 215, 0),
            "count":  20,
        })

    def update(self, dt: float) -> None:
        pass
