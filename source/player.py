"""
Classes:
    - Player
    - PlayerComponent
"""

from time import time
import pygame as pg
from pygame import Surface, event

from source.traits.fighter import Fighter
from source.traits.mobile import Mobile
from source.traits.effect import Affectible
from source.core.tools import Position, Direction
from source.core.component import Component
from source.resources import TEXTURES as T


class Player(Fighter, Mobile, Affectible):
    """
    The representation of the player in the game.
    """
    def __init__(self, max_health: int, speed: int, position: Position, direction: Direction, graph: dict[Position, list[Position]]) -> None:
        """
        :param max_health: The maximum amount of health the player can have.
        :param speed: The base attack speed of the player.
        :param position: The initial position of the player.
        :param direction: The initial direction of the player.
        :param graph: The graph on which the player will move.
        """
        Fighter.__init__(self, max_health, speed)
        Mobile.__init__(self, position, direction, graph)
        Affectible.__init__(self)


class ExploringPlayerComponent(Component):
    """
    Contains a player.
    """
    def __init__(self, player: Player, render_position: Position) -> None:
        """
        :param player: The player to display.
        :param render_position: The position where the player has to be displayed.
        """
        self.player_texture = T.get("player")
        super().__init__(render_position, self.player_texture.get_width(), self.player_texture.get_height())

        self.player = player
        self.last_moved = 0
        self.movement_locked = False

    def update(self, events: list[pg.event.Event]) -> None:
        """ Updates the player to react to movement keys.

        :param events: A list of the lastly pulled events.
        """
        if self.movement_locked:
            return

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
        """ Renders the player on the specified surface.

        :param surface: The surface on which the player will be rendered.
        """
        self.player_texture.render(surface, self.render_position, self.player.direction)


class FightingPlayerComponent(Component):
    """
    The player's representation while in combat.
    """
    def __init__(self, player: Player, target: Fighter, render_position: Position):
        self.fighting_texture = T.get("player_fighting")
        self.blocking_texture = T.get("player_fighting_blocking")
        super().__init__(render_position, self.fighting_texture.get_width(), self.fighting_texture.get_height())
        self.player = player
        self.target = target
        self.can_attack = True

    def update(self, events: list[event.Event]) -> None:
        for e in events:
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1 and self.can_attack and not self.player.blocking:
                    self.player.attack(self.target)

        if pg.mouse.get_pressed(3)[2] and time() - self.player.last_attack >= 0.75:
            self.player.blocking = True
        else:
            self.player.blocking = False

    def render(self, surface: Surface) -> None:
        if self.player.blocking:
            self.blocking_texture.render(surface, self.render_position)
        else:
            self.fighting_texture.render(surface, self.render_position)
