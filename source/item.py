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
from source.core.texture import Texture


class Item:
    """
    An item which can be held in an entity's inventory.
    """
    def __init__(self, weight: int) -> None:
        self.weight = weight


class ItemComponent(Component):
    """
    Used to display an item.
    """
    def __init__(self, item: Item, texture: Texture, render_position: Position) -> None:
        super().__init__(render_position, texture.get_width(), texture.get_height())
        self.item = item
        self.texture = texture

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
    def __init__(self, weight: int, damage: int) -> None:
        super().__init__(weight)
        self.damage = damage


class ArmorSlot(Enum):
    """
    Represents a slot inside an entity's inventory.
    """
    HEAD = 1
    CHEST = 2
    LEGS = 3


class Armor(Item):
    """
    An armor item.
    """
    def __init__(self, weight: int, protection: int, slot: ArmorSlot) -> None:
        super().__init__(weight)
        self.protection = protection
        self.slot = slot
