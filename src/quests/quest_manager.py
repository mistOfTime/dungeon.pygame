# Eclipse Depths - Quest Manager

from __future__ import annotations
import random
from dataclasses import dataclass, field


@dataclass
class Quest:
    id:          str
    title:       str
    description: str
    quest_type:  str          # "main" | "side" | "daily" | "achievement"
    objective:   str          # "kill_N_X" | "collect_N_X" | "reach_floor_N" | etc.
    target:      int = 1
    progress:    int = 0
    completed:   bool = False
    reward_gold: int = 50
    reward_xp:   int = 100
    reward_item: str = ""

    @property
    def is_complete(self) -> bool:
        return self.progress >= self.target

    def to_dict(self):
        return self.__dict__.copy()


MAIN_QUESTS = [
    Quest("mq_1", "Descent Begins",     "Reach floor 3",        "main", "reach_floor", 3,   reward_gold=100, reward_xp=200),
    Quest("mq_2", "Dungeon Delver",     "Reach floor 5",        "main", "reach_floor", 5,   reward_gold=200, reward_xp=400),
    Quest("mq_3", "First Blood",        "Kill 10 enemies",      "main", "kill_any",    10,  reward_gold=80,  reward_xp=150),
    Quest("mq_4", "Treasure Hunter",    "Open 5 chests",        "main", "open_chest",  5,   reward_gold=120, reward_xp=180),
    Quest("mq_5", "Boss Slayer",        "Defeat your first boss","main","kill_boss",   1,   reward_gold=300, reward_xp=500),
]

SIDE_QUESTS = [
    Quest("sq_1",  "Exterminator",   "Kill 20 Slimes",       "side", "kill_slime",    20, reward_gold=60,  reward_xp=100),
    Quest("sq_2",  "Goblin Bane",    "Kill 15 Goblins",      "side", "kill_goblin",   15, reward_gold=70,  reward_xp=110),
    Quest("sq_3",  "Archaeologist",  "Find 3 secret rooms",  "side", "find_secret",   3,  reward_gold=90,  reward_xp=150),
    Quest("sq_4",  "Moneybags",      "Collect 500 gold",     "side", "collect_gold",  500,reward_gold=0,   reward_xp=200),
    Quest("sq_5",  "Potion Hoarder", "Use 10 potions",       "side", "use_potion",    10, reward_gold=50,  reward_xp=80),
]

ACHIEVEMENTS = [
    Quest("ach_1", "First Steps",      "Complete floor 1",     "achievement", "reach_floor", 1,  reward_gold=30,  reward_xp=50),
    Quest("ach_2", "Speed Runner",     "Complete floor in 3min","achievement","speed_run",   1,  reward_gold=100, reward_xp=150),
    Quest("ach_3", "Untouched",        "Clear a room undamaged","achievement","perfect_room",1,  reward_gold=80,  reward_xp=120),
    Quest("ach_4", "Legendary Finder", "Find a Legendary item", "achievement","find_legendary",1,reward_gold=200, reward_xp=300),
    Quest("ach_5", "Dungeon Master",   "Kill 200 enemies",     "achievement", "kill_any",    200,reward_gold=500, reward_xp=800),
]


class QuestManager:
    def __init__(self, bus) -> None:
        self._bus      = bus
        self.active:   list[Quest] = []
        self.completed:list[Quest] = []
        self._init_quests()
        self._register_events()

    def _init_quests(self) -> None:
        self.active = list(MAIN_QUESTS) + list(SIDE_QUESTS) + list(ACHIEVEMENTS)
        self._generate_daily()

    def _generate_daily(self) -> None:
        random.seed()  # fresh daily
        daily = Quest(
            "daily_1", "Daily Challenge",
            f"Kill {random.randint(5, 20)} enemies",
            "daily", "kill_any", random.randint(5, 20),
            reward_gold=150, reward_xp=200,
        )
        self.active.append(daily)

    def _register_events(self) -> None:
        b = self._bus
        b.subscribe("enemy_killed",   self._on_enemy_killed)
        b.subscribe("chest_opened",   self._on_chest_opened)
        b.subscribe("floor_reached",  self._on_floor_reached)
        b.subscribe("gold_pickup",    self._on_gold_pickup)
        b.subscribe("player_attack",  self._on_potion_used)  # use separate event
        b.subscribe("boss_killed",    self._on_boss_killed)
        b.subscribe("secret_found",   self._on_secret_found)

    def _progress(self, objective_key: str, amount: int = 1) -> None:
        for quest in list(self.active):
            if quest.completed:
                continue
            if quest.objective == objective_key or quest.objective.startswith(objective_key.split("_")[0]):
                quest.progress += amount
                if quest.is_complete and not quest.completed:
                    quest.completed = True
                    self._complete_quest(quest)

    def _complete_quest(self, quest: Quest) -> None:
        self.completed.append(quest)
        if quest in self.active:
            self.active.remove(quest)
        self._bus.publish("quest_complete", {
            "title":       quest.title,
            "reward_gold": quest.reward_gold,
            "reward_xp":   quest.reward_xp,
        })
        self._bus.publish("notification", {
            "text":   f"Quest Complete: {quest.title}",
            "colour": (255, 215, 0),
        })

    # __ Event handlers _______________________________________________________
    def _on_enemy_killed(self, data):
        name = data.get("name", "").lower().replace(" ", "_")
        self._progress("kill_any")
        self._progress(f"kill_{name}")

    def _on_chest_opened(self, data):
        self._progress("open_chest")

    def _on_floor_reached(self, data):
        floor = data.get("floor", 1) if data else 1
        for quest in self.active:
            if not quest.completed and quest.objective == "reach_floor":
                if floor >= quest.target and not quest.completed:
                    quest.progress = quest.target
                    quest.completed = True
                    self._complete_quest(quest)

    def _on_gold_pickup(self, data):
        amount = data.get("amount", 0) if data else 0
        self._progress("collect_gold", amount)

    def _on_potion_used(self, data):
        pass  # handled by consumable system separately

    def _on_boss_killed(self, data):
        self._progress("kill_boss")

    def _on_secret_found(self, data):
        self._progress("find_secret")

    def get_active_by_type(self, t: str) -> list[Quest]:
        return [q for q in self.active if q.quest_type == t]

    def to_dict(self) -> dict:
        return {
            "active":    [q.to_dict() for q in self.active],
            "completed": [q.to_dict() for q in self.completed],
        }
