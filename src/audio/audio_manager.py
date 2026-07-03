# Eclipse Depths - Audio Manager

from __future__ import annotations
import pygame
import os
from src.core.constants import MUSIC_VOLUME_DEFAULT, SFX_VOLUME_DEFAULT

MUSIC_TRACKS: dict[str, list[str]] = {
    "menu":    ["assets/audio/music_menu.ogg"],
    "dungeon": ["assets/audio/music_dungeon.ogg", "assets/audio/music_dungeon2.ogg"],
    "boss":    ["assets/audio/music_boss.ogg"],
    "victory": ["assets/audio/music_victory.ogg"],
}


class AudioManager:
    """Wraps pygame.mixer for music and SFX with volume control."""

    def __init__(self, settings) -> None:
        self._settings   = settings
        self._sfx_cache: dict[str, pygame.mixer.Sound | None] = {}
        self._current_track: str = ""
        self._music_vol  = settings.get("music_volume", MUSIC_VOLUME_DEFAULT)
        self._sfx_vol    = settings.get("sfx_volume",   SFX_VOLUME_DEFAULT)
        pygame.mixer.set_num_channels(32)

    # ── Music ─────────────────────────────────────────────────────────────────
    def play_music(self, key: str, loop: int = -1, fade_ms: int = 1500) -> None:
        if key == self._current_track:
            return
        tracks = MUSIC_TRACKS.get(key, [])
        for track in tracks:
            if os.path.exists(track):
                pygame.mixer.music.fadeout(800)
                pygame.mixer.music.load(track)
                pygame.mixer.music.set_volume(self._music_vol)
                pygame.mixer.music.play(loop, fade_ms=fade_ms)
                self._current_track = key
                return
        # No file present — silence is fine
        pygame.mixer.music.stop()
        self._current_track = key

    def stop_music(self, fade_ms: int = 500) -> None:
        pygame.mixer.music.fadeout(fade_ms)
        self._current_track = ""

    # ── SFX ──────────────────────────────────────────────────────────────────
    def play_sfx(self, key: str, volume: float | None = None) -> None:
        snd = self._get_sound(key)
        if snd:
            vol = volume if volume is not None else self._sfx_vol
            snd.set_volume(vol)
            snd.play()

    def _get_sound(self, key: str) -> pygame.mixer.Sound | None:
        if key not in self._sfx_cache:
            for ext in (".ogg", ".wav"):
                path = f"assets/audio/{key}{ext}"
                if os.path.exists(path):
                    try:
                        self._sfx_cache[key] = pygame.mixer.Sound(path)
                        return self._sfx_cache[key]
                    except Exception:
                        pass
            self._sfx_cache[key] = None
        return self._sfx_cache[key]

    # ── Volume ────────────────────────────────────────────────────────────────
    def set_music_volume(self, vol: float) -> None:
        self._music_vol = max(0.0, min(1.0, vol))
        pygame.mixer.music.set_volume(self._music_vol)

    def set_sfx_volume(self, vol: float) -> None:
        self._sfx_vol = max(0.0, min(1.0, vol))

    def apply_settings(self, settings) -> None:
        self.set_music_volume(settings.get("music_volume", MUSIC_VOLUME_DEFAULT))
        self.set_sfx_volume(settings.get("sfx_volume", SFX_VOLUME_DEFAULT))
