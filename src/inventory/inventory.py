# Eclipse Depths - Inventory system

from __future__ import annotations
from typing import Optional
from src.items.item_data import Item


INVENTORY_COLS  = 8
INVENTORY_ROWS  = 5
INVENTORY_SIZE  = INVENTORY_COLS * INVENTORY_ROWS   # 40 slots

HOTBAR_SIZE     = 4

EQUIPMENT_SLOTS = ["weapon", "shield", "helmet", "chest", "gloves", "boots", "ring", "necklace"]


class Inventory:
    """Grid inventory with equipment slots and a hotbar."""

    def __init__(self) -> None:
        self._slots:     list[Item | None]        = [None] * INVENTORY_SIZE
        self._hotbar:    list[Item | None]        = [None] * HOTBAR_SIZE
        self._equipment: dict[str, Item | None]   = {s: None for s in EQUIPMENT_SLOTS}

    # ── Core add/remove ──────────────────────────────────────────────────────
    def add_item(self, item: Item) -> bool:
        """Returns True if the item was added successfully.
        Consumables are also auto-assigned to the first free hotbar slot."""
        if item.stackable:
            for slot in self._slots:
                if slot and slot.id == item.id and slot.stack_size < slot.max_stack:
                    slot.stack_size += item.stack_size
                    if slot.stack_size > slot.max_stack:
                        slot.stack_size = slot.max_stack
                    # Keep hotbar reference in sync
                    self._sync_hotbar_stack(item.id, slot.stack_size)
                    return True
        for i, slot in enumerate(self._slots):
            if slot is None:
                self._slots[i] = item
                # Auto-assign consumables to first free hotbar slot
                if item.item_type == "consumable":
                    self._try_auto_hotbar(item)
                return True
        return False

    def _try_auto_hotbar(self, item: Item) -> None:
        """Put item reference into first empty hotbar slot."""
        for i in range(HOTBAR_SIZE):
            if self._hotbar[i] is None:
                self._hotbar[i] = item
                return

    def _sync_hotbar_stack(self, item_id: str, new_stack: int) -> None:
        """Keep hotbar stack counts in sync after stacking."""
        for slot in self._hotbar:
            if slot and slot.id == item_id:
                slot.stack_size = new_stack

    def remove_item(self, index: int, count: int = 1) -> Optional[Item]:
        item = self._slots[index]
        if not item:
            return None
        if item.stackable and item.stack_size > count:
            item.stack_size -= count
            import copy
            removed = copy.copy(item)
            removed.stack_size = count
            return removed
        self._slots[index] = None
        return item

    def remove_item_by_id(self, item_id: str, count: int = 1) -> bool:
        for i, slot in enumerate(self._slots):
            if slot and slot.id == item_id:
                if slot.stackable and slot.stack_size > count:
                    slot.stack_size -= count
                else:
                    self._slots[i] = None
                return True
        return False

    def swap(self, idx_a: int, idx_b: int) -> None:
        self._slots[idx_a], self._slots[idx_b] = self._slots[idx_b], self._slots[idx_a]

    def sort(self) -> None:
        items = [s for s in self._slots if s is not None]
        items.sort(key=lambda i: (i.item_type, i.rarity, i.name))
        self._slots = items + [None] * (INVENTORY_SIZE - len(items))

    # ── Equipment ────────────────────────────────────────────────────────────
    def equip(self, inv_index: int) -> bool:
        item = self._slots[inv_index]
        if not item:
            return False
        slot_name = self._resolve_equip_slot(item)
        if slot_name is None:
            return False
        old_item = self._equipment[slot_name]
        self._equipment[slot_name] = item
        self._slots[inv_index] = old_item
        return True

    def unequip(self, slot_name: str) -> bool:
        item = self._equipment[slot_name]
        if not item:
            return False
        if self.add_item(item):
            self._equipment[slot_name] = None
            return True
        return False

    def _resolve_equip_slot(self, item: Item) -> Optional[str]:
        if item.item_type == "weapon":
            return "weapon"
        if item.item_type == "armor":
            return item.subtype if item.subtype in EQUIPMENT_SLOTS else None
        if item.subtype in EQUIPMENT_SLOTS:
            return item.subtype
        return None

    # ── Hotbar ───────────────────────────────────────────────────────────────
    def set_hotbar(self, hotbar_idx: int, inv_index: int) -> None:
        if 0 <= hotbar_idx < HOTBAR_SIZE and 0 <= inv_index < INVENTORY_SIZE:
            self._hotbar[hotbar_idx] = self._slots[inv_index]

    def hotbar_item(self, idx: int) -> Item | None:
        if 0 <= idx < HOTBAR_SIZE:
            return self._hotbar[idx]
        return None

    def use_hotbar(self, idx: int) -> Optional[Item]:
        """Returns item for use; removes consumable from inventory."""
        item = self._hotbar[idx]
        if not item:
            return None
        if item.item_type == "consumable":
            self.remove_item_by_id(item.id, 1)
            if not self.has_item(item.id):
                self._hotbar[idx] = None
        return item

    def has_item(self, item_id: str) -> bool:
        return any(s and s.id == item_id for s in self._slots)

    def count_item(self, item_id: str) -> int:
        return sum(s.stack_size for s in self._slots if s and s.id == item_id)

    # ── Stats aggregation ────────────────────────────────────────────────────
    def total_stats(self):
        from src.items.item_data import ItemStats
        total = ItemStats()
        for item in self._equipment.values():
            if item:
                s = item.stats
                total.damage       += s.damage
                total.defense      += s.defense
                total.hp_bonus     += s.hp_bonus
                total.mana_bonus   += s.mana_bonus
                total.speed_bonus  += s.speed_bonus
                total.crit_chance  += s.crit_chance
                total.crit_mult    += s.crit_mult
                total.attack_speed += s.attack_speed
                total.knockback    += s.knockback
                total.life_steal   += s.life_steal
                total.mana_regen   += s.mana_regen
        return total

    # ── Serialisation ────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        def serial(item):
            if item is None:
                return None
            return {"id": item.id, "name": item.name, "rarity": item.rarity,
                    "stack_size": item.stack_size, "item_type": item.item_type,
                    "subtype": item.subtype}
        return {
            "slots":     [serial(s) for s in self._slots],
            "hotbar":    [serial(s) for s in self._hotbar],
            "equipment": {k: serial(v) for k, v in self._equipment.items()},
        }

    @property
    def slots(self): return self._slots
    @property
    def equipment(self): return self._equipment
    @property
    def hotbar(self): return self._hotbar
