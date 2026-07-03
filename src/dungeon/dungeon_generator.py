# Eclipse Depths - Procedural Dungeon Generator

from __future__ import annotations
import random
import pygame
from src.core.constants import *
from src.dungeon.room import Room
from src.utils.helpers import weighted_choice


class Tile:
    FLOOR   = 0
    WALL    = 1
    DOOR    = 2
    VOID    = 3
    CHEST   = 4
    TRAP    = 5
    BREAKABLE = 6
    EXIT    = 7
    SPAWN   = 8


class DungeonGenerator:
    """BSP-inspired dungeon generator that produces rooms, corridors, and a tile grid."""

    def __init__(self, floor: int = 1) -> None:
        self.floor   = floor
        self.rooms:  list[Room] = []
        self.tiles:  list[list[int]] = []
        self.grid_w  = 0
        self.grid_h  = 0
        self.walls:  list[pygame.Rect] = []
        self.spawn_room:  Room | None = None
        self.boss_room:   Room | None = None
        self.exit_room:   Room | None = None

    def generate(self) -> "DungeonGenerator":
        target_rooms = random.randint(DUNGEON_MIN_ROOMS, DUNGEON_MAX_ROOMS)
        self._place_rooms(target_rooms)
        self._assign_types()
        self._build_tile_grid()
        self._carve_corridors()
        self._build_walls()
        return self

    # ── Room placement ────────────────────────────────────────────────────────
    def _place_rooms(self, target: int) -> None:
        grid_cols = 100
        grid_rows = 80
        self.grid_w = grid_cols
        self.grid_h = grid_rows
        attempts  = 0

        while len(self.rooms) < target and attempts < target * 60:
            attempts += 1
            w = random.randint(ROOM_MIN_W, ROOM_MAX_W)
            h = random.randint(ROOM_MIN_H, ROOM_MAX_H)
            c = random.randint(1, grid_cols - w - 2)
            r = random.randint(1, grid_rows - h - 2)

            # Check overlap with 2-tile padding
            new_rect = pygame.Rect(c - 2, r - 2, w + 4, h + 4)
            overlap  = False
            for existing in self.rooms:
                er = pygame.Rect(existing.col - 2, existing.row - 2,
                                 existing.w + 4, existing.h + 4)
                if new_rect.colliderect(er):
                    overlap = True
                    break
            if overlap:
                continue

            room = Room(col=c, row=r, w=w, h=h)
            self.rooms.append(room)

        if not self.rooms:
            # Fallback: single room
            self.rooms.append(Room(col=5, row=5, w=14, h=12))

        # Connect rooms via MST (nearest neighbour)
        self._connect_rooms_mst()

    def _connect_rooms_mst(self) -> None:
        if len(self.rooms) < 2:
            return
        connected: list[Room] = [self.rooms[0]]
        remaining:  list[Room] = list(self.rooms[1:])
        while remaining:
            best_dist = float("inf")
            best_r    = None
            best_c    = None
            for r in connected:
                for c in remaining:
                    cx, cy = r.center_tile
                    dx, dy = c.center_tile
                    d = abs(cx - dx) + abs(cy - dy)
                    if d < best_dist:
                        best_dist = d
                        best_r    = r
                        best_c    = c
            if best_r and best_c:
                best_r.connected.append(best_c)
                best_c.connected.append(best_r)
                connected.append(best_c)
                remaining.remove(best_c)

        # Add ~30% extra connections for loops
        extras = max(1, len(self.rooms) // 3)
        for _ in range(extras):
            a, b = random.sample(self.rooms, 2)
            if b not in a.connected:
                a.connected.append(b)
                b.connected.append(a)

    # ── Type assignment ───────────────────────────────────────────────────────
    def _assign_types(self) -> None:
        if not self.rooms:
            return
        self.rooms[0].room_type = "spawn"
        self.spawn_room = self.rooms[0]

        remaining = self.rooms[1:]
        random.shuffle(remaining)

        type_pool = (
            ["boss"] +
            ["treasure"] * 2 +
            ["elite"] * max(1, len(remaining) // 4) +
            ["shop"] +
            ["secret"] +
            ["puzzle"] +
            ["exit"]
        )
        assigned: set = set()
        for i, t in enumerate(type_pool):
            if i < len(remaining):
                remaining[i].room_type = t
                assigned.add(i)

        for i, r in enumerate(remaining):
            if i not in assigned:
                r.room_type = "normal"

        self.boss_room = next((r for r in self.rooms if r.room_type == "boss"), self.rooms[-1])
        self.exit_room = next((r for r in self.rooms if r.room_type == "exit"), self.rooms[-2] if len(self.rooms) > 1 else self.rooms[0])

    # ── Tile grid ─────────────────────────────────────────────────────────────
    def _build_tile_grid(self) -> None:
        self.tiles = [[Tile.VOID] * self.grid_w for _ in range(self.grid_h)]
        for room in self.rooms:
            for dr in range(room.h):
                for dc in range(room.w):
                    tr = room.row + dr
                    tc = room.col + dc
                    if 0 <= tr < self.grid_h and 0 <= tc < self.grid_w:
                        if dr == 0 or dr == room.h - 1 or dc == 0 or dc == room.w - 1:
                            self.tiles[tr][tc] = Tile.WALL
                        else:
                            self.tiles[tr][tc] = Tile.FLOOR

        # Mark spawn / exit
        if self.spawn_room:
            sc, sr = self.spawn_room.center_tile
            if 0 <= sr < self.grid_h and 0 <= sc < self.grid_w:
                self.tiles[sr][sc] = Tile.SPAWN
        if self.exit_room:
            ec, er = self.exit_room.center_tile
            if 0 <= er < self.grid_h and 0 <= ec < self.grid_w:
                self.tiles[er][ec] = Tile.EXIT

    # ── Corridors ─────────────────────────────────────────────────────────────
    def _carve_corridors(self) -> None:
        carved: set[tuple] = set()
        for room in self.rooms:
            for other in room.connected:
                key = (min(id(room), id(other)), max(id(room), id(other)))
                if key in carved:
                    continue
                carved.add(key)
                self._carve_l_corridor(room.center_tile, other.center_tile)

    def _carve_l_corridor(self, a: tuple[int, int], b: tuple[int, int]) -> None:
        ax, ay = a
        bx, by = b
        half   = CORRIDOR_WIDTH // 2
        # Horizontal leg
        for x in range(min(ax, bx), max(ax, bx) + 1):
            for dy in range(-half, half + 1):
                r = ay + dy
                if 0 < r < self.grid_h - 1 and 0 < x < self.grid_w - 1:
                    if self.tiles[r][x] == Tile.VOID:
                        self.tiles[r][x] = Tile.FLOOR
                    elif self.tiles[r][x] == Tile.WALL:
                        self.tiles[r][x] = Tile.DOOR
        # Vertical leg
        for y in range(min(ay, by), max(ay, by) + 1):
            for dx in range(-half, half + 1):
                c = bx + dx
                if 0 < y < self.grid_h - 1 and 0 < c < self.grid_w - 1:
                    if self.tiles[y][c] == Tile.VOID:
                        self.tiles[y][c] = Tile.FLOOR
                    elif self.tiles[y][c] == Tile.WALL:
                        self.tiles[y][c] = Tile.DOOR

    # ── Wall rects ────────────────────────────────────────────────────────────
    def _build_walls(self) -> None:
        self.walls = []
        for row in range(self.grid_h):
            for col in range(self.grid_w):
                if self.tiles[row][col] in (Tile.WALL, Tile.VOID):
                    self.walls.append(pygame.Rect(
                        col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def is_passable(self, col: int, row: int) -> bool:
        if 0 <= row < self.grid_h and 0 <= col < self.grid_w:
            return self.tiles[row][col] not in (Tile.WALL, Tile.VOID)
        return False

    def world_to_tile(self, wx: float, wy: float) -> tuple[int, int]:
        return int(wx // TILE_SIZE), int(wy // TILE_SIZE)

    def tile_to_world(self, col: int, row: int) -> tuple[float, float]:
        return col * TILE_SIZE + TILE_SIZE / 2, row * TILE_SIZE + TILE_SIZE / 2

    def random_floor_pos(self, room: Room | None = None) -> tuple[float, float]:
        if room:
            for _ in range(100):
                c = random.randint(room.col + 1, room.col + room.w - 2)
                r = random.randint(room.row + 1, room.row + room.h - 2)
                if self.tiles[r][c] == Tile.FLOOR:
                    return self.tile_to_world(c, r)
        for _ in range(500):
            c = random.randint(1, self.grid_w - 2)
            r = random.randint(1, self.grid_h - 2)
            if self.tiles[r][c] == Tile.FLOOR:
                return self.tile_to_world(c, r)
        return TILE_SIZE * 5, TILE_SIZE * 5
