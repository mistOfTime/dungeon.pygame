# Eclipse Depths - Base Boss

from __future__ import annotations
import pygame
import math
import random
from src.enemies.base_enemy import BaseEnemy, EnemyState
from src.utils.timer import Timer


class BaseBoss(BaseEnemy):
    """
    Extended boss with multiple phases, patterns, and cinematic entrance.
    """

    PHASES     = 2
    PHASE_THRESHOLDS = [0.5]  # HP ratios that trigger phase change

    def __init__(self, x: float, y: float, bus, floor: int = 1) -> None:
        super().__init__(x, y, bus, floor)
        self.phase          = 1
        self._intro_timer   = Timer(2.0)
        self._intro_timer.start()
        self._is_in_intro   = True
        self._pattern_index = 0
        self._pattern_timer = Timer(0.0)
        bus.publish("boss_spawn", {"name": self.STATS["name"]})
        bus.publish("sfx", {"key": "boss_intro"})

    def update(self, dt, player, walls, dungeon_gen, projectiles):
        # Intro phase – boss stands still
        self._intro_timer.update(dt)
        if self._is_in_intro:
            if self._intro_timer.done:
                self._is_in_intro = False
            return

        # Phase transitions
        for i, threshold in enumerate(self.PHASE_THRESHOLDS):
            if self.hp / self.max_hp <= threshold and self.phase <= i + 1:
                self.phase = i + 2
                self._on_phase_change(self.phase)

        super().update(dt, player, walls, dungeon_gen, projectiles)

    def _on_phase_change(self, new_phase: int) -> None:
        self.bus.publish("boss_phase_change", {"phase": new_phase, "name": self.STATS["name"]})
        self.bus.publish("camera_shake", {"magnitude": 12})
        self.bus.publish("sfx", {"key": "boss_phase"})
        # Speed / damage increase per phase
        self.speed  *= 1.25
        self.damage *= 1.2

    def _die(self):
        self.bus.publish("boss_killed", {
            "pos":  (self.pos.x, self.pos.y),
            "name": self.STATS["name"],
            "floor": self.floor,
        })
        self.bus.publish("sfx", {"key": "boss_death"})
        self.bus.publish("camera_shake", {"magnitude": 20})
        super()._die()
