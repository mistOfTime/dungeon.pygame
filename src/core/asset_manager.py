# Eclipse Depths - Asset Manager

from __future__ import annotations
import pygame
import os
from src.core.constants import TILE_SIZE


class AssetManager:
    """Loads, caches, and provides access to all game assets.
    Falls back to procedurally generated surfaces when files are absent."""

    ASSET_ROOT = "assets"

    def __init__(self) -> None:
        self._images:  dict[str, pygame.Surface] = {}
        self._fonts:   dict[tuple, pygame.font.Font] = {}
        self._sounds:  dict[str, pygame.mixer.Sound] = {}
        self._preload()

    # __ Preload _______________________________________________________________
    def _preload(self) -> None:
        """Load any bundled assets that exist on disk."""
        # Fonts _ try to load a pixel font; fall back to system default
        font_path = os.path.join(self.ASSET_ROOT, "fonts", "pixel.ttf")
        self._default_font_path = font_path if os.path.exists(font_path) else None

    # __ Images ________________________________________________________________
    def image(self, key: str, fallback_size=(TILE_SIZE, TILE_SIZE),
              fallback_colour=(200, 200, 200)) -> pygame.Surface:
        if key in self._images:
            return self._images[key]
        path = os.path.join(self.ASSET_ROOT, "sprites", f"{key}.png")
        if os.path.exists(path):
            surf = pygame.image.load(path).convert_alpha()
        else:
            surf = self._make_placeholder(fallback_size, fallback_colour, key)
        self._images[key] = surf
        return surf

    def tile(self, key: str, fallback_colour=(80, 60, 50)) -> pygame.Surface:
        if key in self._images:
            return self._images[key]
        path = os.path.join(self.ASSET_ROOT, "tiles", f"{key}.png")
        if os.path.exists(path):
            surf = pygame.image.load(path).convert()
        else:
            surf = self._make_tile_placeholder(fallback_colour, key)
        self._images[key] = surf
        return surf

    def ui_image(self, key: str, size=(32, 32), colour=(100, 100, 120)) -> pygame.Surface:
        full_key = f"ui_{key}"
        if full_key in self._images:
            return self._images[full_key]
        path = os.path.join(self.ASSET_ROOT, "ui", f"{key}.png")
        if os.path.exists(path):
            surf = pygame.image.load(path).convert_alpha()
        else:
            surf = self._make_placeholder(size, colour, key)
        self._images[full_key] = surf
        return surf

    # __ Fonts _________________________________________________________________
    def font(self, size: int = 16, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in self._fonts:
            if self._default_font_path:
                try:
                    self._fonts[key] = pygame.font.Font(self._default_font_path, size)
                    return self._fonts[key]
                except Exception:
                    pass
            self._fonts[key] = pygame.font.SysFont("consolas" if not bold else "consolas", size, bold=bold)
        return self._fonts[key]

    # __ Sounds ________________________________________________________________
    def sound(self, key: str) -> pygame.mixer.Sound | None:
        if key in self._sounds:
            return self._sounds[key]
        for ext in (".ogg", ".wav", ".mp3"):
            path = os.path.join(self.ASSET_ROOT, "audio", f"{key}{ext}")
            if os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    self._sounds[key] = snd
                    return snd
                except Exception:
                    pass
        return None  # silent fallback

    # __ Placeholders _________________________________________________________
    @staticmethod
    def _make_placeholder(size: tuple, colour: tuple, label: str = "") -> pygame.Surface:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((*colour[:3], 200))
        if label:
            font = pygame.font.SysFont("consolas", max(8, size[1] // 4))
            txt  = font.render(label[:6], True, (255, 255, 255))
            surf.blit(txt, txt.get_rect(center=(size[0]//2, size[1]//2)))
        pygame.draw.rect(surf, (255, 255, 255, 80), surf.get_rect(), 1)
        return surf

    @staticmethod
    def _make_tile_placeholder(colour: tuple, label: str = "") -> pygame.Surface:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(colour)
        pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 1)
        return surf

    # __ Sprite sheets _________________________________________________________
    def sprite_sheet(self, key: str, frame_w: int, frame_h: int) -> list[pygame.Surface]:
        """Slice a sprite sheet into frames."""
        sheet = self.image(key, (frame_w, frame_h))
        cols  = sheet.get_width()  // frame_w
        rows  = sheet.get_height() // frame_h
        frames: list[pygame.Surface] = []
        for row in range(rows):
            for col in range(cols):
                frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (col * frame_w, row * frame_h, frame_w, frame_h))
                frames.append(frame)
        return frames
