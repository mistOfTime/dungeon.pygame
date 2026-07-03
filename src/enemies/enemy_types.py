# Eclipse Depths - All enemy types

from __future__ import annotations
import pygame
import math
import random
from src.enemies.base_enemy import BaseEnemy, EnemyState
from src.combat.projectile import Projectile


class Slime(BaseEnemy):
    STATS = {
        "name": "Slime", "hp": 22, "speed": 60, "damage": 5,
        "attack_range": 30, "chase_range": 160, "attack_cd": 1.5,
        "xp": 8, "gold_min": 0, "gold_max": 3,
        "colour": (60, 200, 80), "size": (24, 20), "knockback": 2.0,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_slime
        draw_slime(self.image, t, hit)


class Goblin(BaseEnemy):
    STATS = {
        "name": "Goblin", "hp": 28, "speed": 100, "damage": 8,
        "attack_range": 34, "chase_range": 200, "attack_cd": 1.0,
        "xp": 12, "gold_min": 1, "gold_max": 6,
        "colour": (100, 170, 60), "size": (24, 28), "knockback": 3.0,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_goblin
        draw_goblin(self.image, t, hit)


class Skeleton(BaseEnemy):
    STATS = {
        "name": "Skeleton", "hp": 35, "speed": 75, "damage": 10,
        "attack_range": 36, "chase_range": 210, "attack_cd": 1.2,
        "xp": 15, "gold_min": 2, "gold_max": 7,
        "colour": (210, 210, 195), "size": (24, 32), "knockback": 4.0,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_skeleton
        draw_skeleton(self.image, t, hit)


class Archer(BaseEnemy):
    STATS = {
        "name": "Archer", "hp": 25, "speed": 85, "damage": 12,
        "attack_range": 220, "chase_range": 240, "attack_cd": 1.6,
        "xp": 18, "gold_min": 2, "gold_max": 8,
        "colour": (160, 130, 60), "size": (24, 30), "knockback": 2.0,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_archer
        draw_archer(self.image, t, hit)

    def _do_attack(self, player, projectiles):
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y
        d  = math.hypot(dx, dy)
        if d == 0: return
        proj = Projectile(
            self.pos.x, self.pos.y, dx, dy,
            speed=240, damage=self.damage, owner="enemy",
            colour=(220, 180, 50), radius=4, lifetime=1.8, knockback=3,
        )
        projectiles.add(proj)
        self.bus.publish("sfx", {"key": "arrow_shoot"})


class Bat(BaseEnemy):
    STATS = {
        "name": "Bat", "hp": 18, "speed": 130, "damage": 6,
        "attack_range": 28, "chase_range": 200, "attack_cd": 0.7,
        "xp": 8, "gold_min": 0, "gold_max": 2,
        "colour": (90, 60, 120), "size": (22, 16), "knockback": 1.5,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_bat
        draw_bat(self.image, t, hit)

    def _behaviour_chase(self, dt, player, dungeon_gen):
        # Bats fly directly (ignore pathfinding)
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y + math.sin(pygame.time.get_ticks() * 0.003) * 20
        d  = math.hypot(dx, dy)
        if d > 0:
            return pygame.math.Vector2(dx/d, dy/d) * self.speed
        return pygame.math.Vector2(0, 0)


class Wizard(BaseEnemy):
    STATS = {
        "name": "Wizard", "hp": 38, "speed": 65, "damage": 18,
        "attack_range": 200, "chase_range": 220, "attack_cd": 2.0,
        "xp": 25, "gold_min": 3, "gold_max": 10,
        "colour": (100, 80, 200), "size": (26, 32), "knockback": 2.0,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_wizard
        draw_wizard(self.image, t, hit)

    def _do_attack(self, player, projectiles):
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y
        d  = math.hypot(dx, dy)
        if d == 0: return
        # Triple spread
        for offset_angle in [-0.2, 0, 0.2]:
            angle = math.atan2(dy, dx) + offset_angle
            proj  = Projectile(
                self.pos.x, self.pos.y,
                math.cos(angle), math.sin(angle),
                speed=200, damage=self.damage * 0.6, owner="enemy",
                colour=(160, 100, 255), radius=5, lifetime=2.0, knockback=2,
            )
            projectiles.add(proj)
        self.bus.publish("sfx", {"key": "spell_fireball"})


class Ghost(BaseEnemy):
    STATS = {
        "name": "Ghost", "hp": 30, "speed": 90, "damage": 10,
        "attack_range": 32, "chase_range": 180, "attack_cd": 1.3,
        "xp": 20, "gold_min": 1, "gold_max": 5,
        "colour": (180, 200, 255), "size": (28, 32), "knockback": 2.0,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_ghost
        draw_ghost(self.image, t, hit)

    def _behaviour_chase(self, dt, player, dungeon_gen):
        # Ghosts move through walls
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y
        d  = math.hypot(dx, dy)
        return pygame.math.Vector2(dx/d, dy/d) * self.speed if d > 0 else pygame.math.Vector2(0,0)

    def _move(self, dt, vel, walls):
        # Ghosts ignore walls
        self.pos += vel * dt
        self.rect.center    = (int(self.pos.x), int(self.pos.y))
        self.hitbox.center  = self.rect.center


class GiantSpider(BaseEnemy):
    STATS = {
        "name": "Giant Spider", "hp": 55, "speed": 110, "damage": 14,
        "attack_range": 38, "chase_range": 200, "attack_cd": 1.0,
        "xp": 30, "gold_min": 3, "gold_max": 12,
        "colour": (80, 40, 20), "size": (36, 32), "knockback": 5.0,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_spider
        draw_spider(self.image, t, hit)


class DarkKnight(BaseEnemy):
    STATS = {
        "name": "Dark Knight", "hp": 90, "speed": 70, "damage": 20,
        "attack_range": 44, "chase_range": 200, "attack_cd": 1.4,
        "xp": 50, "gold_min": 8, "gold_max": 20,
        "colour": (50, 40, 80), "size": (34, 40), "knockback": 8.0,
    }
    def _draw_sprite_frame(self, t, hit):
        from src.enemies.sprites import draw_dark_knight
        draw_dark_knight(self.image, t, hit)


# ── Factory ──────────────────────────────────────────────────────────────────
ENEMY_CLASSES = {
    "slime":        Slime,
    "goblin":       Goblin,
    "skeleton":     Skeleton,
    "archer":       Archer,
    "bat":          Bat,
    "wizard":       Wizard,
    "ghost":        Ghost,
    "giant_spider": GiantSpider,
    "dark_knight":  DarkKnight,
}

# Enemies available per floor range
FLOOR_ENEMY_POOL: list[tuple[int, int, list[str]]] = [
    (1, 2,  ["slime", "bat", "goblin"]),
    (2, 4,  ["slime", "bat", "goblin", "skeleton", "archer"]),
    (4, 6,  ["goblin", "skeleton", "archer", "bat", "wizard"]),
    (6, 8,  ["skeleton", "archer", "wizard", "ghost", "giant_spider"]),
    (8, 99, ["wizard", "ghost", "giant_spider", "dark_knight"]),
]


def get_enemy_pool(floor: int) -> list[str]:
    for min_f, max_f, pool in FLOOR_ENEMY_POOL:
        if min_f <= floor <= max_f:
            return pool
    return ["slime", "goblin"]


def spawn_enemy(enemy_type: str, x: float, y: float, bus, floor: int) -> BaseEnemy:
    cls = ENEMY_CLASSES.get(enemy_type, Slime)
    return cls(x, y, bus, floor)
