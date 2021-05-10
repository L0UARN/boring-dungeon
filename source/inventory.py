"""
Classes:
    - Inventory
    - InventoryComponent
    - InventoryLayer
"""

from source.item import Item, Weapon, Armor, ArmorSlot


class Inventory:
    """
    Represents the inventory of an entity. Contains items, weapons, armor...
    """
    def __init__(self) -> None:
        self.misc: list[Item] = [None for _ in range(8)]
        self.weapon: Weapon = None
        self.armor: dict[ArmorSlot, Armor] = {slot: None for slot in ArmorSlot}

    def add_item(self, item: Item) -> int:
        """ Adds an item to the inventory.

        :param item: The item to add.
        :return: The index of the slot in which the item was placed, or -1 if there wasn't enough space.
        """
        if self.misc.count(None) > 0:
            index = self.misc.index(None)
            self.misc[index] = item
            return index
        return -1

    def get_item(self, index: int) -> Item:
        """ Get the item placed at the specified index.

        :param index: The index of the desired item.
        :return: The item set on the given index.
        """
        return self.misc[index]

    def remove_item(self, index: int) -> None:
        """ Removes an item from the inventory.

        :param index: The index of the slot in which the item is placed.
        """
        self.misc[index] = None

    def set_weapon(self, weapon: Weapon, store_current: bool = True) -> bool:
        """ Changes the currently equipped weapon.

        :param weapon: The weapon to equip.
        :param store_current: True if the currently equipped weapon must return to the inventory.
        :return: True if the operation was successful, False if not.
        """
        if store_current and self.weapon is not None and self.add_item(self.weapon) == -1:
            return False
        self.weapon = weapon
        return True

    def get_weapon(self) -> Weapon:
        """ Get the equipped weapon.

        :return: The equipped weapon.
        """
        return self.weapon

    def store_weapon(self) -> int:
        """ Stores away the equipped weapon.

        :return: The index of the slot in which the weapon is placed.
        """
        index = self.add_item(self.weapon)
        if index != -1:
            self.weapon = None
        return index

    def set_armor(self, armor: Armor, store_current: bool = True) -> bool:
        """ Changes an equipped armor piece.

        :param armor: The armor piece to equip.
        :param store_current: True if the armor currently equipped in the slot must return to the inventory.
        :return: True if the operation was successful, False if not.
        """
        if store_current and self.armor[armor.slot] is not None and self.add_item(self.armor[armor.slot]) == -1:
            return False
        self.armor[armor.slot] = armor
        return True

    def get_armor(self, slot: ArmorSlot) -> Armor:
        """ Get the armor equipped at the specified slot.

        :param slot: The slot of the wanted armor.
        :return: The armor placed in the given slot.
        """
        return self.armor[slot]

    def store_armor(self, armor_slot: ArmorSlot) -> int:
        """ Stores away a piece of equipped armor.

        :param armor_slot: The slot in which the armor is.
        :return: The index of the slot in which the armor is placed.
        """
        index = self.add_item(self.armor[armor_slot])
        if index != -1:
            self.armor[armor_slot] = None
        return index

    def get_protection(self) -> int:
        """ Get the total protection granted by the equipped armor.

        :return: The total protection granted by the equipped armor.
        """
        total = 0
        for slot in ArmorSlot:
            if self.armor[slot] is not None:
                total += self.armor[slot].protection

    def get_equipped_weight(self) -> int:
        """ Get the total weight of the equipped gear.

        :return: The total weight of the equipped gear.
        """
        total = 0
        if self.weapon is not None:
            total += self.weapon.weight
        for slot in ArmorSlot:
            if self.armor[slot] is not None:
                total += self.armor[slot].weight
        return total
