# Eclipse Depths - Player

from __future__ import annotations
import pygame
import math
from src.core.constants import *
from src.utils.timer import Timer
from src.utils.helpers import clamp, normalise
from src.inventory.inventory import Inventory
from src.items.item_data import ItemStats


class PlayerStats:
    """Runtime statistics (kills, gold, floors, etc.)."""
    def __init__(self):
        self.kills      = 0
        self.gold       = 0
        self.floors     = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        self.potions_used = 0
        self.chests_opened = 0
        self.play_time  = 0.0

    def to_dict(self):
        return self.__dict__.copy()

    def from_dict(self, d: dict):
        for k, v in d.items():
            setattr(self, k, v)


class Player(pygame.sprite.Sprite):
    """Player entity with movement, combat, stats, and inventory."""

    SPRITE_COLOUR = (80, 140, 220)

    def __init__(self, x: float, y: float, assets, bus, settings) -> None:
        super().__init__()
        self.assets   = assets
        self.bus      = bus
        self.settings = settings

        # ── Visuals ──────────────────────────────────────────────────────────
        self.facing_angle  = 0.0
        self.is_dodging    = False
        self.is_attacking  = False
        self.image    = pygame.Surface((28, 36), pygame.SRCALPHA)
        self._draw_sprite()
        self.rect     = self.image.get_rect(center=(int(x), int(y)))
        self.hitbox   = pygame.Rect(0, 0, 22, 28)
        self.hitbox.center = self.rect.center

        # ── World position (float precision) ─────────────────────────────────
        self.pos      = pygame.math.Vector2(x, y)
        self.vel      = pygame.math.Vector2(0, 0)
        self.facing   = pygame.math.Vector2(1, 0)

        # ── Base stats ───────────────────────────────────────────────────────
        self.level         = 1
        self.xp            = 0
        self.xp_to_next    = xp_for_level(2)
        self.skill_points  = 0

        self._base_max_hp      = PLAYER_MAX_HP
        self._base_max_mana    = PLAYER_MAX_MANA
        self._base_max_stamina = PLAYER_MAX_STAMINA
        self._base_speed       = PLAYER_SPEED

        # ── Passive upgrades ─────────────────────────────────────────────────
        self.upgrades: dict[str, int] = {
            "max_hp":      0,
            "max_mana":    0,
            "max_stamina": 0,
            "speed":       0,
            "damage":      0,
            "defense":     0,
            "crit":        0,
        }

        # ── Inventory / equipment ─────────────────────────────────────────────
        self.inventory = Inventory()

        self.hp       = float(self.max_hp)
        self.mana     = float(self.max_mana)
        self.stamina  = float(self.max_stamina)

        # ── Timers ───────────────────────────────────────────────────────────
        self._dodge_timer    = Timer(DODGE_DURATION)
        self._dodge_cd       = Timer(DODGE_COOLDOWN)
        self._iframe_timer   = Timer(DODGE_IFRAMES)
        self._attack_timer   = Timer(0.4)
        self._combo_timer    = Timer(COMBO_WINDOW)
        self._hit_flash      = Timer(0.1)

        # ── State flags ──────────────────────────────────────────────────────
        self.is_dodging    = False
        self.is_sprinting  = False
        self.is_attacking  = False
        self.is_dead       = False
        self._dodge_vel    = pygame.math.Vector2(0, 0)
        self.combo_count   = 0
        self.facing_angle  = 0.0

        # ── Combat stats ─────────────────────────────────────────────────────
        self._base_damage    = 10.0
        self._base_crit      = 0.05
        self._base_crit_mult = CRIT_MULTIPLIER
        self._base_defense   = 0.0

        # ── Game stats ───────────────────────────────────────────────────────
        self.stats     = PlayerStats()

    # ── Computed stats ───────────────────────────────────────────────────────
    @property
    def equip_stats(self) -> ItemStats:
        return self.inventory.total_stats()

    @property
    def max_hp(self) -> float:
        return self._base_max_hp + self.upgrades["max_hp"] * 15 + self.equip_stats.hp_bonus

    @property
    def max_mana(self) -> float:
        return self._base_max_mana + self.upgrades["max_mana"] * 10 + self.equip_stats.mana_bonus

    @property
    def max_stamina(self) -> float:
        return self._base_max_stamina + self.upgrades["max_stamina"] * 10

    @property
    def speed(self) -> float:
        return self._base_speed + self.upgrades["speed"] * 8 + self.equip_stats.speed_bonus

    @property
    def attack_damage(self) -> float:
        return self._base_damage + self.upgrades["damage"] * 5 + self.equip_stats.damage

    @property
    def defense(self) -> float:
        return self._base_defense + self.upgrades["defense"] * 3 + self.equip_stats.defense

    @property
    def crit_chance(self) -> float:
        return min(self._base_crit + self.upgrades["crit"] * 0.03 + self.equip_stats.crit_chance, 0.7)

    @property
    def crit_mult(self) -> float:
        return self._base_crit_mult + self.equip_stats.crit_mult

    @property
    def invincible(self) -> bool:
        return not self._iframe_timer.done

    # ── Draw ─────────────────────────────────────────────────────────────────
    def _draw_sprite(self) -> None:
        from src.player.sprites import draw_player
        hit = (hasattr(self, '_hit_flash') and not self._hit_flash.done)
        draw_player(self.image, self.facing_angle,
                    self.is_dodging, self.is_attacking, hit)

    # ── Input handling ───────────────────────────────────────────────────────
    def handle_event(self, event: pygame.Event) -> None:
        kb = self.settings.keybinds
        if event.type == pygame.KEYDOWN:
            if event.key == kb.get("key_dodge", 32):
                self._try_dodge()
            for i in range(4):
                hk = kb.get(f"key_hotbar_{i+1}", 49 + i)
                if event.key == hk:
                    self._use_hotbar(i)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._try_attack()

    # ── Update ───────────────────────────────────────────────────────────────
    def update(self, dt: float, walls: list[pygame.Rect]) -> None:
        if self.is_dead:
            return

        self.stats.play_time += dt

        keys = pygame.key.get_pressed()
        kb   = self.settings.keybinds

        # ── Timers ───────────────────────────────────────────────────────────
        self._dodge_timer.update(dt)
        self._dodge_cd.update(dt)
        self._iframe_timer.update(dt)
        self._attack_timer.update(dt)
        self._combo_timer.update(dt)
        self._hit_flash.update(dt)

        if self._combo_timer.done:
            self.combo_count = 0

        # ── Movement ─────────────────────────────────────────────────────────
        if self.is_dodging:
            self._update_dodge(dt, walls)
        else:
            self._update_movement(dt, keys, kb, walls)

        # ── Regen ────────────────────────────────────────────────────────────
        self.stamina = min(self.max_stamina,
                           self.stamina + PLAYER_STAMINA_REGEN * dt)
        mana_regen = PLAYER_MANA_REGEN + self.equip_stats.mana_regen
        self.mana   = min(self.max_mana, self.mana + mana_regen * dt)

        # ── Sync rects ───────────────────────────────────────────────────────
        self.rect.center     = (int(self.pos.x), int(self.pos.y))
        self.hitbox.center   = self.rect.center

        # ── Facing ───────────────────────────────────────────────────────────
        mx, my = pygame.mouse.get_pos()
        from src.core.camera import Camera
        dx = mx - self.rect.centerx
        dy = my - self.rect.centery
        if dx != 0 or dy != 0:
            self.facing.x, self.facing.y = normalise(dx, dy)
            self.facing_angle = math.degrees(math.atan2(dy, dx))

        # ── Sprite flash ─────────────────────────────────────────────────────
        self._draw_sprite()
        if not self._hit_flash.done:
            flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 160))
            self.image.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _update_movement(self, dt, keys, kb, walls):
        dx = dy = 0
        if keys[kb.get("key_left",  97)]:  dx -= 1
        if keys[kb.get("key_right", 100)]: dx += 1
        if keys[kb.get("key_up",    119)]: dy -= 1
        if keys[kb.get("key_down",  115)]: dy += 1

        if dx != 0 or dy != 0:
            dx, dy = normalise(dx, dy)

        sprinting = (keys[kb.get("key_sprint", 304)] and
                     self.stamina >= SPRINT_STAMINA_COST * dt and
                     (dx != 0 or dy != 0))
        self.is_sprinting = sprinting
        if sprinting:
            self.stamina -= SPRINT_STAMINA_COST * dt

        target_speed = self.speed * (PLAYER_SPRINT_MULT if sprinting else 1.0)

        if dx != 0 or dy != 0:
            self.vel.x += dx * PLAYER_ACCEL * dt
            self.vel.y += dy * PLAYER_ACCEL * dt
            spd = self.vel.length()
            if spd > target_speed:
                self.vel.scale_to_length(target_speed)
        else:
            decel = PLAYER_DECEL * dt
            if self.vel.length() <= decel:
                self.vel.xy = 0, 0
            else:
                self.vel.scale_to_length(self.vel.length() - decel)

        self._move_with_collision(dt, walls)

    def _update_dodge(self, dt, walls):
        if self._dodge_timer.done:
            self.is_dodging = False
            return
        self._move_with_collision(dt, walls, vel_override=self._dodge_vel)

    def _move_with_collision(self, dt, walls, vel_override=None):
        v = vel_override if vel_override is not None else self.vel
        # X
        self.pos.x += v.x * dt
        self.hitbox.centerx = int(self.pos.x)
        for wall in walls:
            if self.hitbox.colliderect(wall):
                if v.x > 0: self.hitbox.right  = wall.left
                else:        self.hitbox.left   = wall.right
                self.pos.x = self.hitbox.centerx
                if vel_override is None: self.vel.x = 0
        # Y
        self.pos.y += v.y * dt
        self.hitbox.centery = int(self.pos.y)
        for wall in walls:
            if self.hitbox.colliderect(wall):
                if v.y > 0: self.hitbox.bottom = wall.top
                else:        self.hitbox.top    = wall.bottom
                self.pos.y = self.hitbox.centery
                if vel_override is None: self.vel.y = 0

    # ── Actions ──────────────────────────────────────────────────────────────
    def _try_dodge(self) -> None:
        if (not self.is_dodging and self._dodge_cd.done and
                self.stamina >= DODGE_STAMINA_COST):
            self.stamina   -= DODGE_STAMINA_COST
            self.is_dodging = True
            self._dodge_timer.start()
            self._iframe_timer.start()
            self._dodge_cd.start()
            if self.vel.length() > 0:
                self._dodge_vel = self.vel.normalize() * DODGE_SPEED
            else:
                self._dodge_vel = pygame.math.Vector2(self.facing) * DODGE_SPEED

    def _try_attack(self) -> None:
        if not self._attack_timer.done:
            return
        spd = self.equip_stats.attack_speed
        self._attack_timer.duration = max(0.15, 0.4 / (1.0 + spd))
        self._attack_timer.start()
        self.is_attacking   = True
        self._combo_timer.start()
        self.combo_count    = min(self.combo_count + 1, 3)
        self.bus.publish("player_attack", {
            "pos":        (self.pos.x, self.pos.y),
            "facing":     (self.facing.x, self.facing.y),
            "damage":     self._roll_damage(),
            "combo":      self.combo_count,
            "knockback":  5 + self.equip_stats.knockback,
        })

    def _roll_damage(self) -> float:
        import random
        dmg = self.attack_damage * random.uniform(0.9, 1.1)
        if random.random() < self.crit_chance:
            dmg *= self.crit_mult
            self.bus.publish("crit_hit", None)
        combo_bonus = {1: 1.0, 2: 1.15, 3: 1.35}.get(self.combo_count, 1.0)
        return round(dmg * combo_bonus, 1)

    def _use_hotbar(self, idx: int) -> None:
        item = self.inventory.use_hotbar(idx)
        if item and item.item_type == "consumable":
            self._apply_consumable(item.effect_id)

    def _apply_consumable(self, effect_id: str) -> None:
        self.stats.potions_used += 1
        if effect_id.startswith("heal_"):
            amt = int(effect_id.split("_")[1])
            self.hp = min(self.max_hp, self.hp + amt)
        elif effect_id.startswith("mana_"):
            amt = int(effect_id.split("_")[1])
            self.mana = min(self.max_mana, self.mana + amt)
        elif effect_id.startswith("stamina_"):
            amt = int(effect_id.split("_")[1])
            self.stamina = min(self.max_stamina, self.stamina + amt)
        elif effect_id.startswith("explode_"):
            dmg = int(effect_id.split("_")[1])
            self.bus.publish("bomb_thrown", {"pos": (self.pos.x, self.pos.y), "damage": dmg})
        self.bus.publish("sfx", {"key": "potion_use"})

    # ── Damage / healing ─────────────────────────────────────────────────────
    def take_damage(self, amount: float, knockback_vec: pygame.math.Vector2 | None = None) -> None:
        if self.invincible or self.is_dead:
            return
        reduced = max(1.0, amount - self.defense * 0.4)
        self.hp -= reduced
        self.stats.damage_taken += reduced
        self._hit_flash.start()
        self.bus.publish("sfx", {"key": "player_hit"})
        self.bus.publish("damage_number", {"pos": (self.pos.x, self.pos.y - 20),
                                            "value": int(reduced), "colour": (255, 80, 80)})
        if knockback_vec:
            self.vel += knockback_vec
        if self.hp <= 0:
            self.hp      = 0
            self.is_dead = True
            self.bus.publish("player_died", None)

    def heal(self, amount: float) -> None:
        self.hp = min(self.max_hp, self.hp + amount)
        life_steal = self.equip_stats.life_steal
        if life_steal > 0:
            bonus = amount * life_steal
            self.hp = min(self.max_hp, self.hp + bonus)

    # ── XP / levelling ───────────────────────────────────────────────────────
    def gain_xp(self, amount: int) -> None:
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp         -= self.xp_to_next
            self.level      += 1
            self.skill_points += 2
            self.xp_to_next  = xp_for_level(self.level + 1)
            # Restore on level up
            self.hp      = self.max_hp
            self.mana    = self.max_mana
            self.bus.publish("level_up", {"level": self.level})
            self.bus.publish("sfx", {"key": "level_up"})

    def add_gold(self, amount: int) -> None:
        self.stats.gold += amount
        self.bus.publish("gold_pickup", {"amount": amount})

    # ── Serialisation ────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "level":       self.level,
            "xp":          self.xp,
            "xp_to_next":  self.xp_to_next,
            "skill_points":self.skill_points,
            "hp":          self.hp,
            "mana":        self.mana,
            "stamina":     self.stamina,
            "upgrades":    self.upgrades,
            "inventory":   self.inventory.to_dict(),
            "stats":       self.stats.to_dict(),
        }

    def from_dict(self, d: dict) -> None:
        self.level        = d.get("level", 1)
        self.xp           = d.get("xp", 0)
        self.xp_to_next   = d.get("xp_to_next", xp_for_level(2))
        self.skill_points = d.get("skill_points", 0)
        self.hp           = d.get("hp", self.max_hp)
        self.mana         = d.get("mana", self.max_mana)
        self.stamina      = d.get("stamina", self.max_stamina)
        self.upgrades.update(d.get("upgrades", {}))
        self.stats.from_dict(d.get("stats", {}))
