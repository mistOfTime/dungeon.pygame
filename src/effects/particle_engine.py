# Eclipse Depths - Particle Engine

from __future__ import annotations
import pygame
import random
import math
from src.core.constants import MAX_PARTICLES
from src.utils.helpers import clamp


class Particle:
    __slots__ = ("x","y","vx","vy","life","max_life","colour","radius","gravity","fade")

    def __init__(self, x, y, vx, vy, life, colour, radius, gravity=0.0, fade=True):
        self.x       = float(x)
        self.y       = float(y)
        self.vx      = float(vx)
        self.vy      = float(vy)
        self.life    = float(life)
        self.max_life= float(life)
        self.colour  = colour
        self.radius  = float(radius)
        self.gravity = float(gravity)
        self.fade    = fade

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.vx   *= 0.96
        self.vy   *= 0.96
        self.vy   += self.gravity * dt
        self.x    += self.vx * dt
        self.y    += self.vy * dt
        return self.life > 0

    def draw(self, surface: pygame.Surface, cam_ox: float, cam_oy: float) -> None:
        sx = int(self.x - cam_ox)
        sy = int(self.y - cam_oy)
        if self.fade:
            alpha = int(clamp(self.life / self.max_life, 0, 1) * 220)
        else:
            alpha = 200
        r = max(1, int(self.radius * clamp(self.life / self.max_life, 0.1, 1)))
        col = (*self.colour[:3], alpha)
        surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, col, (r + 1, r + 1), r)
        surface.blit(surf, (sx - r - 1, sy - r - 1))


class ParticleEngine:
    """Custom particle system with pooling."""

    def __init__(self) -> None:
        self._particles: list[Particle] = []

    def emit(self, x: float, y: float, count: int,
             colour: tuple = (255, 200, 50),
             speed_min: float = 30, speed_max: float = 120,
             life_min: float = 0.3, life_max: float = 0.8,
             radius_min: float = 2, radius_max: float = 5,
             gravity: float = 60, angle_min: float = 0,
             angle_max: float = math.tau, fade: bool = True) -> None:
        room = MAX_PARTICLES - len(self._particles)
        count = min(count, room)
        for _ in range(count):
            angle = random.uniform(angle_min, angle_max)
            speed = random.uniform(speed_min, speed_max)
            life  = random.uniform(life_min, life_max)
            r     = random.uniform(radius_min, radius_max)
            col   = (
                clamp(colour[0] + random.randint(-20, 20), 0, 255),
                clamp(colour[1] + random.randint(-20, 20), 0, 255),
                clamp(colour[2] + random.randint(-20, 20), 0, 255),
            )
            self._particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life, col, r, gravity, fade,
            ))

    def emit_burst(self, pos: tuple, colour: tuple, count: int = 16) -> None:
        self.emit(pos[0], pos[1], count, colour,
                  speed_min=40, speed_max=140,
                  life_min=0.3, life_max=0.7,
                  radius_min=2, radius_max=5, gravity=80)

    def emit_trail(self, x: float, y: float, colour: tuple, count: int = 3) -> None:
        self.emit(x, y, count, colour,
                  speed_min=10, speed_max=50,
                  life_min=0.1, life_max=0.3,
                  radius_min=1, radius_max=3, gravity=0)

    def emit_blood(self, x: float, y: float, count: int = 8) -> None:
        self.emit(x, y, count, (200, 40, 40),
                  speed_min=30, speed_max=100,
                  life_min=0.3, life_max=0.6,
                  radius_min=2, radius_max=4,
                  angle_min=0, angle_max=math.tau, gravity=120)

    def emit_heal(self, x: float, y: float) -> None:
        self.emit(x, y, 12, (80, 230, 100),
                  speed_min=20, speed_max=60,
                  life_min=0.5, life_max=1.2,
                  radius_min=2, radius_max=4,
                  angle_min=-math.pi, angle_max=0, gravity=-40)

    def emit_levelup(self, x: float, y: float) -> None:
        self.emit(x, y, 30, (255, 215, 0),
                  speed_min=50, speed_max=200,
                  life_min=0.5, life_max=1.5,
                  radius_min=3, radius_max=6,
                  angle_min=0, angle_max=math.tau, gravity=-20)

    def update(self, dt: float) -> None:
        self._particles = [p for p in self._particles if p.update(dt)]

    def draw(self, surface: pygame.Surface, camera) -> None:
        ox, oy = camera.offset
        for p in self._particles:
            p.draw(surface, ox, oy)

    def clear(self) -> None:
        self._particles.clear()
