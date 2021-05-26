"""
Classes:
    - Enemy
    - EnemyComponent
"""

from time import time
from random import Random
from pygame import Surface, event
from source.traits.fighter import Fighter
from source.traits.mobile import Mobile
from source.traits.effect import Affectible
from source.core.tools import Position, Direction
from source.core.component import Component
from source.resources import TEXTURES as T


class Enemy(Fighter, Mobile, Affectible):
    """
    An enemy found in the dungeon.
    """
    def __init__(self, max_health: int, speed: int, position: Position, direction: Direction, graph: dict[Position, list[Position]], rng: Random) -> None:
        """
        :param max_health: The maximum amount of health the enemy can have.
        :param speed: The attack speed of the enemy.
        :param position: The initial position of the enemy.
        :param direction: The initial direction of the enemy.
        :param graph: The graph on which the enemy will move.
        :param rng: The random numbers generator used for the 'AI' of the enemy.
        """
        Fighter.__init__(self, max_health, speed)
        Mobile.__init__(self, position, direction, graph)
        Affectible.__init__(self)

        self.rng = rng


class RoamingEnemyComponent(Component):
    """
    Contains an enemy.
    """
    def __init__(self, enemy: Enemy, render_position: Position) -> None:
        """
        :param enemy: The enemy to update and render.
        :param render_position: The position to which the enemy will be rendered.
        """
        self.enemy_texture = T.get("enemy")
        super().__init__(render_position, self.enemy_texture.get_width(), self.enemy_texture.get_height())
        self.enemy = enemy

        self.destination = self.enemy.rng.choice(list(self.enemy.graph.keys()))
        self.last_moved = time()
        self.taking_break = False
        self.last_break_update = time()
        self.break_start = 0
        self.has_target = False
        self.ai_locked = False

    def update(self, events: list[event.Event]) -> None:
        """ Updates the enemy.

        :param events: A list of the lastly pulled events.
        """
        if self.ai_locked:
            return

        if self.has_target:
            if time() - self.last_moved >= 0.25:
                self.enemy.move_towards(self.destination)
                self.last_moved = time()
        elif self.taking_break:
            if time() - self.last_break_update >= 0.50:
                self.enemy.direction = self.enemy.rng.choice(self.enemy.direction.possible_turns())
                if self.enemy.rng.random() < (time() - self.break_start) / 4:
                    self.taking_break = False
                    self.last_moved = time()
                    self.destination = self.enemy.rng.choice(list(self.enemy.graph.keys()))
                self.last_break_update = time()
        elif time() - self.last_moved >= 0.40:
            if self.enemy.position == self.destination:
                self.taking_break = True
                self.break_start = time()
                self.last_break_update = time()
            elif not self.enemy.has_path(self.destination):
                self.enemy.direction = self.enemy.rng.choice(self.enemy.direction.possible_turns())
                self.destination = self.enemy.rng.choice(list(self.enemy.graph.keys()))
            else:
                self.enemy.move_towards(self.destination)
            self.last_moved = time()

        self.enemy.update_effects(events)

    def render(self, surface: Surface) -> None:
        """ Renders the enemy.

        :param surface: The surface on which the enemy will be rendered.
        """
        self.enemy_texture.render(surface, self.render_position, self.enemy.direction)


class FightingEnemyComponent(Component):
    """
    An enemy's representation while in combat.
    """
    def __init__(self, enemy: Enemy, target: Fighter, render_position: Position):
        self.fighting_texture = T.get("enemy_fighting")
        self.blocking_texture = T.get("enemy_fighting_blocking")
        super().__init__(render_position, self.fighting_texture.get_width(), self.fighting_texture.get_height())
        self.enemy = enemy
        self.target = target
        self.can_attack = True

        self.delay = self.enemy.rng.random() / 4
        self.last_action = 0
        self.block_chance = 0.25 if self.enemy.speed > self.enemy.inventory.get_protection() else 0.50
        self.block_time = 0
        self.block_length = 1.0 if self.enemy.speed > self.enemy.inventory.get_protection() else 2.0

    def update(self, events: list[event.Event]) -> None:
        if self.can_attack and time() - self.enemy.last_attack >= self.enemy.attack_speed + self.delay:
            if self.enemy.blocking:
                if time() - self.block_time >= self.block_length + self.delay:
                    self.enemy.blocking = False
                    self.last_action = 1
            elif self.last_action == 1:
                if self.enemy.attack(self.target):
                    self.last_action = 0
            else:
                if self.enemy.rng.random() < self.block_chance:
                    self.enemy.blocking = True
                    self.block_time = time()
                elif self.enemy.attack(self.target):
                    self.last_action = 0

        self.enemy.update_effects(events)

    def render(self, surface: Surface) -> None:
        if self.enemy.blocking:
            self.blocking_texture.render(surface, self.render_position)
        else:
            self.fighting_texture.render(surface, self.render_position)
