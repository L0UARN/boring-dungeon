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
    def __init__(self, max_health: int, position: Position, direction: Direction, graph: dict[Position, list[Position]], rng: Random) -> None:
        """
        :param max_health: The maximum amount of health the enemy can have.
        :param position: The initial position of the enemy.
        :param direction: The initial direction of the enemy.
        :param graph: The graph on which the enemy will move.
        :param rng: The random numbers generator used for the 'AI' of the enemy.
        """
        Fighter.__init__(self, max_health)
        Mobile.__init__(self, position, direction, graph)
        Affectible.__init__(self)

        self.rng = rng
        self.destination = self.rng.choice(list(self.graph.keys()))
        self.last_moved = time()
        self.taking_break = False
        self.last_break_update = time()
        self.break_start = 0
        self.has_target = False
        self.ai_locked = False

    def update_ai(self) -> None:
        """
        Updates the enemy's behavior.
        """
        if self.ai_locked:
            return

        if self.has_target:
            if time() - self.last_moved >= 0.25:
                self.move_towards(self.destination)
                self.last_moved = time()
        elif self.taking_break:
            if time() - self.last_break_update >= 0.50:
                self.direction = self.rng.choice(self.direction.possible_turns())
                if self.rng.random() < (time() - self.break_start) / 4:
                    self.taking_break = False
                    self.last_moved = time()
                    self.destination = self.rng.choice(list(self.graph.keys()))
                self.last_break_update = time()
        elif time() - self.last_moved >= 0.40:
            if self.position == self.destination:
                self.taking_break = True
                self.break_start = time()
                self.last_break_update = time()
            elif not self.move_towards(self.destination):
                self.direction = self.rng.choice(self.direction.possible_turns())
                self.destination = self.rng.choice(list(self.graph.keys()))
            self.last_moved = time()


class EnemyComponent(Component):
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

    def update(self, events: list[event.Event]) -> None:
        """ Updates the enemy.

        :param events: A list of the lastly pulled events.
        """
        self.enemy.update_ai()

    def render(self, surface: Surface) -> None:
        """ Renders the enemy.

        :param surface: The surface on which the enemy will be rendered.
        """
        self.enemy_texture.render(surface, self.render_position, self.enemy.direction)
