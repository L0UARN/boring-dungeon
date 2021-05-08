"""
Classes:
    - Player
    - PlayerComponent
"""

from time import time
import pygame as pg
from source.traits.living import Living
from source.traits.mobile import Mobile
from source.traits.effect import Affectible
from source.core.tools import Position, Direction
from source.core.component import Component
from source.resources import TEXTURES as T


class Player(Living, Mobile, Affectible):
    """
    The representation of the player in the game.
    """
    def __init__(self, max_health: int, position: Position, direction: Direction, graph: dict[Position, [Position]]) -> None:
        Living.__init__(self, max_health)
        Mobile.__init__(self, position, direction, graph)
        Affectible.__init__(self)


class PlayerComponent(Component):
    """
    Contains a player.
    """
    def __init__(self, player: Player, render_position: Position, render_width: int, render_height: int) -> None:
        super().__init__(render_position, render_width, render_height)

        self.player = player
        self.last_moved = 0

        self.player_texture = T.get("player")

    def update(self, events: list[pg.event.Event]) -> None:
        pressed = pg.key.get_pressed()
        if time() - self.last_moved >= 0.20:
            if pressed[pg.K_w] or pressed[pg.K_UP]:
                self.player.step_in_direction(Direction.NORTH)
                self.last_moved = time()
            elif pressed[pg.K_d] or pressed[pg.K_RIGHT]:
                self.player.step_in_direction(Direction.EAST)
                self.last_moved = time()
            elif pressed[pg.K_s] or pressed[pg.K_DOWN]:
                self.player.step_in_direction(Direction.SOUTH)
                self.last_moved = time()
            elif pressed[pg.K_a] or pressed[pg.K_LEFT]:
                self.player.step_in_direction(Direction.WEST)
                self.last_moved = time()

    def render(self, surface: pg.Surface) -> None:
        self.player_texture.render(surface, self.render_position, self.player.direction)
