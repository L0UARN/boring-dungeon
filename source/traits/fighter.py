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
    def __init__(self, max_health: int, speed: int) -> None:
        """
        :param max_health: The maximum amount of health the fighter entity can have.
        :param speed: The initial speed of the fighter.
        """
        super().__init__(max_health)
        self.inventory = Inventory()
        self.speed = speed
        self.attack_speed: float
        if self.speed - self.inventory.get_equipped_weight() <= 0:
            self.attack_speed = 1
        else:
            self.attack_speed = 1 / (self.speed - self.inventory.get_equipped_weight())
        self.last_attack = 0
        self.blocking = False

    def damage(self, amount: int) -> None:
        """ Damages the entity, accounting for the equipped armor.

        :param amount: The amount of damage to deal.
        """
        if self.blocking:
            amount -= self.inventory.get_protection() * 2
        else:
            amount -= self.inventory.get_protection()
        if amount <= 0:
            amount = 1

        super().damage(amount)

    def attack(self, target: Fighter) -> bool:
        """ Deal damage to another fighter.

        :param target: The fighter to deal damage to.
        :return: True if the attack succeeded, False if not.
        """
        if self.speed - self.inventory.get_equipped_weight() <= 0:
            self.attack_speed = 1
        else:
            self.attack_speed = 1 / (self.speed - self.inventory.get_equipped_weight())

        if time() - self.last_attack >= self.attack_speed:
            if self.inventory.get_weapon() is None:
                target.damage(1)
            else:
                target.damage(self.inventory.get_weapon().damage)

            self.last_attack = time()
            return True
        return False
