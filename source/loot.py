"""
Classes:
    - ItemBook
    - LootTable
"""

from json import loads
from random import Random
from source.item import Item, Armor, Weapon, ArmorSlot, Consumable


class ItemBook:
    """
    A registry of every item present in the game.
    """
    def __init__(self) -> None:
        self.items: dict[str, Item] = {}

    def load(self, path: str) -> None:
        """ Loads a set of items from a JSON file.

        :param path: The path of the JSON file to load the items from.
        """
        file = open(path, "r")
        data = loads(file.read())
        file.close()

        for item in data:
            if data[item]["type"] == "armor":
                self.items[item] = Armor(item, data[item]["weight"], data[item]["protection"], ArmorSlot(data[item]["slot"]))
            elif data[item]["type"] == "weapon":
                self.items[item] = Weapon(item, data[item]["weight"], data[item]["damage"])
            elif data[item]["type"] == "consumable":
                self.items[item] = Consumable(item, data[item]["weight"], data[item]["effects"])
            else:
                self.items[item] = Item(item, data[item]["weight"])

    def add(self, name: str, item: Item) -> None:
        """ Adds an item to the registry.

        :param name: The name of the item.
        :param item: The item to add.
        """
        self.items[name] = item

    def get(self, name: str) -> Item:
        """ Get an item from the registry.

        :param name: The name of the item.
        """
        return self.items[name]


ITEMS = ItemBook()


class LootTable:
    """
    A way to determine the loot present in rooms.
    """
    def __init__(self, path: str, rng: Random):
        """
        :param path: The path from which the loot table's data should be loaded.
        """
        file = open(path, "r")
        data = loads(file.read())
        file.close()

        self.table: dict[Item, float] = {}
        for item in data["items"]:
            self.table[ITEMS.get(item)] = data["items"][item]

        self.amount = data["amount"]
        self.rng = rng

    def get_items(self) -> list[Item]:
        """ Returns a random list of items present in the loot table, based on their drop rate.

        :return: A list of items, of size equal to the amount specified in the JSON file.
        """
        items = list(self.table.keys())

        rates = list(self.table.values())
        if 1.0 - sum(rates) > 0:
            items.append(None)
            rates.append(1.0 - sum(rates))

        return self.rng.choices(items, weights=rates, k=self.amount)

    def get_weapon(self) -> Weapon:
        """ Get a random weapon from the table.

        :return: A weapon from the table, based on the drop rate of each weapon present in the table.
        """
        weapons = {i: self.table[i] for i in self.table if isinstance(i, Weapon)}
        if len(weapons) >= 1:
            return self.rng.choices(list(weapons.keys()), weights=list(weapons.values()), k=1)[0]
        else:
            return None

    def get_armor(self) -> Armor:
        """ Get a random armor piece from the table.

        :return: An armor piece from the table, based on the drop rate of each armor piece present in the table.
        """
        armors = {i: self.table[i] for i in self.table if isinstance(i, Armor)}
        if len(armors) >= 1:
            return self.rng.choices(list(armors.keys()), weights=list(armors.values()), k=1)[0]
        else:
            return None
