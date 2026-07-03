# Eclipse Depths - Base Enemy

from __future__ import annotations
import pygame
import math
import random
from enum import Enum, auto
from src.utils.timer import Timer
from src.utils.helpers import normalise, distance, clamp
from src.utils.astar import astar
from src.core.constants import TILE_SIZE, KNOCKBACK_FRICTION


class EnemyState(Enum):
    IDLE    = auto()
    PATROL  = auto()
    CHASE   = auto()
    ATTACK  = auto()
    RETREAT = auto()
    DEAD    = auto()


class BaseEnemy(pygame.sprite.Sprite):
    """
    State-machine enemy base class.
    Subclasses override STATS and optionally _do_attack().
    """

    STATS = {
        "name":         "Enemy",
        "hp":           30,
        "speed":        80,
        "damage":       8,
        "attack_range": 36,
        "chase_range":  220,
        "attack_cd":    1.2,
        "xp":           15,
        "gold_min":     1,
        "gold_max":     5,
        "colour":       (180, 60, 60),
        "size":         (26, 30),
        "knockback":    4.0,
    }

    def __init__(self, x: float, y: float, bus, floor: int = 1) -> None:
        super().__init__()
        self.bus   = bus
        self.floor = floor

        from src.core.constants import enemy_hp_scale, enemy_dmg_scale
        hp_mult  = enemy_hp_scale(floor)
        dmg_mult = enemy_dmg_scale(floor)

        s = self.STATS
        self.max_hp    = s["hp"]  * hp_mult
        self.hp        = self.max_hp
        self.speed     = s["speed"]
        self.damage    = s["damage"] * dmg_mult
        self.xp_reward = s["xp"]
        self.gold_min  = s["gold_min"]
        self.gold_max  = s["gold_max"]
        self.attack_range = s["attack_range"]
        self.chase_range  = s["chase_range"]
        self.knockback    = s["knockback"]

        # Sprite
        w, h = s["size"]
        self.image  = pygame.Surface((w, h), pygame.SRCALPHA)
        self._draw_base_sprite(s["colour"])
        self.rect   = self.image.get_rect(center=(int(x), int(y)))
        self.hitbox = pygame.Rect(0, 0, w - 4, h - 4)
        self.hitbox.center = self.rect.center

        self.pos    = pygame.math.Vector2(x, y)
        self.vel    = pygame.math.Vector2(0, 0)
        self._anim_t = 0.0   # animation time accumulator

        # State machine
        self.state  = EnemyState.IDLE
        self._state_timer  = Timer(random.uniform(1.0, 3.0))
        self._attack_cd    = Timer(s["attack_cd"])
        self._hit_flash    = Timer(0.1)
        self._patrol_dir   = pygame.math.Vector2(random.choice([-1, 1]), 0)
        self._patrol_timer = Timer(random.uniform(1.5, 3.5), auto_reset=True)
        self._patrol_timer.start()
        self._path:        list[tuple[int, int]] = []
        self._path_timer   = Timer(0.5, auto_reset=True)
        self._path_timer.start()

        self.alive  = True
        self._knockback_vel = pygame.math.Vector2(0, 0)

    def _redraw_sprite(self, hit_flash: bool = False) -> None:
        """Called every frame. Subclasses override _draw_sprite_frame."""
        self._draw_sprite_frame(self._anim_t, hit_flash)

    def _draw_sprite_frame(self, t: float, hit: bool) -> None:
        """Override in subclasses for animated sprites."""
        self._draw_base_sprite(self.STATS["colour"])
        if hit:
            flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 180))
            self.image.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_base_sprite(self, colour: tuple) -> None:
        """Subclasses override to use their own draw function."""
        w, h = self.image.get_size()
        self.image.fill((0, 0, 0, 0))
        pygame.draw.ellipse(self.image, colour, (2, h//3, w-4, h*2//3))
        pygame.draw.circle(self.image, colour, (w//2, h//4), h//4 + 2)
        pygame.draw.circle(self.image, (255, 60, 60), (w//2 - 4, h//4 - 1), 2)
        pygame.draw.circle(self.image, (255, 60, 60), (w//2 + 4, h//4 - 1), 2)

    # ── Update ───────────────────────────────────────────────────────────────
    def update(self, dt: float, player, walls: list[pygame.Rect],
               dungeon_gen, projectiles) -> None:
        if not self.alive:
            return

        # Timers
        self._state_timer.update(dt)
        self._attack_cd.update(dt)
        self._hit_flash.update(dt)
        self._patrol_timer.update(dt)
        self._path_timer.update(dt)
        self._anim_t += dt

        # Knockback decay
        if self._knockback_vel.length() > 0:
            friction = KNOCKBACK_FRICTION * dt
            if self._knockback_vel.length() <= friction:
                self._knockback_vel.xy = 0, 0
            else:
                self._knockback_vel.scale_to_length(self._knockback_vel.length() - friction)

        # State transitions
        dist_to_player = distance(self.pos.x, self.pos.y,
                                   player.pos.x, player.pos.y)
        self._update_state(dist_to_player, player)

        # State behaviours
        move = pygame.math.Vector2(0, 0)
        if self.state == EnemyState.IDLE:
            move = self._behaviour_idle(dt)
        elif self.state == EnemyState.PATROL:
            move = self._behaviour_patrol(dt)
        elif self.state == EnemyState.CHASE:
            move = self._behaviour_chase(dt, player, dungeon_gen)
        elif self.state == EnemyState.ATTACK:
            self._behaviour_attack(player, projectiles)
        elif self.state == EnemyState.RETREAT:
            move = self._behaviour_retreat(dt, player)

        total_vel = move + self._knockback_vel
        self._move(dt, total_vel, walls)

        # Flash effect
        self._redraw_sprite(not self._hit_flash.done)

    def _update_state(self, dist: float, player) -> None:
        if self.state == EnemyState.DEAD:
            return
        if player.is_dead:
            self.state = EnemyState.IDLE
            return

        hp_ratio = self.hp / self.max_hp
        if hp_ratio < 0.25 and self.state not in (EnemyState.ATTACK, EnemyState.DEAD):
            self.state = EnemyState.RETREAT
        elif dist <= self.attack_range:
            self.state = EnemyState.ATTACK
        elif dist <= self.chase_range:
            self.state = EnemyState.CHASE
        elif self.state == EnemyState.CHASE:
            self.state = EnemyState.PATROL

    # ── Behaviours ───────────────────────────────────────────────────────────
    def _behaviour_idle(self, dt) -> pygame.math.Vector2:
        if self._state_timer.done:
            self.state = EnemyState.PATROL
            self._state_timer.duration = random.uniform(2.0, 4.0)
            self._state_timer.start()
        return pygame.math.Vector2(0, 0)

    def _behaviour_patrol(self, dt) -> pygame.math.Vector2:
        if self._patrol_timer.done:
            angle = random.uniform(0, math.tau)
            self._patrol_dir = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        return self._patrol_dir * (self.speed * 0.4)

    def _behaviour_chase(self, dt, player, dungeon_gen) -> pygame.math.Vector2:
        # Recompute path periodically
        if self._path_timer.done and dungeon_gen:
            pc = dungeon_gen.world_to_tile(self.pos.x, self.pos.y)
            pp = dungeon_gen.world_to_tile(player.pos.x, player.pos.y)
            self._path = astar(dungeon_gen.is_passable, pc, pp, max_steps=200)
            self._path_timer.start()

        if self._path:
            nc = self._path[0]
            nx, ny = dungeon_gen.tile_to_world(*nc) if dungeon_gen else (nc[0]*TILE_SIZE, nc[1]*TILE_SIZE)
            dx = nx - self.pos.x
            dy = ny - self.pos.y
            dist = math.hypot(dx, dy)
            if dist < TILE_SIZE * 0.6:
                self._path.pop(0)
            if dist > 0:
                return pygame.math.Vector2(dx/dist, dy/dist) * self.speed
        # Fallback: direct
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y
        d  = math.hypot(dx, dy)
        if d > 0:
            return pygame.math.Vector2(dx/d, dy/d) * self.speed
        return pygame.math.Vector2(0, 0)

    def _behaviour_attack(self, player, projectiles) -> None:
        if self._attack_cd.done:
            self._do_attack(player, projectiles)
            self._attack_cd.start()

    def _do_attack(self, player, projectiles) -> None:
        """Default: melee damage."""
        dx = player.pos.x - self.pos.x
        dy = player.pos.y - self.pos.y
        d  = math.hypot(dx, dy)
        kb = pygame.math.Vector2(dx/d, dy/d) * self.knockback if d > 0 else pygame.math.Vector2(0, 0)
        player.take_damage(self.damage, kb)
        self.bus.publish("sfx", {"key": "enemy_attack"})

    def _behaviour_retreat(self, dt, player) -> pygame.math.Vector2:
        dx = self.pos.x - player.pos.x
        dy = self.pos.y - player.pos.y
        d  = math.hypot(dx, dy)
        if d == 0:
            return pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)) * self.speed
        return pygame.math.Vector2(dx/d, dy/d) * (self.speed * 0.7)

    # ── Movement ─────────────────────────────────────────────────────────────
    def _move(self, dt: float, vel: pygame.math.Vector2, walls: list[pygame.Rect]) -> None:
        self.pos.x += vel.x * dt
        self.hitbox.centerx = int(self.pos.x)
        for wall in walls:
            if self.hitbox.colliderect(wall):
                if vel.x > 0: self.hitbox.right = wall.left
                else:          self.hitbox.left  = wall.right
                self.pos.x = self.hitbox.centerx
                self._knockback_vel.x = 0

        self.pos.y += vel.y * dt
        self.hitbox.centery = int(self.pos.y)
        for wall in walls:
            if self.hitbox.colliderect(wall):
                if vel.y > 0: self.hitbox.bottom = wall.top
                else:          self.hitbox.top    = wall.bottom
                self.pos.y = self.hitbox.centery
                self._knockback_vel.y = 0

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.hitbox.center = self.rect.center

    # ── Damage ───────────────────────────────────────────────────────────────
    def take_damage(self, amount: float,
                    knockback_vec: pygame.math.Vector2 | None = None) -> None:
        if not self.alive:
            return
        self.hp -= amount
        self._hit_flash.start()
        self.bus.publish("damage_number", {
            "pos":    (self.pos.x, self.pos.y - 20),
            "value":  int(amount),
            "colour": (255, 220, 80),
        })
        if knockback_vec:
            self._knockback_vel += knockback_vec
        if self.hp <= 0:
            self._die()

    def _die(self) -> None:
        self.alive = False
        self.state = EnemyState.DEAD
        self.bus.publish("enemy_killed", {
            "pos":  (self.pos.x, self.pos.y),
            "xp":   self.xp_reward,
            "gold": random.randint(self.gold_min, self.gold_max),
            "name": self.STATS["name"],
        })
        self.bus.publish("sfx", {"key": "enemy_death"})
        self.kill()
