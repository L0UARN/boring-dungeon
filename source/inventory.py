"""
Classes:
    - Inventory
    - InventoryComponent
    - InventoryLayer
"""

from pygame import Surface, event, draw, Rect, MOUSEBUTTONDOWN, mouse, MOUSEMOTION
from source.item import Item, Weapon, Armor, ArmorSlot, ItemComponent, Consumable
from source.core.component import Component
from source.core.tools import Position
from source.resources import TEXTURES as T
from source.core.layer import Layer
from source.ui.darkener import DarkenerComponent
from source.core.texture import Texture
from source.ui.box import BoxComponent
from source.ui.text import TextComponent


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

        return total

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


class InventoryComponent(Component):
    """
    Used to display an inventory.
    """
    def __init__(self, inventory: Inventory, entity, render_position: Position) -> None:
        """
        :param inventory: The inventory that will be displayed.
        :param entity: The entity who owns the inventory.
        :param render_position: The position at which to render the inventory.
        """
        self.misc_texture = T.get("inventory_misc")
        self.equipped_texture = T.get("inventory_equipped")

        super().__init__(render_position, self.misc_texture.get_width() + self.equipped_texture.get_width(), self.misc_texture.get_height())

        self.inventory = inventory
        self.entity = entity

        self.misc_components = [ItemComponent(Item("empty", 0), Position(0, 0)) for i in range(len(self.inventory.misc))]
        self.armor_components = [ItemComponent(Item("empty", 0), Position(0, 0)) for i in range(len(ArmorSlot))]
        self.weapon_component = ItemComponent(Item("empty", 0), Position(0, 0))

    def update(self, events: list[event.Event]) -> None:
        """ Updates the inventory and manage the mouse interaction.

        :param events: A list of the lastly pulled events.
        """
        self.misc_components = [
            ItemComponent(
                self.inventory.misc[i] if self.inventory.misc[i] is not None else Item("empty", 0),
                Position(
                    self.render_position.x + (64 + 96) * Texture.UIScale * (i % 4) + 32 * Texture.UIScale,
                    self.render_position.y + (64 + 96) * Texture.UIScale * (i // 4) + 32 * Texture.UIScale
                )
            )
            for i in range(len(self.inventory.misc))
        ]

        self.armor_components = [
            ItemComponent(
                self.inventory.armor[ArmorSlot(i)] if self.inventory.armor[ArmorSlot(i)] is not None else Armor("empty_armor", 0, 0, ArmorSlot(i)),
                Position(
                    self.render_position.x + self.misc_texture.get_width() + (32 * Texture.UIScale),
                    self.render_position.y + (8 + 96) * Texture.UIScale * i + 8 * Texture.UIScale
                )
            )
            for i in range(len(ArmorSlot))
        ]

        self.weapon_component = ItemComponent(
            self.inventory.weapon if self.inventory.weapon is not None else Weapon("empty_weapon", 0, 0),
            Position(
                self.render_position.x + self.misc_texture.get_width() + 192 * Texture.UIScale,
                self.render_position.y + 112 * Texture.UIScale
            )
        )

        for e in events:
            if e.type == MOUSEBUTTONDOWN:
                position = Position(mouse.get_pos()[0], mouse.get_pos()[1])

                if e.button == 1:  # left click
                    for i in range(len(self.misc_components)):
                        if self.misc_components[i].render_position.x <= position.x <= self.misc_components[i].render_position.x + 96 * Texture.UIScale and \
                           self.misc_components[i].render_position.y <= position.y <= self.misc_components[i].render_position.y + 96 * Texture.UIScale:
                            if isinstance(self.misc_components[i].item, Armor):
                                self.inventory.set_armor(self.misc_components[i].item, True)
                                self.inventory.remove_item(i)
                            elif isinstance(self.misc_components[i].item, Weapon):
                                self.inventory.set_weapon(self.misc_components[i].item, True)
                                self.inventory.remove_item(i)
                            elif isinstance(self.misc_components[i].item, Consumable):
                                self.misc_components[i].item.use(self.entity)
                                self.inventory.remove_item(i)
                            break

                    for item in self.armor_components:
                        if item.render_position.x <= position.x <= item.render_position.x + 96 * Texture.UIScale and \
                           item.render_position.y <= position.y <= item.render_position.y + 96 * Texture.UIScale:
                            self.inventory.store_armor(item.item.slot)
                            break

                    if self.weapon_component.render_position.x <= position.x <= self.weapon_component.render_position.x + 96 * Texture.UIScale and \
                       self.weapon_component.render_position.y <= position.y <= self.weapon_component.render_position.y + 96 * Texture.UIScale:
                        self.inventory.store_weapon()

                elif e.button == 3:  # right click
                    for i in range(len(self.misc_components)):
                        if self.misc_components[i].render_position.x <= position.x <= self.misc_components[i].render_position.x + 96 * Texture.UIScale and \
                           self.misc_components[i].render_position.y <= position.y <= self.misc_components[i].render_position.y + 96 * Texture.UIScale:
                            self.inventory.remove_item(i)

    def render(self, surface: Surface) -> None:
        """ Renders the inventory to the screen.

        :param surface: The surface on which the inventory will be rendered.
        """

        self.misc_texture.render(surface, self.render_position)
        self.equipped_texture.render(surface, Position(self.render_position.x + self.misc_texture.get_width(), self.render_position.y))

        for item in self.misc_components:
            item.render(surface)
        for armor in self.armor_components:
            armor.render(surface)
        self.weapon_component.render(surface)


class InventoryLayer(Layer):
    """
    The layer used to display the inventory.
    """
    def __init__(self, player: object, inventory: Inventory, width: int, height: int) -> None:
        """
        :param player: The player who owns the inventory.
        :param inventory: The inventory which will be rendered.
        :param width: The width of the screen.
        :param height: The height of the screen.
        """
        super().__init__(True, width, height)
        self.player = player
        self.inventory_display = InventoryComponent(inventory, self.player, Position(0, 0))
        self.inventory_display.render_position = Position((width - self.inventory_display.render_width) // 2, (height - self.inventory_display.render_height) // 2)
        self.stats_text = TextComponent("resources/font.ttf", 24, (255, 255, 255), Position(self.inventory_display.render_position.x, self.inventory_display.render_position.y - 112), self.inventory_display.render_width, 96)
        self.darkener = DarkenerComponent(Position(0, 0), self.width, self.height)
        self.hint_box = BoxComponent(Position(0, 0), 384, 256)
        self.hint_text = TextComponent("resources/font.ttf", 24, (0, 0, 0), Position(0, 0), 384, 256)

        self.add_component("darkener", self.darkener)
        self.add_component("inventory", self.inventory_display)
        self.add_component("stats", self.stats_text)
        self.add_component("hint_box", self.hint_box)
        self.add_component("hint_text", self.hint_text)
        self.lock_component("hint_box")
        self.lock_component("hint_text")

    def update(self, events: list[event.Event]) -> None:
        """ Updates the inventory layer.

        :param events: A list of the lastly pulled events.
        """
        super().update(events)

        self.stats_text.set_text([
            f"Health: {self.player.health}/{self.player.max_health}",
            f"Exp: level {self.player.exp_level} ({self.player.exp_amount}/{self.player.exp_needed} to level {self.player.exp_level + 1})",
            f"Attack speed: {self.player.speed - self.player.inventory.get_equipped_weight()} ({self.player.speed} - {self.player.inventory.get_equipped_weight()})"
        ])

        for e in events:
            if e.type == MOUSEMOTION:
                mouse_position = Position(mouse.get_pos()[0], mouse.get_pos()[1])

                hovered = False
                for item in self.inventory_display.misc_components:
                    if item.render_position.x <= mouse_position.x <= item.render_position.x + 96 * Texture.UIScale and \
                       item.render_position.y <= mouse_position.y <= item.render_position.y + 96 * Texture.UIScale:
                        lines = [item.item.name, "", f"Weight: {item.item.weight}"]
                        if isinstance(item.item, Weapon):
                            lines.append(f"Damage: {item.item.damage}")
                        elif isinstance(item.item, Armor):
                            lines.append(f"Protection: {item.item.protection}")
                        elif isinstance(item.item, Consumable):
                            lines.append(f"Effects: {', '.join(item.item.effect_names)}")
                        self.hint_text.set_text(lines)

                        self.hint_box.render_position = mouse_position
                        self.hint_text.render_position = mouse_position

                        if self.is_locked("hint_box"):
                            self.unlock_component("hint_box")
                        if self.is_locked("hint_text"):
                            self.unlock_component("hint_text")

                        hovered = True
                        break

                for item in self.inventory_display.armor_components:
                    if item.render_position.x <= mouse_position.x <= item.render_position.x + 96 * Texture.UIScale and \
                       item.render_position.y <= mouse_position.y <= item.render_position.y + 96 * Texture.UIScale:
                        lines = [
                            item.item.name,
                            "",
                            f"Weight: {item.item.weight}",
                            f"Protection: {item.item.protection}",
                            f"Slot: {item.item.slot}"
                        ]
                        self.hint_text.set_text(lines)

                        self.hint_box.render_position = mouse_position
                        self.hint_text.render_position = mouse_position

                        if self.is_locked("hint_box"):
                            self.unlock_component("hint_box")
                        if self.is_locked("hint_text"):
                            self.unlock_component("hint_text")

                        hovered = True
                        break

                if self.inventory_display.weapon_component.render_position.x <= mouse_position.x <= self.inventory_display.weapon_component.render_position.x + 96 * Texture.UIScale and \
                   self.inventory_display.weapon_component.render_position.y <= mouse_position.y <= self.inventory_display.weapon_component.render_position.y + 96 * Texture.UIScale:
                    lines = [
                        self.inventory_display.weapon_component.item.name,
                        "",
                        f"Weight: {self.inventory_display.weapon_component.item.weight}",
                        f"Damage: {self.inventory_display.weapon_component.item.damage}"
                    ]

                    self.hint_text.set_text(lines)

                    self.hint_box.render_position = mouse_position
                    self.hint_text.render_position = mouse_position

                    if self.is_locked("hint_box"):
                        self.unlock_component("hint_box")
                    if self.is_locked("hint_text"):
                        self.unlock_component("hint_text")

                    hovered = True

                if not hovered:
                    if not self.is_locked("hint_box"):
                        self.lock_component("hint_box")
                    if not self.is_locked("hint_text"):
                        self.lock_component("hint_text")

    def render(self, surface: Surface) -> None:
        """ Renders the inventory layer.

        :param surface: The surface on which the inventory layer will be rendered.
        """
        super().render(surface)
