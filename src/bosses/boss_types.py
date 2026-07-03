# Eclipse Depths - Boss types

from __future__ import annotations
import pygame
import math
import random
from src.bosses.base_boss import BaseBoss
from src.combat.projectile import Projectile
from src.utils.timer import Timer


class SkeletonKing(BaseBoss):
    STATS = {
        "name": "Skeleton King", "hp": 280, "speed": 72, "damage": 22,
        "attack_range": 48, "chase_range": 300, "attack_cd": 1.0,
        "xp": 200, "gold_min": 20, "gold_max": 40,
        "colour": (220, 220, 200), "size": (44, 52), "knockback": 10.0,
    }
    PHASE_THRESHOLDS = [0.5]

    def _draw_sprite_frame(self, t, hit):
        from src.bosses.sprites import draw_skeleton_king
        draw_skeleton_king(self.image, t, self.phase, hit)

    def _do_attack(self, player, projectiles):
        if self.phase == 1:
            # Summon bone projectiles in a cross
            for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
                proj = Projectile(
                    self.pos.x, self.pos.y,
                    math.cos(angle), math.sin(angle),
                    speed=200, damage=self.damage * 0.7, owner="enemy",
                    colour=(220, 220, 190), radius=5, lifetime=2.0,
                )
                projectiles.add(proj)
        else:
            # Phase 2: 8-way spread + direct
            for i in range(8):
                angle = i * math.pi / 4
                proj  = Projectile(
                    self.pos.x, self.pos.y,
                    math.cos(angle), math.sin(angle),
                    speed=240, damage=self.damage * 0.5, owner="enemy",
                    colour=(255, 100, 80), radius=5, lifetime=2.5,
                )
                projectiles.add(proj)
        self.bus.publish("sfx", {"key": "boss_attack"})


class FireDragon(BaseBoss):
    STATS = {
        "name": "Fire Dragon", "hp": 380, "speed": 85, "damage": 28,
        "attack_range": 220, "chase_range": 320, "attack_cd": 1.4,
        "xp": 350, "gold_min": 35, "gold_max": 60,
        "colour": (220, 80, 30), "size": (56, 48), "knockback": 12.0,
    }
    PHASE_THRESHOLDS = [0.66, 0.33]

    def _draw_sprite_frame(self, t, hit):
        from src.bosses.sprites import draw_fire_dragon
        draw_fire_dragon(self.image, t, self.phase, hit)

    def _do_attack(self, player, projectiles):
        count = 3 + self.phase * 2
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y
        base_angle = math.atan2(dy, dx)
        spread = math.pi / 6
        for i in range(count):
            a = base_angle + (i - count//2) * (spread / max(count - 1, 1))
            proj = Projectile(
                self.pos.x, self.pos.y,
                math.cos(a), math.sin(a),
                speed=280, damage=self.damage, owner="enemy",
                colour=(255, 140, 20), radius=6, lifetime=2.0, knockback=5,
            )
            projectiles.add(proj)
        self.bus.publish("sfx", {"key": "spell_fireball"})


class AncientGolem(BaseBoss):
    STATS = {
        "name": "Ancient Golem", "hp": 500, "speed": 50, "damage": 35,
        "attack_range": 52, "chase_range": 260, "attack_cd": 2.0,
        "xp": 400, "gold_min": 40, "gold_max": 70,
        "colour": (120, 100, 80), "size": (60, 60), "knockback": 18.0,
    }
    PHASE_THRESHOLDS = [0.5]

    def _draw_sprite_frame(self, t, hit):
        from src.bosses.sprites import draw_ancient_golem
        draw_ancient_golem(self.image, t, self.phase, hit)

    def __init__(self, x, y, bus, floor=1):
        super().__init__(x, y, bus, floor)
        self._stomp_timer = Timer(3.0, auto_reset=True)
        self._stomp_timer.start()

    def update(self, dt, player, walls, dungeon_gen, projectiles):
        super().update(dt, player, walls, dungeon_gen, projectiles)
        if not self._is_in_intro:
            self._stomp_timer.update(dt)
            if self._stomp_timer.done:
                self._stomp(player)

    def _stomp(self, player):
        dist = math.hypot(player.pos.x - self.pos.x, player.pos.y - self.pos.y)
        if dist < 100:
            player.take_damage(self.damage * 0.6)
        self.bus.publish("camera_shake", {"magnitude": 10})
        self.bus.publish("sfx", {"key": "boss_stomp"})


class ShadowKnight(BaseBoss):
    STATS = {
        "name": "Shadow Knight", "hp": 320, "speed": 95, "damage": 26,
        "attack_range": 50, "chase_range": 300, "attack_cd": 0.9,
        "xp": 300, "gold_min": 30, "gold_max": 55,
        "colour": (50, 40, 80), "size": (46, 52), "knockback": 9.0,
    }
    PHASE_THRESHOLDS = [0.4]

    def _draw_sprite_frame(self, t, hit):
        from src.bosses.sprites import draw_shadow_knight
        draw_shadow_knight(self.image, t, self.phase, hit)

    def __init__(self, x, y, bus, floor=1):
        super().__init__(x, y, bus, floor)
        self._dash_timer = Timer(4.0, auto_reset=True)
        self._dash_timer.start()

    def update(self, dt, player, walls, dungeon_gen, projectiles):
        super().update(dt, player, walls, dungeon_gen, projectiles)
        if not self._is_in_intro:
            self._dash_timer.update(dt)
            if self._dash_timer.done:
                self._shadow_dash(player)

    def _shadow_dash(self, player):
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y
        d  = math.hypot(dx, dy)
        if d > 0:
            self.pos.x += dx/d * 160
            self.pos.y += dy/d * 160
        self.bus.publish("particle_burst", {
            "pos": (self.pos.x, self.pos.y), "colour": (80, 40, 140), "count": 20})
        self.bus.publish("sfx", {"key": "spell_dash"})


class AbyssMage(BaseBoss):
    STATS = {
        "name": "Abyss Mage", "hp": 260, "speed": 60, "damage": 32,
        "attack_range": 280, "chase_range": 320, "attack_cd": 1.8,
        "xp": 320, "gold_min": 30, "gold_max": 60,
        "colour": (60, 20, 100), "size": (42, 46), "knockback": 4.0,
    }
    PHASE_THRESHOLDS = [0.5]

    def _draw_sprite_frame(self, t, hit):
        from src.bosses.sprites import draw_abyss_mage
        draw_abyss_mage(self.image, t, self.phase, hit)

    def _do_attack(self, player, projectiles):
        # Spiral attack
        count = 6 + (self.phase - 1) * 4
        t     = pygame.time.get_ticks() * 0.002
        for i in range(count):
            angle = t + i * (math.tau / count)
            proj  = Projectile(
                self.pos.x, self.pos.y,
                math.cos(angle), math.sin(angle),
                speed=170, damage=self.damage * 0.5, owner="enemy",
                colour=(200, 80, 255), radius=5, lifetime=2.5, knockback=3,
            )
            projectiles.add(proj)
        self.bus.publish("sfx", {"key": "spell_lightning"})


# __ Factory __________________________________________________________________
BOSS_BY_FLOOR: dict[int, type] = {
    1: SkeletonKing,
    2: FireDragon,
    3: AncientGolem,
    4: ShadowKnight,
    5: AbyssMage,
}


def get_boss_for_floor(floor: int) -> type:
    # Cycle through bosses
    idx = ((floor - 1) % len(BOSS_BY_FLOOR)) + 1
    return BOSS_BY_FLOOR[idx]
