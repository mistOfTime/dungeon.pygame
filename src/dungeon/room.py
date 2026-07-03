# Eclipse Depths - Room definition

from __future__ import annotations
import pygame
from dataclasses import dataclass, field
from src.core.constants import TILE_SIZE


ROOM_TYPES = [
    "spawn", "normal", "treasure", "elite", "puzzle",
    "secret", "shop", "boss", "exit",
]


@dataclass
class Room:
    col:     int
    row:     int
    w:       int          # width in tiles
    h:       int          # height in tiles
    room_type: str = "normal"
    connected: list["Room"] = field(default_factory=list)
    visited:   bool = False
    cleared:   bool = False
    # Pixel rect of the floor area
    rect:      pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(self.col * TILE_SIZE, self.row * TILE_SIZE,
                                self.w * TILE_SIZE, self.h * TILE_SIZE)

    @property
    def center_px(self) -> tuple[int, int]:
        return self.rect.centerx, self.rect.centery

    @property
    def center_tile(self) -> tuple[int, int]:
        return self.col + self.w // 2, self.row + self.h // 2

    def world_rect(self) -> pygame.Rect:
        return self.rect

    def __hash__(self):
        return hash((self.col, self.row))

    def __eq__(self, other):
        return isinstance(other, Room) and self.col == other.col and self.row == other.row
