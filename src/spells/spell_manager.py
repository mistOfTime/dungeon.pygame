# Eclipse Depths - Spell Manager

from __future__ import annotations
import pygame
import math
from src.utils.timer import Timer
from src.combat.projectile import Projectile


SPELLS: dict[str, dict] = {
    "fireball": {
        "name": "Fireball", "mana_cost": 15, "cooldown": 1.2,
        "colour": (255, 100, 30), "radius": 7, "speed": 320, "damage": 28,
        "lifetime": 2.0, "knockback": 6,
    },
    "ice_blast": {
        "name": "Ice Blast", "mana_cost": 12, "cooldown": 0.9,
        "colour": (100, 200, 255), "radius": 6, "speed": 280, "damage": 20,
        "lifetime": 1.8, "knockback": 4,
    },
    "lightning": {
        "name": "Lightning Bolt", "mana_cost": 20, "cooldown": 1.6,
        "colour": (220, 220, 50), "radius": 5, "speed": 480, "damage": 38,
        "lifetime": 1.2, "knockback": 8, "piercing": True,
    },
    "poison_cloud": {
        "name": "Poison Cloud", "mana_cost": 18, "cooldown": 2.0,
        "colour": (80, 200, 80), "radius": 8, "speed": 180, "damage": 12,
        "lifetime": 3.0, "knockback": 2,
    },
    "heal": {
        "name": "Heal", "mana_cost": 25, "cooldown": 4.0,
        "colour": (100, 255, 100), "radius": 0, "speed": 0, "damage": 0,
        "lifetime": 0, "heal": 40,
    },
    "magic_shield": {
        "name": "Magic Shield", "mana_cost": 30, "cooldown": 8.0,
        "colour": (100, 150, 255), "radius": 0, "speed": 0, "damage": 0,
        "lifetime": 5.0, "shield": True,
    },
    "dash_spell": {
        "name": "Dash Spell", "mana_cost": 10, "cooldown": 2.0,
        "colour": (200, 100, 255), "radius": 0, "speed": 0, "damage": 0,
        "lifetime": 0, "dash": True,
    },
}


class SpellManager:
    """Manages equipped spells, cooldowns, and casting."""

    MAX_EQUIPPED = 4

    def __init__(self, bus) -> None:
        self._bus     = bus
        self._spells  = ["fireball", "ice_blast", "heal", "dash_spell"]
        self._cds:    dict[str, Timer] = {}
        self._shield_active   = False
        self._shield_timer    = Timer(5.0)
        self._reload_cds()

    def _reload_cds(self) -> None:
        for sid in self._spells:
            if sid and sid not in self._cds:
                self._cds[sid] = Timer(SPELLS[sid]["cooldown"])

    def equip_spell(self, slot: int, spell_id: str) -> None:
        if 0 <= slot < self.MAX_EQUIPPED:
            self._spells[slot] = spell_id
            self._cds[spell_id] = Timer(SPELLS[spell_id]["cooldown"])

    def cast(self, slot: int, player, projectiles: pygame.sprite.Group) -> None:
        if slot >= len(self._spells):
            return
        sid = self._spells[slot]
        if not sid:
            return
        data = SPELLS[sid]
        cd   = self._cds.get(sid)
        if cd and not cd.done:
            return
        if player.mana < data["mana_cost"]:
            self._bus.publish("notification", {"text": "Not enough mana!", "colour": (100, 150, 255)})
            return

        player.mana -= data["mana_cost"]
        if cd:
            cd.start()

        if sid == "heal":
            player.heal(data["heal"])
            self._bus.publish("sfx", {"key": "spell_heal"})
            self._bus.publish("particle_burst", {"pos": (player.pos.x, player.pos.y),
                                                  "colour": (100, 255, 100), "count": 20})
        elif sid == "magic_shield":
            self._shield_active = True
            self._shield_timer.duration = data["lifetime"]
            self._shield_timer.start()
            self._bus.publish("sfx", {"key": "spell_shield"})
        elif sid == "dash_spell":
            player.pos += player.facing * 120
            self._bus.publish("sfx", {"key": "spell_dash"})
            self._bus.publish("particle_burst", {"pos": (player.pos.x, player.pos.y),
                                                  "colour": data["colour"], "count": 15})
        else:
            proj = Projectile(
                player.pos.x, player.pos.y,
                player.facing.x, player.facing.y,
                speed    = data["speed"],
                damage   = data["damage"],
                owner    = "player",
                colour   = data["colour"],
                radius   = data["radius"],
                lifetime = data["lifetime"],
                piercing = data.get("piercing", False),
                knockback= data.get("knockback", 3),
                spell_id = sid,
            )
            projectiles.add(proj)
            self._bus.publish("sfx", {"key": f"spell_{sid}"})

    def update(self, dt: float, player) -> None:
        for cd in self._cds.values():
            cd.update(dt)
        self._shield_timer.update(dt)
        if self._shield_timer.done:
            self._shield_active = False

    def is_shielded(self) -> bool:
        return self._shield_active

    def get_cooldown_progress(self, slot: int) -> float:
        if slot >= len(self._spells):
            return 1.0
        sid = self._spells[slot]
        if not sid:
            return 1.0
        cd = self._cds.get(sid)
        if cd is None:
            return 1.0
        return cd.progress

    @property
    def equipped(self) -> list[str]:
        return self._spells
