# Eclipse Depths - Game (main loop / state machine)

from __future__ import annotations
import pygame
import sys
from src.core.constants import *
from src.core.event_bus import EventBus
from src.core.asset_manager import AssetManager
from src.core.camera import Camera
from src.audio.audio_manager import AudioManager
from src.settings.settings_manager import SettingsManager
from src.save.save_manager import SaveManager
from src.ui.hud import HUD
from src.ui.main_menu import MainMenu
from src.ui.pause_menu import PauseMenu
from src.ui.game_over_screen import GameOverScreen
from src.ui.settings_screen import SettingsScreen
from src.ui.inventory_screen import InventoryScreen
from src.ui.map_screen import MapScreen
from src.ui.quest_log_screen import QuestLogScreen
from src.ui.credits_screen import CreditsScreen
from src.world.game_world import GameWorld


class Game:
    """Top-level game controller. Owns the main loop and state machine."""

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init(channels=AUDIO_CHANNELS)
        pygame.display.set_caption(WINDOW_TITLE)

        self.settings   = SettingsManager()
        self._apply_display_settings()

        self.clock      = pygame.time.Clock()
        self.bus        = EventBus()
        self.assets     = AssetManager()
        self.audio      = AudioManager(self.settings)
        self.save_mgr   = SaveManager()

        self.state      = STATE_MAIN_MENU
        self.running    = True
        self.dt         = 0.0

        # Screens / subsystems (lazy-created when first needed)
        self.world:     GameWorld | None     = None
        self.hud:       HUD | None           = None

        self.main_menu      = MainMenu(self.screen, self.assets, self.bus)
        self.pause_menu     = PauseMenu(self.screen, self.assets, self.bus)
        self.game_over_scr  = GameOverScreen(self.screen, self.assets, self.bus)
        self.settings_scr   = SettingsScreen(self.screen, self.assets, self.bus, self.settings)
        self.inventory_scr  = InventoryScreen(self.screen, self.assets, self.bus)
        self.map_scr        = MapScreen(self.screen, self.assets, self.bus)
        self.quest_log_scr  = QuestLogScreen(self.screen, self.assets, self.bus)
        self.credits_scr    = CreditsScreen(self.screen, self.assets, self.bus)

        self._register_bus_events()
        self.audio.play_music("menu")

    # __ Display ______________________________________________________________
    def _apply_display_settings(self) -> None:
        flags = pygame.DOUBLEBUF
        if self.settings.get("fullscreen"):
            flags |= pygame.FULLSCREEN
        w = self.settings.get("resolution_w", SCREEN_WIDTH)
        h = self.settings.get("resolution_h", SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode((w, h), flags, vsync=int(self.settings.get("vsync", True)))

    # __ Event bus wiring _____________________________________________________
    def _register_bus_events(self) -> None:
        b = self.bus
        b.subscribe("new_game",         self._on_new_game)
        b.subscribe("continue_game",    self._on_continue_game)
        b.subscribe("load_game",        self._on_load_game)
        b.subscribe("goto_main_menu",   self._on_goto_main_menu)
        b.subscribe("pause",            self._on_pause)
        b.subscribe("resume",           self._on_resume)
        b.subscribe("open_inventory",   self._on_open_inventory)
        b.subscribe("close_inventory",  self._on_resume)
        b.subscribe("open_map",         self._on_open_map)
        b.subscribe("close_map",        self._on_resume)
        b.subscribe("open_quest_log",   self._on_open_quest_log)
        b.subscribe("close_quest_log",  self._on_resume)
        b.subscribe("open_settings",    self._on_open_settings)
        b.subscribe("close_settings",   self._on_close_settings)
        b.subscribe("open_credits",     self._on_open_credits)
        b.subscribe("close_credits",    self._on_goto_main_menu)
        b.subscribe("player_died",      self._on_player_died)
        b.subscribe("quit_game",        self._on_quit)
        b.subscribe("apply_settings",   self._on_apply_settings)
        b.subscribe("next_floor",       self._on_next_floor)

    # __ Bus handlers _________________________________________________________
    def _on_new_game(self, data=None) -> None:
        slot = data.get("slot", 0) if data else 0
        self._start_world(slot, new=True)

    def _on_continue_game(self, data=None) -> None:
        self._start_world(0, new=False)

    def _on_load_game(self, data=None) -> None:
        slot = data.get("slot", 0) if data else 0
        self._start_world(slot, new=False)

    def _start_world(self, slot: int, new: bool) -> None:
        save_data = None if new else self.save_mgr.load(slot)
        self.world = GameWorld(self.screen, self.assets, self.audio,
                               self.bus, self.settings, save_data, slot)
        self.hud   = HUD(self.screen, self.assets, self.bus, self.world.player)
        self.hud.set_world(self.world)
        self.inventory_scr.set_player(self.world.player)
        self.map_scr.set_world(self.world)
        self.quest_log_scr.set_quest_manager(self.world.quest_manager)
        self.state = STATE_PLAYING
        self.audio.play_music("dungeon")

    def _on_goto_main_menu(self, data=None) -> None:
        self.world = None
        self.hud   = None
        self.state = STATE_MAIN_MENU
        self.audio.play_music("menu")

    def _on_pause(self, data=None)        -> None: self.state = STATE_PAUSED
    def _on_resume(self, data=None)       -> None: self.state = STATE_PLAYING
    def _on_open_inventory(self, data=None) -> None: self.state = STATE_INVENTORY
    def _on_open_map(self, data=None)     -> None: self.state = STATE_MAP
    def _on_open_quest_log(self, data=None) -> None: self.state = STATE_QUEST_LOG

    def _on_open_settings(self, data=None) -> None:
        self._prev_state = self.state
        self.state = STATE_SETTINGS

    def _on_close_settings(self, data=None) -> None:
        self.state = getattr(self, "_prev_state", STATE_MAIN_MENU)

    def _on_open_credits(self, data=None) -> None: self.state = STATE_CREDITS

    def _on_player_died(self, data=None) -> None:
        if self.world:
            self.save_mgr.save_stats(self.world.player.stats)
        self.state = STATE_GAME_OVER

    def _on_next_floor(self, data=None) -> None:
        if self.world:
            self.world.next_floor()

    def _on_apply_settings(self, data=None) -> None:
        self._apply_display_settings()
        self.audio.apply_settings(self.settings)

    def _on_quit(self, data=None) -> None:
        self.running = False

    # __ Main loop ____________________________________________________________
    def run(self) -> None:
        while self.running:
            self.dt = min(self.clock.tick(self.settings.get("fps_limit", TARGET_FPS)) / 1000.0, 0.05)
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
        self._shutdown()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                self.running = False
                return
            self._dispatch_event(event)

    def _dispatch_event(self, event: pygame.Event) -> None:
        s = self.state
        if s == STATE_MAIN_MENU:
            self.main_menu.handle_event(event)
        elif s == STATE_PLAYING:
            if self.world:
                self.world.handle_event(event)
            if self.hud:
                self.hud.handle_event(event)
        elif s == STATE_PAUSED:
            self.pause_menu.handle_event(event)
        elif s == STATE_INVENTORY:
            self.inventory_scr.handle_event(event)
        elif s == STATE_MAP:
            self.map_scr.handle_event(event)
        elif s == STATE_QUEST_LOG:
            self.quest_log_scr.handle_event(event)
        elif s == STATE_GAME_OVER:
            self.game_over_scr.handle_event(event)
        elif s == STATE_SETTINGS:
            self.settings_scr.handle_event(event)
        elif s == STATE_CREDITS:
            self.credits_scr.handle_event(event)

    def _update(self) -> None:
        s  = self.state
        dt = self.dt
        if s == STATE_MAIN_MENU:
            self.main_menu.update(dt)
        elif s == STATE_PLAYING:
            if self.world: self.world.update(dt)
            if self.hud:   self.hud.update(dt)
        elif s == STATE_PAUSED:
            self.pause_menu.update(dt)
        elif s == STATE_INVENTORY:
            self.inventory_scr.update(dt)
        elif s == STATE_MAP:
            self.map_scr.update(dt)
        elif s == STATE_QUEST_LOG:
            self.quest_log_scr.update(dt)
        elif s == STATE_GAME_OVER:
            self.game_over_scr.update(dt)
        elif s == STATE_SETTINGS:
            self.settings_scr.update(dt)
        elif s == STATE_CREDITS:
            self.credits_scr.update(dt)

    def _draw(self) -> None:
        self.screen.fill(DARK_GREY)
        s = self.state
        if s == STATE_MAIN_MENU:
            self.main_menu.draw()
        elif s in (STATE_PLAYING, STATE_PAUSED, STATE_INVENTORY, STATE_MAP, STATE_QUEST_LOG):
            if self.world: self.world.draw()
            if self.hud:   self.hud.draw()
            if s == STATE_PAUSED:
                self.pause_menu.draw()
            elif s == STATE_INVENTORY:
                self.inventory_scr.draw()
            elif s == STATE_MAP:
                self.map_scr.draw()
            elif s == STATE_QUEST_LOG:
                self.quest_log_scr.draw()
        elif s == STATE_GAME_OVER:
            self.game_over_scr.draw()
        elif s == STATE_SETTINGS:
            self.settings_scr.draw()
        elif s == STATE_CREDITS:
            self.credits_scr.draw()

    def _shutdown(self) -> None:
        if self.world:
            self.save_mgr.save(self.world.player, self.world.current_floor,
                               self.world.player.stats, slot=self.world.save_slot)
        pygame.quit()
        sys.exit(0)
