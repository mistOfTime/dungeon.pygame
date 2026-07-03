# Eclipse Depths - Settings Manager

from __future__ import annotations
import json
import os
from src.core.constants import (SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS,
                                 MUSIC_VOLUME_DEFAULT, SFX_VOLUME_DEFAULT)

SETTINGS_FILE = "saves/settings.json"

DEFAULTS: dict = {
    "fullscreen":     False,
    "resolution_w":   SCREEN_WIDTH,
    "resolution_h":   SCREEN_HEIGHT,
    "fps_limit":      TARGET_FPS,
    "vsync":          True,
    "music_volume":   MUSIC_VOLUME_DEFAULT,
    "sfx_volume":     SFX_VOLUME_DEFAULT,
    "language":       "en",
    # Key bindings (pygame key constants stored as ints)
    "key_up":         119,   # W
    "key_down":       115,   # S
    "key_left":       97,    # A
    "key_right":      100,   # D
    "key_sprint":     304,   # L-Shift
    "key_dodge":      32,    # Space
    "key_attack":     1,     # Mouse1 (handled separately)
    "key_interact":   101,   # E
    "key_inventory":  105,   # I
    "key_map":        109,   # M
    "key_quest_log":  113,   # Q
    "key_pause":      27,    # Escape
    "key_hotbar_1":   49,    # 1
    "key_hotbar_2":   50,    # 2
    "key_hotbar_3":   51,    # 3
    "key_hotbar_4":   52,    # 4
}


class SettingsManager:
    def __init__(self) -> None:
        self._data: dict = dict(DEFAULTS)
        self._load()

    def _load(self) -> None:
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    loaded = json.load(f)
                self._data.update(loaded)
            except Exception:
                pass

    def save(self) -> None:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default=None):
        return self._data.get(key, DEFAULTS.get(key, default))

    def set(self, key: str, value) -> None:
        self._data[key] = value

    def reset_to_defaults(self) -> None:
        self._data = dict(DEFAULTS)

    @property
    def keybinds(self) -> dict[str, int]:
        return {k: v for k, v in self._data.items() if k.startswith("key_")}
