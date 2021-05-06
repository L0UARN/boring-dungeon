"""
Classes:
    Level
    LevelComponent
"""

from source.rng_threads import GENERATION as rng
from source.core.tools import Position, Direction


class Level:
    """
    A level is the maze-exploration part of the game. It contains a navigable graph, rooms, and
    stairs to go down a level.
    """
    def __init__(self, difficulty: int) -> None:
        """
        :param difficulty: How complex the level is to navigate.
        """
        self.difficulty = difficulty
        self.graph: dict[Position, list[Position]] = {}
        self.rooms: list[Position] = []
        self.stairs: list[Position] = []

        self.generate()

    def generate(self) -> None:
        """
        Generates the level's maze and its content.
        """
        self._generate_maze(Position(0, 0), Direction.NORTH, 8 + self.difficulty * 4)
        self._generate_rooms()
        self._generate_stairs()

    def _generate_maze(self, start: Position, direction: Direction, length: int) -> None:
        """ Generates recursively the level's maze.

        :param start: The position at which the rng process should start (or continue).
        :param direction: The direction in which the rng is going to continue.
        :param length: The amount of steps left in the grid the path can take.
        """
        if length == 0:
            return

        if start not in self.graph:
            self.graph[start] = []

        continued_direction = direction
        continued_position = start.next_in_direction(direction)

        if start.x % 2 == 0 and start.y % 2 == 0:
            if rng.random() < 0.25:
                continued_direction = rng.choice(continued_direction.possible_turns())
                continued_position = start.next_in_direction(continued_direction)
            elif rng.random() < 0.10:
                new_path_direction = rng.choice(continued_direction.possible_turns())
                new_path_position = start.next_in_direction(new_path_direction)

                if new_path_position not in self.graph:
                    self.graph[new_path_position] = []
                if new_path_position not in self.graph[start]:
                    self.graph[start].append(new_path_position)
                if start not in self.graph[new_path_position]:
                    self.graph[new_path_position].append(start)

                self._generate_maze(new_path_position, new_path_direction, length - 1)

        if continued_position not in self.graph:
            self.graph[continued_position] = []
        if continued_position not in self.graph[start]:
            self.graph[start].append(continued_position)
        if start not in self.graph[continued_position]:
            self.graph[continued_position].append(start)

        self._generate_maze(continued_position, continued_direction, length - 1)

    def _generate_rooms(self) -> None:
        """
        Chooses rooms positions inside of the level's maze.
        """
        best_positions: list[Position] = []
        possible_positions: list[Position] = []

        for position in self.graph:
            if position == Position(0, 0):
                continue
            elif len(self.graph[position]) >= 3:
                best_positions.append(position)
            elif len(self.graph[position]) == 2 and position.x % 2 == 0 and position.y % 2 == 0:
                possible_positions.append(position)

        if not best_positions:
            if len(possible_positions) > self.difficulty:
                self.rooms = rng.sample(possible_positions, self.difficulty)
            else:
                self.rooms = possible_positions
        elif len(best_positions) < self.difficulty:
            if len(best_positions) + len(possible_positions) > self.difficulty:
                self.rooms = best_positions + rng.sample(
                    possible_positions,
                    self.difficulty - len(best_positions)
                )
            else:
                self.rooms = best_positions + possible_positions
        elif len(best_positions) > self.difficulty:
            self.rooms = rng.sample(best_positions, self.difficulty)
        else:  # len(best_positions) == self.difficulty
            self.rooms = best_positions

    def _generate_stairs(self) -> None:
        """
        Places stairs in random dead-ends of the level's maze.
        """
        dead_ends = []
        for position in self.graph:
            if position == Position(0, 0):
                continue
            elif len(self.graph[position]) == 1:
                dead_ends.append(position)

        if len(dead_ends) == 1 or len(dead_ends) == 2:
            self.stairs = dead_ends
        else:  # len(dead_ends) > 2
            self.stairs = rng.sample(dead_ends, 2)
