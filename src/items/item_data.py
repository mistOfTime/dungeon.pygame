# Eclipse Depths - Item definitions and random generation

from __future__ import annotations
import random
from dataclasses import dataclass, field
from src.core.constants import RARITY_COLOURS
from src.utils.helpers import weighted_choice


RARITY_WEIGHTS = [
    ("Common",    50),
    ("Uncommon",  25),
    ("Rare",      14),
    ("Epic",       7),
    ("Legendary",  3),
    ("Mythic",     1),
]

RARITY_STAT_MULT = {
    "Common":    1.0,
    "Uncommon":  1.25,
    "Rare":      1.55,
    "Epic":      1.90,
    "Legendary": 2.40,
    "Mythic":    3.20,
}


@dataclass
class ItemStats:
    damage:       float = 0.0
    defense:      float = 0.0
    hp_bonus:     float = 0.0
    mana_bonus:   float = 0.0
    speed_bonus:  float = 0.0
    crit_chance:  float = 0.0
    crit_mult:    float = 0.0
    attack_speed: float = 0.0
    knockback:    float = 0.0
    range_bonus:  float = 0.0
    life_steal:   float = 0.0
    mana_regen:   float = 0.0


@dataclass
class Item:
    id:          str
    name:        str
    item_type:   str          # weapon / armor / ring / necklace / consumable / material / spell
    subtype:     str = ""     # sword / bow / helmet / chest _
    rarity:      str = "Common"
    description: str = ""
    value:       int = 10
    stackable:   bool = False
    stack_size:  int = 1
    max_stack:   int = 1
    sprite_key:  str = ""
    stats:       ItemStats = field(default_factory=ItemStats)
    spell_id:    str = ""     # if item_type == "spell"
    effect_id:   str = ""     # if consumable

    @property
    def colour(self) -> tuple:
        return RARITY_COLOURS.get(self.rarity, (180, 180, 180))


# __ Base item templates _______________________________________________________
WEAPON_TEMPLATES = [
    dict(id="sword",    name="Sword",      subtype="sword",    sprite_key="sword",
         stats=ItemStats(damage=18, attack_speed=1.0, crit_chance=0.08, knockback=5)),
    dict(id="axe",      name="Axe",        subtype="axe",      sprite_key="axe",
         stats=ItemStats(damage=26, attack_speed=0.7, crit_chance=0.05, knockback=9)),
    dict(id="dagger",   name="Dagger",     subtype="dagger",   sprite_key="dagger",
         stats=ItemStats(damage=12, attack_speed=1.8, crit_chance=0.18, knockback=3)),
    dict(id="spear",    name="Spear",      subtype="spear",    sprite_key="spear",
         stats=ItemStats(damage=20, attack_speed=0.9, crit_chance=0.07, knockback=6, range_bonus=24)),
    dict(id="hammer",   name="Hammer",     subtype="hammer",   sprite_key="hammer",
         stats=ItemStats(damage=34, attack_speed=0.55, crit_chance=0.04, knockback=14)),
    dict(id="bow",      name="Bow",        subtype="bow",      sprite_key="bow",
         stats=ItemStats(damage=15, attack_speed=1.1, crit_chance=0.12, range_bonus=200)),
    dict(id="crossbow", name="Crossbow",   subtype="crossbow", sprite_key="crossbow",
         stats=ItemStats(damage=22, attack_speed=0.7, crit_chance=0.10, range_bonus=220)),
    dict(id="staff",    name="Magic Staff",subtype="staff",    sprite_key="staff",
         stats=ItemStats(damage=14, attack_speed=0.9, crit_chance=0.09, range_bonus=190, mana_regen=2)),
]

ARMOR_TEMPLATES = [
    dict(id="helmet",   name="Helmet",    subtype="helmet",  sprite_key="helmet",
         stats=ItemStats(defense=4, hp_bonus=10)),
    dict(id="chest",    name="Chest Armor",subtype="chest",  sprite_key="chest",
         stats=ItemStats(defense=8, hp_bonus=20)),
    dict(id="gloves",   name="Gloves",    subtype="gloves",  sprite_key="gloves",
         stats=ItemStats(defense=2, attack_speed=0.05, crit_chance=0.02)),
    dict(id="boots",    name="Boots",     subtype="boots",   sprite_key="boots",
         stats=ItemStats(defense=3, speed_bonus=10)),
]

ACCESSORY_TEMPLATES = [
    dict(id="ring",     name="Ring",      subtype="ring",    sprite_key="ring",
         stats=ItemStats(crit_chance=0.04, life_steal=0.02)),
    dict(id="necklace", name="Necklace",  subtype="necklace",sprite_key="necklace",
         stats=ItemStats(hp_bonus=15, mana_bonus=10)),
]

CONSUMABLE_TEMPLATES = [
    dict(id="health_potion",  name="Health Potion",  effect_id="heal_50",    value=20,  stackable=True, max_stack=5,  sprite_key="potion_red"),
    dict(id="mana_potion",    name="Mana Potion",    effect_id="mana_40",    value=18,  stackable=True, max_stack=5,  sprite_key="potion_blue"),
    dict(id="stamina_potion", name="Stamina Potion", effect_id="stamina_50", value=15,  stackable=True, max_stack=5,  sprite_key="potion_green"),
    dict(id="elixir",         name="Elixir",         effect_id="heal_100",   value=60,  stackable=True, max_stack=3,  sprite_key="potion_gold"),
    dict(id="bomb",           name="Bomb",           effect_id="explode_30", value=25,  stackable=True, max_stack=5,  sprite_key="bomb"),
]


def roll_rarity(floor: int = 1) -> str:
    # Higher floors shift weights toward rarer
    weights = list(RARITY_WEIGHTS)
    if floor > 3:
        bonus = min(floor - 3, 6)
        weights = [(r, max(1, w - bonus * 2 if r == "Common" else w + bonus // 2))
                   for r, w in weights]
    return weighted_choice(weights)


def generate_weapon(floor: int = 1) -> Item:
    tmpl   = random.choice(WEAPON_TEMPLATES)
    rarity = roll_rarity(floor)
    mult   = RARITY_STAT_MULT[rarity]
    prefix = _rarity_prefix(rarity)
    s      = tmpl["stats"]
    scaled = ItemStats(
        damage       = round(s.damage       * mult * random.uniform(0.9, 1.1), 1),
        attack_speed = round(s.attack_speed * random.uniform(0.95, 1.05), 2),
        crit_chance  = round(min(s.crit_chance  + (mult - 1) * 0.05, 0.6), 2),
        knockback    = round(s.knockback    * mult, 1),
        range_bonus  = s.range_bonus,
        mana_regen   = s.mana_regen,
    )
    return Item(
        id=tmpl["id"], name=f"{prefix} {tmpl['name']}", item_type="weapon",
        subtype=tmpl["subtype"], rarity=rarity, stats=scaled,
        sprite_key=tmpl["sprite_key"], value=int(20 * mult),
    )


def generate_armor(floor: int = 1, subtype: str | None = None) -> Item:
    pool = ARMOR_TEMPLATES
    if subtype:
        pool = [t for t in pool if t["subtype"] == subtype] or pool
    tmpl   = random.choice(pool)
    rarity = roll_rarity(floor)
    mult   = RARITY_STAT_MULT[rarity]
    prefix = _rarity_prefix(rarity)
    s      = tmpl["stats"]
    scaled = ItemStats(
        defense      = round(s.defense    * mult * random.uniform(0.9, 1.1), 1),
        hp_bonus     = round(s.hp_bonus   * mult, 1),
        mana_bonus   = s.mana_bonus,
        speed_bonus  = s.speed_bonus,
        attack_speed = s.attack_speed,
        crit_chance  = s.crit_chance,
    )
    return Item(
        id=tmpl["id"], name=f"{prefix} {tmpl['name']}", item_type="armor",
        subtype=tmpl["subtype"], rarity=rarity, stats=scaled,
        sprite_key=tmpl["sprite_key"], value=int(15 * mult),
    )


def generate_accessory(floor: int = 1) -> Item:
    tmpl   = random.choice(ACCESSORY_TEMPLATES)
    rarity = roll_rarity(floor)
    mult   = RARITY_STAT_MULT[rarity]
    prefix = _rarity_prefix(rarity)
    s      = tmpl["stats"]
    scaled = ItemStats(
        hp_bonus    = round(s.hp_bonus    * mult, 1),
        mana_bonus  = round(s.mana_bonus  * mult, 1),
        crit_chance = round(s.crit_chance * mult, 2),
        life_steal  = round(s.life_steal  * mult, 2),
    )
    return Item(
        id=tmpl["id"], name=f"{prefix} {tmpl['name']}", item_type=tmpl["subtype"],
        subtype=tmpl["subtype"], rarity=rarity, stats=scaled,
        sprite_key=tmpl["sprite_key"], value=int(25 * mult),
    )


def make_consumable(consumable_id: str) -> Item:
    tmpl = next((t for t in CONSUMABLE_TEMPLATES if t["id"] == consumable_id), CONSUMABLE_TEMPLATES[0])
    return Item(
        id=tmpl["id"], name=tmpl["name"], item_type="consumable",
        effect_id=tmpl["effect_id"], value=tmpl["value"],
        stackable=tmpl.get("stackable", False), stack_size=1,
        max_stack=tmpl.get("max_stack", 1), sprite_key=tmpl.get("sprite_key", ""),
        rarity="Common",
    )


def _rarity_prefix(rarity: str) -> str:
    return {
        "Common":    "",
        "Uncommon":  "Fine",
        "Rare":      "Superior",
        "Epic":      "Arcane",
        "Legendary": "Ancient",
        "Mythic":    "Mythic",
    }.get(rarity, "")
