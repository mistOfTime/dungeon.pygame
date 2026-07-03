# Eclipse Depths - NPC

from __future__ import annotations
import pygame
import random
from src.items.item_data import generate_weapon, generate_armor, make_consumable


NPC_COLOURS = {
    "Merchant":   (220, 180, 80),
    "Blacksmith": (180, 100, 60),
    "Potion Seller": (80, 200, 120),
    "Quest Giver": (100, 160, 220),
}

NPC_SIZES = {
    "Merchant":   (26, 34),
    "Blacksmith": (30, 36),
    "Potion Seller": (24, 32),
    "Quest Giver":   (26, 34),
}


class NPC(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, npc_type: str,
                 assets, bus, floor: int = 1) -> None:
        super().__init__()
        self.npc_type = npc_type
        self.bus      = bus
        self.floor    = floor
        self._shop_items = self._generate_shop(floor)
        self._dialogue_index = 0

        w, h = NPC_SIZES.get(npc_type, (26, 32))
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self._draw(NPC_COLOURS.get(npc_type, (180, 180, 180)))
        self.rect  = self.image.get_rect(center=(int(x), int(y)))
        self._bob_timer = 0.0

    def _draw(self, colour: tuple) -> None:
        w, h = self.image.get_size()
        self.image.fill((0, 0, 0, 0))
        # Body
        pygame.draw.ellipse(self.image, colour, (3, h//3, w-6, h*2//3))
        # Head
        pygame.draw.circle(self.image, (220, 180, 140), (w//2, h//4+1), h//5+2)
        # Name badge
        pygame.draw.rect(self.image, (255, 255, 255, 60), (2, h//3 - 4, w-4, 5))
        # Eyes
        pygame.draw.circle(self.image, (40, 40, 60), (w//2 - 3, h//4), 2)
        pygame.draw.circle(self.image, (40, 40, 60), (w//2 + 3, h//4), 2)
        # Exclamation mark above head
        fnt = pygame.font.SysFont("consolas", 12, bold=True)
        txt = fnt.render("!", True, (255, 215, 0))
        self.image.blit(txt, (w//2 - txt.get_width()//2, 0))

    def _generate_shop(self, floor: int) -> list:
        items = []
        if self.npc_type == "Merchant":
            for _ in range(3):
                items.append(generate_weapon(floor))
            for _ in range(2):
                items.append(generate_armor(floor))
        elif self.npc_type == "Blacksmith":
            for _ in range(4):
                items.append(generate_weapon(floor))
        elif self.npc_type == "Potion Seller":
            for cid in ["health_potion", "mana_potion", "stamina_potion", "elixir"]:
                items.append(make_consumable(cid))
        return items

    def interact(self, player) -> None:
        self.bus.publish("open_shop", {
            "npc_type": self.npc_type,
            "items":    self._shop_items,
            "player":   player,
        })
        self.bus.publish("sfx", {"key": "npc_interact"})
        self.bus.publish("notification", {
            "text":   f"{self.npc_type}: Browse my wares!",
            "colour": NPC_COLOURS.get(self.npc_type, (200, 200, 200)),
        })

    def update(self, dt: float) -> None:
        self._bob_timer += dt
        import math
        bob = int(math.sin(self._bob_timer * 2.5) * 2)
        self.rect.y = self.rect.y  # position managed externally
