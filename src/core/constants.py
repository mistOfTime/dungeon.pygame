# Eclipse Depths - Constants
# Central configuration for the entire game

import pygame

# ── Window ──────────────────────────────────────────────────────────────────
WINDOW_TITLE   = "Eclipse Depths"
SCREEN_WIDTH   = 1280
SCREEN_HEIGHT  = 720
TARGET_FPS     = 60
TILE_SIZE      = 32

# ── Colours ──────────────────────────────────────────────────────────────────
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
RED          = (220, 50,  50)
GREEN        = (50,  200, 80)
BLUE         = (50,  100, 220)
YELLOW       = (255, 220, 0)
ORANGE       = (255, 140, 0)
PURPLE       = (160, 32,  240)
CYAN         = (0,   220, 220)
DARK_GREY    = (30,  30,  35)
MID_GREY     = (60,  60,  70)
LIGHT_GREY   = (160, 160, 170)
GOLD         = (255, 215, 0)
DARK_RED     = (140, 20,  20)
DARK_BLUE    = (20,  30,  80)
DARK_GREEN   = (20,  80,  30)
TRANSPARENT  = (0,   0,   0,  0)

# ── Rarity colours ───────────────────────────────────────────────────────────
RARITY_COLOURS = {
    "Common":    (180, 180, 180),
    "Uncommon":  (30,  200, 80),
    "Rare":      (60,  130, 230),
    "Epic":      (160, 50,  240),
    "Legendary": (255, 165, 0),
    "Mythic":    (220, 50,  80),
}

# ── Player defaults ──────────────────────────────────────────────────────────
PLAYER_SPEED         = 200          # px/s
PLAYER_SPRINT_MULT   = 1.6
PLAYER_ACCEL         = 1800
PLAYER_DECEL         = 1400
PLAYER_MAX_HP        = 100
PLAYER_MAX_MANA      = 80
PLAYER_MAX_STAMINA   = 100
PLAYER_STAMINA_REGEN = 25           # per second
PLAYER_MANA_REGEN    = 5
DODGE_DURATION       = 0.25         # seconds
DODGE_SPEED          = 520
DODGE_IFRAMES        = 0.4
DODGE_COOLDOWN       = 1.0
SPRINT_STAMINA_COST  = 20           # per second
DODGE_STAMINA_COST   = 25

# ── Combat ───────────────────────────────────────────────────────────────────
CRIT_MULTIPLIER      = 2.0
COMBO_WINDOW         = 0.6          # seconds between combo hits
KNOCKBACK_FRICTION   = 800

# ── Dungeon generation ───────────────────────────────────────────────────────
DUNGEON_MIN_ROOMS    = 10
DUNGEON_MAX_ROOMS    = 18
ROOM_MIN_W           = 12           # in tiles
ROOM_MAX_W           = 22
ROOM_MIN_H           = 10
ROOM_MAX_H           = 18
CORRIDOR_WIDTH       = 3

# ── Camera ───────────────────────────────────────────────────────────────────
CAMERA_SMOOTHING     = 8.0          # higher = snappier
CAMERA_SHAKE_DECAY   = 5.0

# ── Particle ─────────────────────────────────────────────────────────────────
MAX_PARTICLES        = 600

# ── Layers / draw order ──────────────────────────────────────────────────────
LAYER_FLOOR          = 0
LAYER_SHADOW         = 1
LAYER_OBJECT         = 2
LAYER_ENTITY         = 3
LAYER_PROJECTILE     = 4
LAYER_EFFECT         = 5
LAYER_UI             = 6

# ── Game states ──────────────────────────────────────────────────────────────
STATE_MAIN_MENU      = "main_menu"
STATE_PLAYING        = "playing"
STATE_PAUSED         = "paused"
STATE_INVENTORY      = "inventory"
STATE_MAP            = "map"
STATE_QUEST_LOG      = "quest_log"
STATE_GAME_OVER      = "game_over"
STATE_SETTINGS       = "settings"
STATE_CREDITS        = "credits"
STATE_LOADING        = "loading"

# ── Directions ───────────────────────────────────────────────────────────────
DIR_N  = (0,  -1)
DIR_S  = (0,   1)
DIR_E  = (1,   0)
DIR_W  = (-1,  0)
DIR_NE = (1,  -1)
DIR_NW = (-1, -1)
DIR_SE = (1,   1)
DIR_SW = (-1,  1)
DIRECTIONS_8 = [DIR_N, DIR_S, DIR_E, DIR_W, DIR_NE, DIR_NW, DIR_SE, DIR_SW]

# ── Audio ─────────────────────────────────────────────────────────────────────
MUSIC_VOLUME_DEFAULT  = 0.7
SFX_VOLUME_DEFAULT    = 0.8
AUDIO_CHANNELS        = 32

# ── Save ─────────────────────────────────────────────────────────────────────
SAVE_DIR             = "saves"
SAVE_FILENAME        = "save_slot_{slot}.json"
STATS_DB             = "saves/stats.db"

# ── XP curve ─────────────────────────────────────────────────────────────────
def xp_for_level(level: int) -> int:
    """XP required to reach *level* from *level-1*."""
    return int(100 * (level ** 1.5))

# ── Floor difficulty scaling ─────────────────────────────────────────────────
def enemy_hp_scale(floor: int) -> float:
    return 1.0 + (floor - 1) * 0.18

def enemy_dmg_scale(floor: int) -> float:
    return 1.0 + (floor - 1) * 0.12
