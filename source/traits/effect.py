"""
Classes:
    - Effect
    - Affectible
"""

from abc import abstractmethod
from pygame import event


class Effect:
    """
    An effect to be applied to an affectible entity.
    """
    def __init__(self, target, source: object = None) -> None:
        """
        :param target: The affectible entity which receives the effect.
        :param source: The optional entity which sent the effect to the target.
        """
        self.target = target
        self.source = source

    @abstractmethod
    def update(self, events: list[event.Event]) -> None:
        """ Trigger (or not) what the effect does.

        :param events: The list of events lastly pulled.
        """
        pass

    @abstractmethod
    def should_fade(self) -> bool:
        """ Get if the effect should be removed from the affectible entity's list of effects.

        :return: True if the effect should end, False if not.
        """
        pass


class Affectible:
    """
    An affectible entity is an entity capable of receiving effects.
    """
    def __init__(self) -> None:
        self.effects: list[Effect] = []

    def apply_effect(self, effect: Effect) -> None:
        """ Adds an effect to the entity.

        :param effect: The effect to be added.
        """
        self.effects.append(effect)

    def update(self, events: list[event.Event]) -> None:
        """ Updates every events attached to the entity, and removes the ones which faded away.

        :param events: The list of events lastly pulled.
        """
        faded_effects: list[Effect] = []
        for effect in self.effects:
            effect.update(events)
            if effect.should_fade():
                faded_effects.append(effect)

        for faded in faded_effects:
            self.effects.remove(faded)
