#!/usr/bin/env python3
"""
Eclipse Depths - Web entry point for Pygbag (WebAssembly/itch.io)
Run locally: pygbag main_web.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


async def main() -> None:
    # Pygame must be imported AFTER asyncio loop starts for pygbag
    import pygame
    from src.core.constants import (TARGET_FPS, SCREEN_WIDTH, SCREEN_HEIGHT,
                                     WINDOW_TITLE, DARK_GREY,
                                     STATE_MAIN_MENU, STATE_PLAYING,
                                     STATE_PAUSED, STATE_INVENTORY,
                                     STATE_MAP, STATE_QUEST_LOG,
                                     STATE_GAME_OVER, STATE_SETTINGS,
                                     STATE_CREDITS)
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

    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    pygame.display.set_caption(WINDOW_TITLE)

    screen   = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock    = pygame.time.Clock()

    settings = SettingsManager()
    bus      = EventBus()
    assets   = AssetManager()
    audio    = AudioManager(settings)
    save_mgr = SaveManager()

    state    = STATE_MAIN_MENU
    world    = None
    hud      = None

    main_menu    = MainMenu(screen, assets, bus)
    pause_menu   = PauseMenu(screen, assets, bus)
    game_over    = GameOverScreen(screen, assets, bus)
    settings_scr = SettingsScreen(screen, assets, bus, settings)
    inv_scr      = InventoryScreen(screen, assets, bus)
    map_scr      = MapScreen(screen, assets, bus)
    quest_scr    = QuestLogScreen(screen, assets, bus)
    credits_scr  = CreditsScreen(screen, assets, bus)

    # ?? State transitions ????????????????????????????????????????????????????
    def start_world(new: bool = True) -> None:
        nonlocal world, hud, state
        from src.world.game_world import GameWorld
        save_data = None if new else save_mgr.load(0)
        world = GameWorld(screen, assets, audio, bus, settings, save_data, 0)
        hud   = HUD(screen, assets, bus, world.player)
        hud.set_world(world)
        inv_scr.set_player(world.player)
        map_scr.set_world(world)
        quest_scr.set_quest_manager(world.quest_manager)
        state = STATE_PLAYING
        audio.play_music("dungeon")

    _prev_state = STATE_MAIN_MENU

    def on_event(ev: str, data=None) -> None:
        nonlocal state, world, hud, _prev_state
        if ev == "new_game":          start_world(True)
        elif ev == "continue_game":   start_world(False)
        elif ev == "load_game":       start_world(False)
        elif ev == "goto_main_menu":
            world = hud = None
            state = STATE_MAIN_MENU
            audio.play_music("menu")
        elif ev == "pause":           state = STATE_PAUSED
        elif ev == "resume":          state = STATE_PLAYING
        elif ev == "open_inventory":  state = STATE_INVENTORY
        elif ev == "close_inventory": state = STATE_PLAYING
        elif ev == "open_map":        state = STATE_MAP
        elif ev == "close_map":       state = STATE_PLAYING
        elif ev == "open_quest_log":  state = STATE_QUEST_LOG
        elif ev == "close_quest_log": state = STATE_PLAYING
        elif ev == "open_settings":
            _prev_state = state
            state = STATE_SETTINGS
        elif ev == "close_settings":  state = _prev_state
        elif ev == "open_credits":    state = STATE_CREDITS
        elif ev == "close_credits":   state = STATE_MAIN_MENU
        elif ev == "player_died":
            if world:
                save_mgr.save_stats(world.player.stats)
            state = STATE_GAME_OVER
        elif ev == "next_floor":
            if world: world.next_floor()
        elif ev == "apply_settings":
            audio.apply_settings(settings)
        elif ev == "quit_game":
            pygame.quit()
            sys.exit(0)

    for ev_name in [
        "new_game","continue_game","load_game","goto_main_menu",
        "pause","resume","open_inventory","close_inventory",
        "open_map","close_map","open_quest_log","close_quest_log",
        "open_settings","close_settings","open_credits","close_credits",
        "player_died","quit_game","apply_settings","next_floor",
    ]:
        # Capture ev_name in closure
        (lambda n: bus.subscribe(n, lambda d, name=n: on_event(name, d)))(ev_name)

    audio.play_music("menu")

    # ?? Main loop (async for pygbag) ?????????????????????????????????????????
    running = True
    while running:
        dt = min(clock.tick(TARGET_FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F4:
                running = False
                break
            # Dispatch to current screen
            if state == STATE_MAIN_MENU:      main_menu.handle_event(event)
            elif state == STATE_PLAYING:
                if world: world.handle_event(event)
                if hud:   hud.handle_event(event)
            elif state == STATE_PAUSED:       pause_menu.handle_event(event)
            elif state == STATE_INVENTORY:    inv_scr.handle_event(event)
            elif state == STATE_MAP:          map_scr.handle_event(event)
            elif state == STATE_QUEST_LOG:    quest_scr.handle_event(event)
            elif state == STATE_GAME_OVER:    game_over.handle_event(event)
            elif state == STATE_SETTINGS:     settings_scr.handle_event(event)
            elif state == STATE_CREDITS:      credits_scr.handle_event(event)

        # Update
        if state == STATE_MAIN_MENU:      main_menu.update(dt)
        elif state in (STATE_PLAYING, STATE_PAUSED,
                       STATE_INVENTORY, STATE_MAP, STATE_QUEST_LOG):
            if world: world.update(dt)
            if hud:   hud.update(dt)
            if state == STATE_PAUSED:     pause_menu.update(dt)
            elif state == STATE_INVENTORY: inv_scr.update(dt)
            elif state == STATE_MAP:       map_scr.update(dt)
            elif state == STATE_QUEST_LOG: quest_scr.update(dt)
        elif state == STATE_GAME_OVER:    game_over.update(dt)
        elif state == STATE_SETTINGS:     settings_scr.update(dt)
        elif state == STATE_CREDITS:      credits_scr.update(dt)

        # Draw
        screen.fill(DARK_GREY)
        if state == STATE_MAIN_MENU:
            main_menu.draw()
        elif state in (STATE_PLAYING, STATE_PAUSED,
                       STATE_INVENTORY, STATE_MAP, STATE_QUEST_LOG):
            if world: world.draw()
            if hud:   hud.draw()
            if state == STATE_PAUSED:      pause_menu.draw()
            elif state == STATE_INVENTORY: inv_scr.draw()
            elif state == STATE_MAP:       map_scr.draw()
            elif state == STATE_QUEST_LOG: quest_scr.draw()
        elif state == STATE_GAME_OVER:    game_over.draw()
        elif state == STATE_SETTINGS:     settings_scr.draw()
        elif state == STATE_CREDITS:      credits_scr.draw()

        pygame.display.flip()
        await asyncio.sleep(0)   # ? required by pygbag every frame

    pygame.quit()


asyncio.run(main())
