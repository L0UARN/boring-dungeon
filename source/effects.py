"""
Classes:
    - EffectBook
    - HealingEffect
Constants:
    - EFFECTS
"""

from copy import deepcopy

from pygame import event

from source.traits.effect import Effect
from source.traits.living import Living


class EffectBook:
    """
    A registry of every existing effects.
    """
    def __init__(self) -> None:
        self.effects: dict[str, Effect] = {}

    def add(self, name: str, effect: Effect) -> None:
        """ Adds an effect to the book.

        :param name: The name of the effect to register.
        :param effect: The effect to register.
        """
        self.effects[name] = effect

    def get(self, name: str) -> Effect:
        """ Get an effect registered in the book.

        :param name: The name of the effect.
        :return: The effect of the desired name.
        """
        return deepcopy(self.effects[name])


EFFECTS = EffectBook()


class HealingEffect(Effect):
    """
    An effect which heals an entity
    """
    def __init__(self, target: Living):
        super().__init__(target)
        self.done = False

    def update(self, events: list[event.Event]) -> None:
        if not self.done:
            self.target.heal(5)
            self.done = True

    def should_fade(self) -> bool:
        return self.done


class SpeedEffect(Effect):
    """
    An effect which adds speed to a fighter.
    """
    def __init__(self, target):
        super().__init__(target)
        self.done = False

    def update(self, events: list[event.Event]) -> None:
        if not self.done:
            self.target.speed += 1
            self.done = True

    def should_fade(self) -> bool:
        return self.done


EFFECTS.add("healing", HealingEffect(None))
EFFECTS.add("speed", SpeedEffect(None))
