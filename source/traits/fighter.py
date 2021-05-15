"""
Classes:
    - Fighter
"""

from __future__ import annotations
from time import time
from source.traits.living import Living
from source.inventory import Inventory


class Fighter(Living):
    """
    A fighter is a living entity that can fight. It has an inventory.
    """
    def __init__(self, max_health: int) -> None:
        """
        :param max_health: The maximum amount of health the fighter entity can have.
        """
        super().__init__(max_health)
        self.inventory = Inventory()
        self.last_attack = 0

    def damage(self, amount: int) -> None:
        """ Damages the entity, accounting for the equipped armor.

        :param amount: The amount of damage to deal.
        """
        amount -= self.inventory.get_protection()
        if amount <= 0:
            amount = 1

        super().damage(amount)

    def attack(self, target: Fighter) -> None:
        """ Deal damage to another fighter.

        :param target: The fighter to deal damage to.
        """
        if time() - self.last_attack >= self.inventory.get_equipped_weight() * 0.1:
            if self.inventory.get_weapon() is None:
                target.damage(1)
            else:
                target.damage(self.inventory.get_weapon().damage)

            self.last_attack = time()
