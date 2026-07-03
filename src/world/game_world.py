# Eclipse Depths - Game World (orchestrates everything during gameplay)

from __future__ import annotations
import pygame
import random
from src.core.constants import *
from src.core.camera import Camera
from src.dungeon.dungeon_generator import DungeonGenerator, Tile
from src.dungeon.dungeon_renderer import DungeonRenderer
from src.player.player import Player
from src.enemies.enemy_types import spawn_enemy, get_enemy_pool
from src.bosses.boss_types import get_boss_for_floor
from src.combat.projectile import Projectile
from src.combat.melee_attack import MeleeAttack
from src.effects.particle_engine import ParticleEngine
from src.effects.damage_numbers import DamageNumberManager
from src.spells.spell_manager import SpellManager
from src.quests.quest_manager import QuestManager
from src.items.item_data import generate_weapon, generate_armor, generate_accessory, make_consumable
from src.world.loot_drop import LootDrop
from src.world.chest import Chest
from src.world.npc import NPC
from src.world.trap import Trap
from src.utils.helpers import distance


class GameWorld:
    """The active game session _ one run from start to death or exit."""

    def __init__(self, screen: pygame.Surface, assets, audio, bus,
                 settings, save_data: dict | None, slot: int) -> None:
        self.screen       = screen
        self.assets       = assets
        self.audio        = audio
        self.bus          = bus
        self.settings     = settings
        self.save_slot    = slot
        self.current_floor = 1

        # Camera
        self.camera = Camera(screen.get_width(), screen.get_height())

        # Sprite groups
        self.enemy_group      = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.melee_group      = pygame.sprite.Group()
        self.loot_group       = pygame.sprite.Group()
        self.chest_group      = pygame.sprite.Group()
        self.npc_group        = pygame.sprite.Group()
        self.trap_group       = pygame.sprite.Group()

        # Sub-systems
        self.particles    = ParticleEngine()
        self.dmg_numbers  = DamageNumberManager(assets)
        self.quest_manager= QuestManager(bus)

        # Player
        px, py = 300, 300
        self.player = Player(px, py, assets, bus, settings)
        if save_data:
            self.player.from_dict(save_data.get("player", {}))
            self.current_floor = save_data.get("floor", 1)
            self.quest_manager  # TODO: restore quest state

        self.spell_manager = SpellManager(bus)

        # Generate dungeon
        self._gen_dungeon(self.current_floor)

        # Register bus events
        self._register_events()

    # __ Bus wiring ___________________________________________________________
    def _register_events(self) -> None:
        b = self.bus
        b.subscribe("player_attack",   self._on_player_attack)
        b.subscribe("enemy_killed",    self._on_enemy_killed)
        b.subscribe("damage_number",   self._on_damage_number)
        b.subscribe("particle_burst",  self._on_particle_burst)
        b.subscribe("camera_shake",    self._on_camera_shake)
        b.subscribe("crit_hit",        self._on_crit_hit)
        b.subscribe("level_up",        self._on_level_up)
        b.subscribe("notification",    self._on_notification)
        b.subscribe("sfx",             self._on_sfx)
        b.subscribe("boss_killed",     self._on_boss_killed)
        b.subscribe("quest_complete",  self._on_quest_complete)

        # __ Descent confirmation __________________________________________________
        self._show_descend_prompt = False
        self._descend_prompt_timer = 0.0

    # __ Dungeon generation ___________________________________________________
    def _gen_dungeon(self, floor: int) -> None:
        self.dungeon   = DungeonGenerator(floor).generate()
        self.renderer  = DungeonRenderer(self.dungeon, self.assets)

        # Place player safely at spawn room center
        if self.dungeon.spawn_room:
            px, py = self.dungeon.random_floor_pos(self.dungeon.spawn_room)
        else:
            px, py = self.dungeon.random_floor_pos()

        # Clamp to tile grid bounds
        px = max(TILE_SIZE * 2, min(px, (self.dungeon.grid_w - 2) * TILE_SIZE))
        py = max(TILE_SIZE * 2, min(py, (self.dungeon.grid_h - 2) * TILE_SIZE))

        self.player.pos.xy = px, py
        self.player.rect.center = (int(px), int(py))
        self.player.hitbox.center = (int(px), int(py))
        self.player.vel.xy = 0, 0
        self.player.is_dodging = False

        # Snap camera instantly to new position
        self.camera.x = px - self.screen.get_width() / 2
        self.camera.y = py - self.screen.get_height() / 2
        self.camera._target_x = self.camera.x
        self.camera._target_y = self.camera.y

        # Clear entities
        for g in (self.enemy_group, self.projectile_group, self.melee_group,
                  self.loot_group, self.chest_group, self.npc_group, self.trap_group):
            g.empty()
        self.particles.clear()

        self._populate_rooms(floor)
        self._show_descend_prompt = False
        self.bus.publish("floor_reached", {"floor": floor})
        self.player.stats.floors = floor

    def _populate_rooms(self, floor: int) -> None:
        pool = get_enemy_pool(floor)
        for room in self.dungeon.rooms:
            rt = room.room_type
            if rt == "spawn":
                continue

            if rt in ("normal", "elite"):
                count = random.randint(2, 5) if rt == "normal" else random.randint(4, 7)
                for _ in range(count):
                    ex, ey = self.dungeon.random_floor_pos(room)
                    etype  = random.choice(pool)
                    enemy  = spawn_enemy(etype, ex, ey, self.bus, floor)
                    self.enemy_group.add(enemy)

            elif rt == "boss":
                bx, by = room.center_px
                BossClass = get_boss_for_floor(floor)
                boss = BossClass(bx, by, self.bus, floor)
                self.enemy_group.add(boss)

            elif rt == "treasure":
                for _ in range(random.randint(1, 3)):
                    cx, cy = self.dungeon.random_floor_pos(room)
                    chest  = Chest(cx, cy, self.assets, self.bus, floor)
                    self.chest_group.add(chest)

            elif rt == "shop":
                npcs = [
                    NPC(room.center_px[0] - 40, room.center_px[1], "Merchant", self.assets, self.bus, floor),
                    NPC(room.center_px[0] + 40, room.center_px[1], "Blacksmith", self.assets, self.bus, floor),
                ]
                for n in npcs:
                    self.npc_group.add(n)

            elif rt == "puzzle":
                for _ in range(random.randint(2, 4)):
                    tx, ty = self.dungeon.random_floor_pos(room)
                    trap = Trap(tx, ty, self.assets, self.bus)
                    self.trap_group.add(trap)

            # Random chest in any room
            if rt == "normal" and random.random() < 0.3:
                cx, cy = self.dungeon.random_floor_pos(room)
                chest  = Chest(cx, cy, self.assets, self.bus, floor, rare=False)
                self.chest_group.add(chest)

    # __ Input ________________________________________________________________
    def handle_event(self, event: pygame.Event) -> None:
        self.player.handle_event(event)
        kb = self.settings.keybinds

        if event.type == pygame.KEYDOWN:
            if event.key == kb.get("key_pause", 27):
                self.bus.publish("pause")
            elif event.key == kb.get("key_inventory", 105):
                self.bus.publish("open_inventory")
            elif event.key == kb.get("key_map", 109):
                self.bus.publish("open_map")
            elif event.key == kb.get("key_quest_log", 113):
                self.bus.publish("open_quest_log")
            elif event.key == pygame.K_e:
                self._try_interact()
            # Spell keys Q/E/R/F
            elif event.key == pygame.K_z:
                self.spell_manager.cast(0, self.player, self.projectile_group)
            elif event.key == pygame.K_x:
                self.spell_manager.cast(1, self.player, self.projectile_group)
            elif event.key == pygame.K_c:
                self.spell_manager.cast(2, self.player, self.projectile_group)
            elif event.key == pygame.K_v:
                self.spell_manager.cast(3, self.player, self.projectile_group)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            # Right click = ranged attack if bow equipped
            self._fire_ranged()

    # __ Update _______________________________________________________________
    def update(self, dt: float) -> None:
        # Player
        self.player.update(dt, self.dungeon.walls)

        # Camera
        self.camera.follow(self.player)
        self.camera.update(dt)

        # Fog of war
        col, row = self.dungeon.world_to_tile(self.player.pos.x, self.player.pos.y)
        self.renderer.update_visibility(col, row, radius=9)

        # Mark room visited
        for room in self.dungeon.rooms:
            if room.rect.collidepoint(self.player.pos.x, self.player.pos.y):
                room.visited = True

        # Spell manager
        self.spell_manager.update(dt, self.player)

        # Enemies
        for enemy in list(self.enemy_group):
            enemy.update(dt, self.player, self.dungeon.walls,
                         self.dungeon, self.projectile_group)

        # Projectiles
        self.projectile_group.update(dt, self.dungeon.walls)

        # Melee hitboxes
        self.melee_group.update(dt, self.dungeon.walls)
        self._check_melee_hits()

        # Loot & chests
        self.loot_group.update(dt)
        self.chest_group.update(dt)
        self.npc_group.update(dt)
        self.trap_group.update(dt, self.player)

        # Particle & damage numbers
        self.particles.update(dt)
        self.dmg_numbers.update(dt)

        # Player pickup radius
        self._check_loot_pickup()

        # Projectile hits
        self._check_projectile_hits()

        # Player trail
        self.particles.emit_trail(self.player.pos.x, self.player.pos.y,
                                   (100, 160, 240), count=1)

        # Descent prompt timer
        self._descend_prompt_timer = max(0.0, self._descend_prompt_timer - dt)
        self._show_descend_prompt = self._near_exit()

    def _check_melee_hits(self) -> None:
        for attack in self.melee_group:
            if not attack.alive:
                continue
            if attack.owner == "player":
                for enemy in list(self.enemy_group):
                    if attack.rect.colliderect(enemy.hitbox):
                        kb = attack.knockback_vec()
                        enemy.take_damage(attack.damage, kb)
                        self.particles.emit_blood(enemy.pos.x, enemy.pos.y, 6)
                        if not attack.piercing if hasattr(attack, "piercing") else True:
                            break

    def _check_projectile_hits(self) -> None:
        for proj in list(self.projectile_group):
            if not proj.alive:
                continue
            if proj.owner == "player":
                for enemy in list(self.enemy_group):
                    if proj.rect.colliderect(enemy.hitbox):
                        enemy.take_damage(proj.damage, proj.knockback_vec())
                        self.particles.emit_burst(
                            (proj.pos.x, proj.pos.y), proj.colour, 8)
                        if not proj.piercing:
                            proj.alive = False
                            proj.kill()
                        break
            elif proj.owner == "enemy":
                if proj.rect.colliderect(self.player.hitbox):
                    if self.spell_manager.is_shielded():
                        self.particles.emit_burst(
                            (proj.pos.x, proj.pos.y), (100, 150, 255), 10)
                    else:
                        self.player.take_damage(proj.damage, proj.knockback_vec())
                        self.particles.emit_blood(self.player.pos.x, self.player.pos.y, 4)
                    proj.alive = False
                    proj.kill()

    def _check_loot_pickup(self) -> None:
        for loot in list(self.loot_group):
            if distance(self.player.pos.x, self.player.pos.y,
                        loot.rect.centerx, loot.rect.centery) < 30:
                if loot.item_type == "gold":
                    self.player.add_gold(loot.value)
                    self.particles.emit_burst((loot.rect.centerx, loot.rect.centery),
                                               (255, 215, 0), 8)
                else:
                    added = self.player.inventory.add_item(loot.item)
                    if added:
                        self.bus.publish("notification", {
                            "text":   f"Picked up: {loot.item.name}",
                            "colour": loot.item.colour,
                        })
                loot.kill()

    def _check_exit(self) -> None:
        if self.dungeon.exit_room:
            ex, ey = self.dungeon.exit_room.center_px
            if distance(self.player.pos.x, self.player.pos.y, ex, ey) < 40:
                self.bus.publish("notification", {"text": "Press E to descend...", "colour": (100, 255, 180)})

    def _near_exit(self) -> bool:
        if not self.dungeon.exit_room:
            return False
        ex, ey = self.dungeon.exit_room.center_px
        return distance(self.player.pos.x, self.player.pos.y, ex, ey) < 50

    def _try_interact(self) -> None:
        # NPCs
        for npc in self.npc_group:
            if distance(self.player.pos.x, self.player.pos.y,
                        npc.rect.centerx, npc.rect.centery) < 60:
                npc.interact(self.player)
                return
        # Chests
        for chest in self.chest_group:
            if not chest.opened and distance(
                    self.player.pos.x, self.player.pos.y,
                    chest.rect.centerx, chest.rect.centery) < 50:
                chest.open(self.player, self.loot_group)
                self.player.stats.chests_opened += 1
                self.bus.publish("chest_opened", None)
                return
        # Exit portal _ only trigger when close enough AND pressing E
        if self._near_exit():
            self.next_floor()
            return

    def _fire_ranged(self) -> None:
        """Fire ranged projectile based on equipped weapon."""
        equip = self.player.inventory.equipment.get("weapon")
        if not equip or equip.subtype not in ("bow", "crossbow", "staff"):
            return
        mx, my = self.camera.world_pos(*pygame.mouse.get_pos())
        dx = mx - self.player.pos.x
        dy = my - self.player.pos.y
        import math
        d = math.hypot(dx, dy)
        if d == 0: return
        col = (100, 200, 255) if equip.subtype == "staff" else (220, 200, 80)
        proj = Projectile(
            self.player.pos.x, self.player.pos.y, dx, dy,
            speed=300, damage=self.player.attack_damage * 0.85,
            owner="player", colour=col, radius=5, lifetime=2.5,
            knockback=self.player.equip_stats.knockback,
        )
        self.projectile_group.add(proj)
        self.bus.publish("sfx", {"key": "arrow_shoot"})

    def next_floor(self) -> None:
        self.current_floor += 1
        self._gen_dungeon(self.current_floor)
        self.audio.play_music("dungeon")
        self.bus.publish("notification", {
            "text":   f"Floor {self.current_floor}",
            "colour": (255, 215, 0),
        })

    # __ Draw _________________________________________________________________
    def draw(self) -> None:
        self.screen.fill(DARK_GREY)

        # Dungeon tiles
        self.renderer.draw(self.screen, self.camera)

        # Shadows (simple)
        self._draw_shadows()

        # World objects
        self._draw_group(self.trap_group)
        self._draw_group(self.loot_group)
        self._draw_group(self.chest_group)
        self._draw_group(self.npc_group)
        self._draw_group(self.enemy_group)
        self._draw_group(self.melee_group)
        self._draw_group(self.projectile_group)

        # Player
        self.screen.blit(self.player.image,
                         self.camera.apply(self.player.rect))

        # Particles & numbers
        self.particles.draw(self.screen, self.camera)
        self.dmg_numbers.draw(self.screen, self.camera)

        # Exit portal glow
        self._draw_exit_portal()

        # Descent prompt
        if self._show_descend_prompt:
            self._draw_descend_prompt()

    def _draw_group(self, group: pygame.sprite.Group) -> None:
        for sprite in group:
            self.screen.blit(sprite.image, self.camera.apply(sprite.rect))

    def _draw_shadows(self) -> None:
        entities = list(self.enemy_group) + [self.player]
        for e in entities:
            sr = self.camera.apply(e.rect)
            shadow = pygame.Surface((sr.width, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
            self.screen.blit(shadow, (sr.x, sr.bottom - 6))

    def _draw_exit_portal(self) -> None:
        if not self.dungeon.exit_room:
            return
        ex, ey = self.dungeon.exit_room.center_px
        sr     = self.camera.apply_pos(ex, ey)
        t      = pygame.time.get_ticks() * 0.003
        import math
        r      = int(18 + math.sin(t) * 4)
        surf   = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (80, 220, 140, 160), (r+2, r+2), r)
        pygame.draw.circle(surf, (180, 255, 200, 80),  (r+2, r+2), r+3, 3)
        self.screen.blit(surf, (sr[0] - r - 2, sr[1] - r - 2))

    def _draw_descend_prompt(self) -> None:
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        font = self.assets.font(18, bold=True)
        text = font.render("[ E ]  Descend to next floor", True, (100, 255, 180))
        import math
        alpha = int(180 + math.sin(pygame.time.get_ticks() * 0.004) * 60)
        text.set_alpha(alpha)
        bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        pygame.draw.rect(bg, (60, 200, 120, 100), bg.get_rect(), 1, border_radius=6)
        bx = sw // 2 - bg.get_width() // 2
        by = sh // 2 + 80
        self.screen.blit(bg,   (bx, by))
        self.screen.blit(text, (bx + 10, by + 5))

    # __ Bus event handlers ___________________________________________________
    def _on_player_attack(self, data: dict) -> None:
        px, py   = data["pos"]
        fx, fy   = data["facing"]
        dmg      = data["damage"]
        combo    = data["combo"]
        kb_mag   = data["knockback"]
        # Create melee hitbox
        reach    = 40 + combo * 4
        ma       = MeleeAttack(px, py, fx, fy, dmg,
                               reach=reach, lifetime=0.12,
                               owner="player", knockback=kb_mag, combo=combo)
        self.melee_group.add(ma)
        self.particles.emit(px + fx * reach, py + fy * reach, 8,
                            (255, 220, 80), speed_min=30, speed_max=80,
                            life_min=0.1, life_max=0.25,
                            angle_min=0, angle_max=3.14, gravity=0)
        self.bus.publish("sfx", {"key": "sword_swing"})

    def _on_enemy_killed(self, data: dict) -> None:
        self.player.gain_xp(data["xp"])
        self.player.add_gold(data["gold"])
        self.player.stats.kills += 1
        # Drop loot
        drop_chance = 0.45
        if random.random() < drop_chance:
            pos = data["pos"]
            import random as rnd
            roll = rnd.random()
            if roll < 0.5:
                drop = LootDrop.gold(pos[0], pos[1], random.randint(1, 8))
            elif roll < 0.75:
                drop = LootDrop.weapon(pos[0], pos[1], self.current_floor)
            elif roll < 0.9:
                drop = LootDrop.armor(pos[0], pos[1], self.current_floor)
            else:
                drop = LootDrop.consumable(pos[0], pos[1])
            self.loot_group.add(drop)
        self.particles.emit_burst(data["pos"], (220, 80, 60), 12)

    def _on_damage_number(self, data: dict) -> None:
        pos   = data["pos"]
        value = data["value"]
        col   = data.get("colour", (255, 220, 80))
        is_crit = data.get("crit", False)
        self.dmg_numbers.add(pos[0], pos[1], value, col, is_crit)

    def _on_particle_burst(self, data: dict) -> None:
        self.particles.emit_burst(data["pos"], data["colour"], data.get("count", 16))

    def _on_camera_shake(self, data: dict) -> None:
        self.camera.shake(data.get("magnitude", 8))

    def _on_crit_hit(self, data) -> None:
        self.camera.shake(3)

    def _on_level_up(self, data: dict) -> None:
        self.particles.emit_levelup(self.player.pos.x, self.player.pos.y)
        self.bus.publish("notification", {
            "text":   f"Level Up! You are now level {data['level']}",
            "colour": (255, 215, 0),
        })

    def _on_notification(self, data: dict) -> None:
        pass  # HUD handles notifications

    def _on_sfx(self, data: dict) -> None:
        self.audio.play_sfx(data.get("key", ""))

    def _on_boss_killed(self, data: dict) -> None:
        self.audio.play_music("victory")
        self.bus.publish("notification", {
            "text":   f"Boss Defeated: {data['name']}!",
            "colour": (255, 100, 50),
        })

    def _on_quest_complete(self, data: dict) -> None:
        if data:
            self.player.add_gold(data.get("reward_gold", 0))
            self.player.gain_xp(data.get("reward_xp", 0))
