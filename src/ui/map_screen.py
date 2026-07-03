# Eclipse Depths - Map Screen

from __future__ import annotations
import pygame
from src.core.constants import *


class MapScreen:
    def __init__(self, screen: pygame.Surface, assets, bus) -> None:
        self.screen = screen
        self.assets = assets
        self.bus    = bus
        self._world = None
        self._font  = assets.font(13)
        self._font_title = assets.font(22, bold=True)

    def set_world(self, world) -> None:
        self._world = world

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_m):
            self.bus.publish("close_map")

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        if not self._world:
            return
        sw, sh = self.screen.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title = self._font_title.render("DUNGEON MAP", True, (180, 160, 240))
        self.screen.blit(title, (sw//2 - title.get_width()//2, 20))

        gen   = self._world.dungeon
        scale = min((sw - 80) / (gen.grid_w * TILE_SIZE),
                    (sh - 100) / (gen.grid_h * TILE_SIZE)) * TILE_SIZE * 0.85
        ox    = sw // 2 - int(gen.grid_w * scale / 2)
        oy    = 70

        ROOM_COLOURS = {
            "spawn":    (80, 120, 200),
            "boss":     (200, 50, 50),
            "treasure": (200, 170, 50),
            "shop":     (80, 200, 120),
            "exit":     (80, 220, 140),
            "elite":    (180, 80, 80),
            "puzzle":   (200, 140, 60),
            "secret":   (140, 80, 200),
            "normal":   (55, 50, 70),
        }

        for room in gen.rooms:
            rx = ox + int(room.col * scale)
            ry = oy + int(room.row * scale)
            rw = max(4, int(room.w * scale))
            rh = max(4, int(room.h * scale))
            col = ROOM_COLOURS.get(room.room_type, (55, 50, 70))
            if room.visited:
                pygame.draw.rect(self.screen, col, (rx, ry, rw, rh), border_radius=3)
            else:
                pygame.draw.rect(self.screen, (25, 22, 35), (rx, ry, rw, rh), border_radius=3)
            pygame.draw.rect(self.screen, (80, 70, 110), (rx, ry, rw, rh), 1, border_radius=3)

            if room.visited:
                lbl = self._font.render(room.room_type[:4].capitalize(), True, (200, 190, 220))
                self.screen.blit(lbl, (rx + 2, ry + 2))

        # Player position
        p  = self._world.player
        px = ox + int(p.pos.x / TILE_SIZE * scale)
        py = oy + int(p.pos.y / TILE_SIZE * scale)
        pygame.draw.circle(self.screen, (100, 200, 255), (px, py), 5)
        pygame.draw.circle(self.screen, WHITE, (px, py), 5, 1)

        hint = self._font.render("M / Esc – Close Map", True, MID_GREY)
        self.screen.blit(hint, (sw//2 - hint.get_width()//2, sh - 24))
