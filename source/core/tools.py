""" A collection of general tools used in the game.

Classes:
    - Direction
    - Position
"""

from __future__ import annotations
from enum import Enum


class Direction(Enum):
    """
    Represents a cardinal direction.
    """
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        if self == Direction.NORTH:
            return "North"
        elif self == Direction.EAST:
            return "East"
        elif self == Direction.SOUTH:
            return "South"
        elif self == Direction.WEST:
            return "West"

    def opposite(self) -> Direction:
        """Get the opposite direction of the current one.

        :return: a Direction equal to the opposite direction of self.
        """
        return Direction((self.value + 2) % 4)

    def possible_turns(self) -> list[Direction]:
        """Get a list of the possible turns one can make from the current direction.

        :return: A list of the 2 directions corresponding to a 90 degrees turn from self.
        """
        return [Direction((self.value + 1) % 4), Direction((self.value + 3) % 4)]


class Position:
    """
    Represents a position inside of a grid.
    """
    def __init__(self, x: int, y: int) -> None:
        """
        :param x: the x coordinate of the position.
        :param y: the y coordinate of the position.
        """
        self.x = x
        self.y = y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other: Position) -> int:
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"({self.x};{self.y})"

    def next_in_direction(self, direction: Direction) -> Position:
        """ Get the next position in a given direction.

        :param direction: The direction in which the next position will be determined.
        :return: The position 1 step away from self in the specified direction.
        """
        if direction == Direction.NORTH:
            return Position(self.x, self.y - 1)
        elif direction == Direction.EAST:
            return Position(self.x + 1, self.y)
        elif direction == Direction.SOUTH:
            return Position(self.x, self.y + 1)
        else:  # direction == Direction.WEST
            return Position(self.x - 1, self.y)

    def direction(self, other: Position) -> Direction:
        """ Get the direction in which the other is.

        :param other: Another position.
        :return: The direction of the other position relative to self.
        """
        x_difference = self.x - other.x
        y_difference = self.y - other.y

        if abs(x_difference) >= abs(y_difference):
            if x_difference >= 0:
                return Direction.EAST
            else:
                return Direction.WEST
        else:
            if y_difference >= 0:
                return Direction.SOUTH
            else:
                return Direction.NORTH
