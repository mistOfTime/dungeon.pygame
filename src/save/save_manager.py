# Eclipse Depths - Save Manager

from __future__ import annotations
import json
import os
import sqlite3
from src.core.constants import SAVE_DIR, SAVE_FILENAME, STATS_DB


class SaveManager:
    def __init__(self) -> None:
        os.makedirs(SAVE_DIR, exist_ok=True)
        self._init_db()

    # __ JSON save _____________________________________________________________
    def save(self, player, floor: int, stats, slot: int = 0) -> None:
        data = {
            "floor":  floor,
            "player": player.to_dict(),
        }
        path = os.path.join(SAVE_DIR, SAVE_FILENAME.format(slot=slot))
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, slot: int = 0) -> dict | None:
        path = os.path.join(SAVE_DIR, SAVE_FILENAME.format(slot=slot))
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def has_save(self, slot: int = 0) -> bool:
        path = os.path.join(SAVE_DIR, SAVE_FILENAME.format(slot=slot))
        return os.path.exists(path)

    def delete_save(self, slot: int = 0) -> None:
        path = os.path.join(SAVE_DIR, SAVE_FILENAME.format(slot=slot))
        if os.path.exists(path):
            os.remove(path)

    # __ SQLite stats __________________________________________________________
    def _init_db(self) -> None:
        conn = sqlite3.connect(STATS_DB)
        cur  = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS run_stats (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp     TEXT DEFAULT (datetime('now')),
                kills         INTEGER,
                gold          INTEGER,
                floors        INTEGER,
                damage_dealt  REAL,
                damage_taken  REAL,
                potions_used  INTEGER,
                chests_opened INTEGER,
                play_time     REAL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id   TEXT PRIMARY KEY,
                unlocked_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
        conn.close()

    def save_stats(self, stats) -> None:
        try:
            conn = sqlite3.connect(STATS_DB)
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO run_stats
                  (kills, gold, floors, damage_dealt, damage_taken,
                   potions_used, chests_opened, play_time)
                VALUES (_,_,_,_,_,_,_,_)
            """, (stats.kills, stats.gold, stats.floors,
                  stats.damage_dealt, stats.damage_taken,
                  stats.potions_used, stats.chests_opened, stats.play_time))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def unlock_achievement(self, achievement_id: str) -> None:
        try:
            conn = sqlite3.connect(STATS_DB)
            cur  = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO achievements (id) VALUES (_)",
                        (achievement_id,))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_all_stats(self) -> list[dict]:
        try:
            conn = sqlite3.connect(STATS_DB)
            cur  = conn.cursor()
            cur.execute("SELECT * FROM run_stats ORDER BY id DESC LIMIT 20")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            conn.close()
            return [dict(zip(cols, row)) for row in rows]
        except Exception:
            return []
