"""
Classes:
    - Item
    - ItemComponent
    - Weapon
    - Armor
    - Consumable
"""

from enum import Enum
from pygame import Surface, event
from source.core.component import Component
from source.core.tools import Position
from source.resources import TEXTURES as T
from source.effects import EFFECTS as E
from source.traits.effect import Affectible


class Item:
    """
    An item which can be held in an entity's inventory.
    """
    def __init__(self, name: str, weight: int) -> None:
        """
        :param name: The name of the item.
        :param weight: The weight of the item.
        """
        self.name = name
        self.weight = weight


class ItemComponent(Component):
    """
    Used to display an item.
    """
    def __init__(self, item: Item, render_position: Position) -> None:
        """
        :param item: The item which will be rendered.
        :param render_position: The position of the item on the surface.
        """
        self.texture = T.get(f"{item.name}_item")
        super().__init__(render_position, self.texture.get_width(), self.texture.get_height())
        self.item = item

    def update(self, events: list[event.Event]) -> None:
        """ Updates the item.

        :param events: A list of the lastly pulled events.
        """
        pass

    def render(self, surface: Surface) -> None:
        """ Renders the item's texture.

        :param surface: The surface on which the item will be rendered.
        """
        self.texture.render(surface, self.render_position)


class Weapon(Item):
    """
    A weapon item.
    """
    def __init__(self, name: str, weight: int, damage: int) -> None:
        super().__init__(name, weight)
        self.damage = damage


class ArmorSlot(Enum):
    """
    Represents a slot inside an entity's inventory.
    """
    HEAD = 0
    CHEST = 1
    LEGS = 2

    def __str__(self) -> str:
        if self == ArmorSlot.HEAD:
            return "Head"
        elif self == ArmorSlot.CHEST:
            return "Chest"
        elif self == ArmorSlot.LEGS:
            return "Legs"

    def __repr__(self) -> str:
        return self.__str__()


class Armor(Item):
    """
    An armor item.
    """
    def __init__(self, name: str, weight: int, protection: int, slot: ArmorSlot) -> None:
        super().__init__(name, weight)
        self.protection = protection
        self.slot = slot


class Consumable(Item):
    """
    An item which can be used.
    """
    def __init__(self, name: str, weight: int, effect_names: list[str]):
        super().__init__(name, weight)
        self.effect_names = effect_names

    def use(self, target: Affectible) -> None:
        for e in self.effect_names:
            effect = E.get(e)
            effect.target = target
            target.apply_effect(effect)
