# Eclipse Depths - Dungeon Renderer (realistic stone dungeon)

from __future__ import annotations
import pygame
import random
import math
from src.core.constants import TILE_SIZE
from src.dungeon.dungeon_generator import Tile

# ── Colour palette ────────────────────────────────────────────────────────────
VOID_COL      = (4,   3,   8)

# Floor: dark stone slabs with mortar lines
FLOOR_BASE    = (52,  46,  58)
FLOOR_DARK    = (42,  36,  48)
FLOOR_LIGHT   = (68,  60,  75)
FLOOR_MORTAR  = (32,  28,  38)

# Wall: stone blocks with depth
WALL_FACE     = (38,  32,  50)
WALL_TOP      = (60,  52,  70)   # lit top face (light comes from above)
WALL_SHADOW   = (22,  18,  30)
WALL_CRACK    = (28,  22,  36)
WALL_HIGHLIGHT= (72,  64,  85)

# Corridor floor
CORR_FLOOR    = (46,  40,  54)

# Door
DOOR_WOOD     = (100, 72,  38)
DOOR_IRON     = (70,  65,  80)
DOOR_TRIM     = (140, 110, 50)

# Special tiles
EXIT_COL      = (60,  160, 100)
SPAWN_COL     = (60,  90,  160)
TRAP_COL      = (140, 35,  35)

# Ambient torch glow areas (drawn as overlay on floor)
TORCH_GLOW    = (200, 140, 60, 18)


class DungeonRenderer:
    """Renders a rich stone-dungeon tile grid and manages fog of war."""

    FOG_SEEN_ALPHA = 110

    def __init__(self, generator, assets) -> None:
        self._gen    = generator
        self._assets = assets
        self._rng    = random.Random(hash(id(generator)))   # deterministic per dungeon
        self._tile_surface: pygame.Surface | None = None
        self._fog:   list[list[int]] = []
        self._torch_positions: list[tuple[int,int]] = []
        self._init_fog()
        self._build_surface()

    # ── Fog ──────────────────────────────────────────────────────────────────
    def _init_fog(self) -> None:
        g = self._gen
        self._fog = [[0] * g.grid_w for _ in range(g.grid_h)]

    def update_visibility(self, player_col: int, player_row: int,
                          radius: int = 9) -> None:
        g = self._gen
        for row in range(g.grid_h):
            for col in range(g.grid_w):
                if self._fog[row][col] == 2:
                    self._fog[row][col] = 1
        r2 = radius * radius
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r = player_row + dr
                c = player_col + dc
                if 0 <= r < g.grid_h and 0 <= c < g.grid_w:
                    if dr * dr + dc * dc <= r2:
                        self._fog[r][c] = 2

    # ── Surface build ─────────────────────────────────────────────────────────
    def _build_surface(self) -> None:
        g   = self._gen
        w   = g.grid_w * TILE_SIZE
        h   = g.grid_h * TILE_SIZE
        surf = pygame.Surface((w, h))
        surf.fill(VOID_COL)

        # First pass: base tile colours
        for row in range(g.grid_h):
            for col in range(g.grid_w):
                t  = g.tiles[row][col]
                px = col * TILE_SIZE
                py = row * TILE_SIZE
                if   t == Tile.VOID:    self._draw_void(surf, px, py)
                elif t == Tile.FLOOR:   self._draw_floor(surf, px, py, col, row)
                elif t == Tile.WALL:    self._draw_wall(surf, px, py, col, row, g)
                elif t == Tile.DOOR:    self._draw_door(surf, px, py, col, row, g)
                elif t == Tile.EXIT:    self._draw_exit(surf, px, py)
                elif t == Tile.SPAWN:   self._draw_spawn(surf, px, py)
                elif t == Tile.TRAP:    self._draw_floor(surf, px, py, col, row)
                else:                   self._draw_floor(surf, px, py, col, row)

        # Second pass: wall shadows cast onto adjacent floor
        for row in range(g.grid_h):
            for col in range(g.grid_w):
                if g.tiles[row][col] == Tile.WALL:
                    self._draw_wall_shadow(surf, col, row, g)

        # Third pass: torch glow spots on floors
        self._place_torches(g)
        for tc, tr in self._torch_positions:
            self._draw_torch_glow(surf, tc, tr)

        self._tile_surface = surf

    # ── Tile draw helpers ─────────────────────────────────────────────────────
    def _draw_void(self, surf, px, py) -> None:
        pygame.draw.rect(surf, VOID_COL, (px, py, TILE_SIZE, TILE_SIZE))

    def _draw_floor(self, surf, px, py, col, row) -> None:
        rng = self._rng
        # Base slab
        var = rng.randint(-5, 5)
        base = (
            min(255, max(0, FLOOR_BASE[0] + var)),
            min(255, max(0, FLOOR_BASE[1] + var)),
            min(255, max(0, FLOOR_BASE[2] + var)),
        )
        pygame.draw.rect(surf, base, (px, py, TILE_SIZE, TILE_SIZE))

        # Stone slab pattern: divide tile into 2×2 sub-slabs with mortar lines
        half = TILE_SIZE // 2
        # Subtle alternating shade for slab halves
        offset = (col + row) % 2
        slab_shade = FLOOR_LIGHT if offset == 0 else FLOOR_DARK
        for si in range(2):
            for sj in range(2):
                slab_var = rng.randint(-3, 3)
                sc = (
                    min(255, max(0, slab_shade[0] + slab_var)),
                    min(255, max(0, slab_shade[1] + slab_var)),
                    min(255, max(0, slab_shade[2] + slab_var)),
                )
                sx = px + si * half + 1
                sy = py + sj * half + 1
                pygame.draw.rect(surf, sc, (sx, sy, half - 2, half - 2))

        # Mortar grid lines
        pygame.draw.line(surf, FLOOR_MORTAR, (px, py + half), (px + TILE_SIZE, py + half), 1)
        pygame.draw.line(surf, FLOOR_MORTAR, (px + half, py), (px + half, py + TILE_SIZE), 1)
        pygame.draw.rect(surf, FLOOR_MORTAR, (px, py, TILE_SIZE, TILE_SIZE), 1)

        # Random surface detail (cracks, pebbles)
        detail_roll = rng.random()
        if detail_roll < 0.06:   # small crack
            cx1 = px + rng.randint(4, TILE_SIZE - 4)
            cy1 = py + rng.randint(4, TILE_SIZE - 4)
            cx2 = cx1 + rng.randint(-5, 5)
            cy2 = cy1 + rng.randint(-5, 5)
            pygame.draw.line(surf, WALL_CRACK, (cx1, cy1), (cx2, cy2), 1)
        elif detail_roll < 0.10:  # pebble dot
            px2 = px + rng.randint(3, TILE_SIZE - 3)
            py2 = py + rng.randint(3, TILE_SIZE - 3)
            pygame.draw.circle(surf, FLOOR_DARK, (px2, py2), 1)

    def _draw_wall(self, surf, px, py, col, row, g) -> None:
        rng = self._rng
        # Determine which faces of this wall are exposed to floor
        has_floor_below = self._adj_floor(g, col, row + 1)
        has_floor_above = self._adj_floor(g, col, row - 1)
        has_floor_left  = self._adj_floor(g, col - 1, row)
        has_floor_right = self._adj_floor(g, col + 1, row)

        # Base wall face
        var = rng.randint(-4, 4)
        face = (
            min(255, max(0, WALL_FACE[0] + var)),
            min(255, max(0, WALL_FACE[1] + var)),
            min(255, max(0, WALL_FACE[2] + var)),
        )
        pygame.draw.rect(surf, face, (px, py, TILE_SIZE, TILE_SIZE))

        # Stone block pattern: 2 rows of 2 blocks per tile
        bw, bh = TILE_SIZE // 2, TILE_SIZE // 2
        for bi in range(2):
            for bj in range(2):
                # Offset alternate rows (brick-style)
                row_offset = (bj % 2) * (bw // 2)
                bx = px + (bi * bw + row_offset) % TILE_SIZE
                by2 = py + bj * bh
                block_var = rng.randint(-3, 3)
                bc = (
                    min(255, max(0, face[0] + block_var)),
                    min(255, max(0, face[1] + block_var)),
                    min(255, max(0, face[2] + block_var)),
                )
                pygame.draw.rect(surf, bc, (bx + 1, by2 + 1, bw - 2, bh - 2))

        # Mortar lines
        pygame.draw.line(surf, WALL_SHADOW,
                         (px, py + bh), (px + TILE_SIZE, py + bh), 1)
        pygame.draw.line(surf, WALL_SHADOW,
                         (px + bw, py), (px + bw, py + bh), 1)
        # Second row offset
        half2 = bw // 2
        pygame.draw.line(surf, WALL_SHADOW,
                         (px + half2, py + bh), (px + half2, py + TILE_SIZE), 1)
        pygame.draw.rect(surf, WALL_SHADOW, (px, py, TILE_SIZE, TILE_SIZE), 1)

        # Top-lit highlight on walls exposed to above
        if has_floor_above or row == 0:
            pygame.draw.rect(surf, WALL_TOP, (px, py, TILE_SIZE, 3))

        # Random wall details
        detail = rng.random()
        if detail < 0.04:   # crack
            cx1 = px + rng.randint(3, TILE_SIZE - 3)
            cy1 = py + rng.randint(3, TILE_SIZE - 3)
            pygame.draw.line(surf, WALL_CRACK,
                             (cx1, cy1),
                             (cx1 + rng.randint(-6, 6), cy1 + rng.randint(-6, 6)), 1)
        elif detail < 0.06:  # mossy patch
            mx = px + rng.randint(2, TILE_SIZE - 6)
            my = py + rng.randint(2, TILE_SIZE - 6)
            pygame.draw.ellipse(surf, (40, 70, 40), (mx, my, 5, 3))

        # Wall face shading: darker at bottom
        if has_floor_below:
            shade = pygame.Surface((TILE_SIZE, 6), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 60))
            surf.blit(shade, (px, py + TILE_SIZE - 6))

    def _draw_wall_shadow(self, surf, col, row, g) -> None:
        """Cast a soft shadow from wall onto adjacent floor tile."""
        shadow_surf = pygame.Surface((TILE_SIZE, 6), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 50))

        # Shadow falls south (below wall)
        nr, nc = row + 1, col
        if 0 <= nr < g.grid_h and g.tiles[nr][nc] == Tile.FLOOR:
            surf.blit(shadow_surf, (nc * TILE_SIZE, nr * TILE_SIZE))

        # Thin shadow east
        shadow_e = pygame.Surface((4, TILE_SIZE), pygame.SRCALPHA)
        shadow_e.fill((0, 0, 0, 35))
        nr2, nc2 = row, col + 1
        if 0 <= nc2 < g.grid_w and g.tiles[nr2][nc2] == Tile.FLOOR:
            surf.blit(shadow_e, (nc2 * TILE_SIZE, nr2 * TILE_SIZE))

    def _draw_door(self, surf, px, py, col, row, g) -> None:
        # Floor base under door
        self._draw_floor(surf, px, py, col, row)
        # Determine orientation
        horiz = (self._adj_wall(g, col, row - 1) or self._adj_wall(g, col, row + 1))
        if horiz:
            # Horizontal door (wall above/below) — draw as arch
            pygame.draw.rect(surf, DOOR_WOOD,    (px + 2, py + 4, TILE_SIZE - 4, TILE_SIZE - 8))
            pygame.draw.rect(surf, DOOR_IRON,    (px + 2, py + 4, TILE_SIZE - 4, 5))
            pygame.draw.rect(surf, DOOR_TRIM,    (px + 2, py + 4, TILE_SIZE - 4, TILE_SIZE - 8), 1)
            # Arch top
            pygame.draw.arc(surf, DOOR_TRIM,
                            pygame.Rect(px + 4, py + 2, TILE_SIZE - 8, 8), 0, math.pi, 2)
            # Door handle
            pygame.draw.circle(surf, DOOR_TRIM, (px + TILE_SIZE // 2, py + TILE_SIZE // 2 + 2), 2)
        else:
            # Vertical door
            pygame.draw.rect(surf, DOOR_WOOD,    (px + 4, py + 2, TILE_SIZE - 8, TILE_SIZE - 4))
            pygame.draw.rect(surf, DOOR_IRON,    (px + 4, py + 2, 5, TILE_SIZE - 4))
            pygame.draw.rect(surf, DOOR_TRIM,    (px + 4, py + 2, TILE_SIZE - 8, TILE_SIZE - 4), 1)
            pygame.draw.circle(surf, DOOR_TRIM, (px + TILE_SIZE // 2 + 2, py + TILE_SIZE // 2), 2)

    def _draw_exit(self, surf, px, py) -> None:
        # Floor base
        pygame.draw.rect(surf, FLOOR_BASE, (px, py, TILE_SIZE, TILE_SIZE))
        # Portal circle
        cx, cy = px + TILE_SIZE // 2, py + TILE_SIZE // 2
        pygame.draw.circle(surf, (30, 120, 70), (cx, cy), 12)
        pygame.draw.circle(surf, (60, 200, 120), (cx, cy), 10)
        pygame.draw.circle(surf, (120, 255, 170), (cx, cy), 6)
        pygame.draw.circle(surf, (200, 255, 220), (cx, cy), 3)
        # Rune ring
        for i in range(6):
            angle = i * math.pi / 3
            rx = cx + int(math.cos(angle) * 14)
            ry = cy + int(math.sin(angle) * 14)
            pygame.draw.circle(surf, (60, 180, 100), (rx, ry), 2)

    def _draw_spawn(self, surf, px, py) -> None:
        self._draw_floor(surf, px, py, 0, 0)
        cx, cy = px + TILE_SIZE // 2, py + TILE_SIZE // 2
        pygame.draw.circle(surf, (40, 70, 140, 120), (cx, cy), 11)
        pygame.draw.circle(surf, (80, 120, 200), (cx, cy), 8)
        pygame.draw.circle(surf, (140, 180, 255), (cx, cy), 4)

    # ── Torch system ─────────────────────────────────────────────────────────
    def _place_torches(self, g) -> None:
        """Place torch glows at wall tiles that border floor."""
        rng = self._rng
        self._torch_positions = []
        for row in range(g.grid_h):
            for col in range(g.grid_w):
                if g.tiles[row][col] == Tile.WALL:
                    if self._adj_floor(g, col, row + 1) or self._adj_floor(g, col - 1, row):
                        if rng.random() < 0.06:
                            self._torch_positions.append((col, row))

    def _draw_torch_glow(self, surf, col, row) -> None:
        """Draw warm glow radiating from wall-mounted torch position."""
        cx = col * TILE_SIZE + TILE_SIZE // 2
        cy = row * TILE_SIZE + TILE_SIZE // 2
        radius = TILE_SIZE * 3
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -4):
            alpha = int(12 * (1 - r / radius))
            pygame.draw.circle(glow, (200, 140, 60, alpha), (radius, radius), r)
        surf.blit(glow, (cx - radius, cy - radius),
                  special_flags=pygame.BLEND_RGBA_ADD)
        # Tiny torch dot on wall
        pygame.draw.circle(surf, (255, 200, 80), (cx, cy - 4), 2)
        pygame.draw.circle(surf, (255, 240, 180), (cx, cy - 4), 1)

    # ── Adjacency helpers ─────────────────────────────────────────────────────
    def _adj_floor(self, g, col: int, row: int) -> bool:
        if 0 <= row < g.grid_h and 0 <= col < g.grid_w:
            return g.tiles[row][col] in (Tile.FLOOR, Tile.DOOR,
                                          Tile.EXIT, Tile.SPAWN,
                                          Tile.TRAP, Tile.CHEST)
        return False

    def _adj_wall(self, g, col: int, row: int) -> bool:
        if 0 <= row < g.grid_h and 0 <= col < g.grid_w:
            return g.tiles[row][col] == Tile.WALL
        return False

    # ── Draw (camera-culled) ──────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface, camera) -> None:
        if self._tile_surface is None:
            return

        cx, cy = camera.offset
        vw     = surface.get_width()
        vh     = surface.get_height()
        min_col = max(0, int(cx // TILE_SIZE) - 1)
        max_col = min(self._gen.grid_w,  int((cx + vw) // TILE_SIZE) + 2)
        min_row = max(0, int(cy // TILE_SIZE) - 1)
        max_row = min(self._gen.grid_h, int((cy + vh) // TILE_SIZE) + 2)

        # Pre-build a reusable fog surface
        fog_seen = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        fog_seen.fill((6, 4, 12, self.FOG_SEEN_ALPHA))

        for row in range(min_row, max_row):
            for col in range(min_col, max_col):
                fog_state = self._fog[row][col]
                if fog_state == 0:
                    continue

                tile_rect   = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                          TILE_SIZE, TILE_SIZE)
                screen_rect = camera.apply(tile_rect)

                surface.blit(self._tile_surface, screen_rect,
                             (col * TILE_SIZE, row * TILE_SIZE,
                              TILE_SIZE, TILE_SIZE))

                if fog_state == 1:
                    surface.blit(fog_seen, screen_rect)
