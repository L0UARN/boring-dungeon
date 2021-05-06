"""
Classes:
    - Living
"""


class Living:
    """
    A living is an entity which has health, can be damaged and is capable of healing.
    """
    def __init__(self, max_health: int) -> None:
        """
        :param max_health: The maximum amount of health the entity can have.
        """
        self.max_health = max_health
        self.health = max_health

    def damage(self, amount: int) -> None:
        """ Damages the entity (subtracts health).

        :param amount: The amount of damage that will be dealt to the entity.
        """
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount: int) -> None:
        """ Heal the entity (adds health).

        :param amount: The amount of health that will be healed to the entity.
        """
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def is_dead(self) -> bool:
        """ Get if the entity is dead or not.

        :return: True if the entity is at 0 health or below, or False if not.
        """
        return self.health <= 0
