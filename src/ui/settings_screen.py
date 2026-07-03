# Eclipse Depths - Settings Screen

from __future__ import annotations
import pygame
from src.core.constants import *
from src.ui.main_menu import Button


class Slider:
    def __init__(self, x: int, y: int, w: int, label: str,
                 min_val: float, max_val: float, value: float,
                 font: pygame.font.Font) -> None:
        self.rect     = pygame.Rect(x, y, w, 14)
        self.label    = label
        self.min_val  = min_val
        self.max_val  = max_val
        self.value    = value
        self.font     = font
        self._dragging = False

    def handle_event(self, event: pygame.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._dragging = True
        if event.type == pygame.MOUSEBUTTONUP:
            self._dragging = False
        if event.type == pygame.MOUSEMOTION and self._dragging:
            rel = (event.pos[0] - self.rect.x) / self.rect.width
            self.value = max(self.min_val, min(self.max_val,
                             self.min_val + rel * (self.max_val - self.min_val)))
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (50, 45, 70), self.rect, border_radius=4)
        ratio = (self.value - self.min_val) / max(self.max_val - self.min_val, 0.001)
        fill_w = int(self.rect.width * ratio)
        pygame.draw.rect(surface, (100, 80, 180),
                         (self.rect.x, self.rect.y, fill_w, self.rect.height),
                         border_radius=4)
        pygame.draw.rect(surface, (120, 100, 180), self.rect, 1, border_radius=4)
        # Handle
        hx = self.rect.x + fill_w
        pygame.draw.circle(surface, (200, 180, 255), (hx, self.rect.centery), 8)
        # Label + value
        lbl = self.font.render(f"{self.label}: {self.value:.0%}" if self.max_val <= 1.0
                               else f"{self.label}: {int(self.value)}",
                               True, WHITE)
        surface.blit(lbl, (self.rect.x, self.rect.y - 18))


class SettingsScreen:
    def __init__(self, screen: pygame.Surface, assets, bus, settings) -> None:
        self.screen   = screen
        self.assets   = assets
        self.bus      = bus
        self.settings = settings
        self._font    = assets.font(14)
        self._font_title = assets.font(22, bold=True)

        sw, sh = screen.get_size()
        cx     = sw // 2

        self._sliders = [
            Slider(cx - 160, sh//2 - 80,  320, "Music Volume",
                   0.0, 1.0, settings.get("music_volume", 0.7), self._font),
            Slider(cx - 160, sh//2 - 20,  320, "SFX Volume",
                   0.0, 1.0, settings.get("sfx_volume", 0.8),   self._font),
            Slider(cx - 160, sh//2 + 40,  320, "FPS Limit",
                   30,  240, settings.get("fps_limit", 60),      self._font),
        ]

        bw, bh = 180, 40
        self._btn_apply = Button(cx - 200, sh//2 + 120, bw, bh, "Apply", self._font)
        self._btn_close = Button(cx + 20,  sh//2 + 120, bw, bh, "Close", self._font)

        self._fullscreen_on = settings.get("fullscreen", False)
        self._vsync_on      = settings.get("vsync", True)

    def handle_event(self, event: pygame.Event) -> None:
        for s in self._sliders:
            s.handle_event(event)
        if self._btn_apply.handle_event(event):
            self._apply()
        if self._btn_close.handle_event(event):
            self.bus.publish("close_settings")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.bus.publish("close_settings")
        # Checkboxes
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            sw, sh = self.screen.get_size()
            fs_rect = pygame.Rect(self.screen.get_width()//2 - 160, sh//2 + 80, 20, 20)
            vs_rect = pygame.Rect(self.screen.get_width()//2 + 20,  sh//2 + 80, 20, 20)
            if fs_rect.collidepoint(event.pos):
                self._fullscreen_on = not self._fullscreen_on
            if vs_rect.collidepoint(event.pos):
                self._vsync_on = not self._vsync_on

    def _apply(self) -> None:
        s = self.settings
        s.set("music_volume",  self._sliders[0].value)
        s.set("sfx_volume",    self._sliders[1].value)
        s.set("fps_limit",     int(self._sliders[2].value))
        s.set("fullscreen",    self._fullscreen_on)
        s.set("vsync",         self._vsync_on)
        s.save()
        self.bus.publish("apply_settings")

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        sw, sh = self.screen.get_size()
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        pw, ph = 500, 380
        px, py = sw//2 - pw//2, sh//2 - ph//2
        panel  = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((14, 11, 26, 230))
        pygame.draw.rect(panel, (70, 55, 110), panel.get_rect(), 2, border_radius=10)
        self.screen.blit(panel, (px, py))

        title = self._font_title.render("SETTINGS", True, (200, 180, 255))
        self.screen.blit(title, (sw//2 - title.get_width()//2, py + 14))

        for sl in self._sliders:
            sl.draw(self.screen)

        # Checkboxes
        cx2 = sw // 2
        fs_rect = pygame.Rect(cx2 - 160, sh//2 + 80, 20, 20)
        vs_rect = pygame.Rect(cx2 + 20,  sh//2 + 80, 20, 20)
        for rect, on, label in [(fs_rect, self._fullscreen_on, "Fullscreen"),
                                  (vs_rect,  self._vsync_on,      "VSync")]:
            pygame.draw.rect(self.screen, (50, 45, 70), rect, border_radius=3)
            if on:
                pygame.draw.rect(self.screen, (100, 80, 180), rect, border_radius=3)
                tick = self._font.render("✓", True, WHITE)
                self.screen.blit(tick, (rect.x + 3, rect.y + 2))
            pygame.draw.rect(self.screen, (120, 100, 160), rect, 1, border_radius=3)
            lbl = self._font.render(label, True, WHITE)
            self.screen.blit(lbl, (rect.x + 26, rect.y + 2))

        self._btn_apply.draw(self.screen)
        self._btn_close.draw(self.screen)
