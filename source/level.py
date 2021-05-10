"""
Classes:
    - Level
    - LevelComponent
    - LevelLayer
"""

from random import Random
from math import ceil, floor
from pygame import Surface, event
from source.core.tools import Position, Direction
from source.core.component import Component
from source.core.texture import TILE_SIZE
from source.resources import TEXTURES as T
from source.core.layer import Layer
from source.player import Player, PlayerComponent
from source.ui.halo import HaloComponent
from source.ui.box import BoxComponent
from source.ui.text import TextComponent


class Level:
    """
    A level is the maze-exploration part of the game. It contains a navigable graph, rooms, and stairs to go down a
    level.
    """
    def __init__(self, difficulty: int, rng: Random) -> None:
        """
        :param difficulty: How complex the level is to navigate.
        :param rng: The random number generator used the generation process.
        """
        self.difficulty = difficulty
        self.rng = rng

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
            if self.rng.random() < 0.25:
                continued_direction = self.rng.choice(continued_direction.possible_turns())
                continued_position = start.next_in_direction(continued_direction)
            elif self.rng.random() < 0.10:
                new_path_direction = self.rng.choice(continued_direction.possible_turns())
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
                self.rooms = self.rng.sample(possible_positions, self.difficulty)
            else:
                self.rooms = possible_positions
        elif len(best_positions) < self.difficulty:
            if len(best_positions) + len(possible_positions) > self.difficulty:
                self.rooms = best_positions + self.rng.sample(possible_positions, self.difficulty - len(best_positions))
            else:
                self.rooms = best_positions + possible_positions
        elif len(best_positions) > self.difficulty:
            self.rooms = self.rng.sample(best_positions, self.difficulty)
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

        if 1 <= len(dead_ends) <= 2:
            self.stairs = dead_ends
        elif len(dead_ends) > 2:
            self.stairs = self.rng.sample(dead_ends, 2)
        else:
            self.stairs = [self.rng.choice(list(self.graph.keys())[1:])]


class LevelComponent(Component):
    """
    Contains a level.
    """
    def __init__(self, level: Level, center: Position, render_position: Position, render_width: int, render_height: int) -> None:
        """
        :param level: The level to display.
        :param render_position: The position on the surface on which the component has to be rendered.
        :param render_width: A hint to the width of the rendered component.
        :param render_height: A hint to the height of the rendered component.
        """
        super().__init__(render_position, render_width, render_height)

        self.level: Level = level
        self.center: Position = center

        self.room_texture = T.get("room")
        self.stairs_texture = T.get("stairs")
        self.floor_texture = T.get("floor")
        self.brick_texture = T.get("brick")
        print("brick", self.brick_texture.get_width())

    def update(self, events: list[event.Event]) -> None:
        """ Updates the level with the latest events.

        :param events: The list of the lastly pulled events.
        """
        pass

    def render(self, surface: Surface) -> None:
        """ Renders the level to the specified surface.

        :param surface: The surface on which to render the level.
        """
        width_blocks: int = ceil(self.render_width / TILE_SIZE)
        if width_blocks % 2 == 0:
            width_blocks += 1
        height_blocks: int = ceil(self.render_height / TILE_SIZE)
        if height_blocks % 2 == 0:
            height_blocks += 1

        offset_x = self.render_position.x - (width_blocks * TILE_SIZE - self.render_width) // 2
        offset_y = self.render_position.y - (height_blocks * TILE_SIZE - self.render_height) // 2

        for x in range(self.center.x - floor(width_blocks / 2), self.center.x + ceil(width_blocks / 2)):
            for y in range(self.center.y - floor(height_blocks / 2), self.center.y + ceil(height_blocks / 2)):
                if Position(x, y) in self.level.rooms:
                    self.room_texture.render(surface, Position(offset_x, offset_y))
                elif Position(x, y) in self.level.stairs:
                    self.stairs_texture.render(
                        surface,
                        Position(offset_x, offset_y),
                        Position(x, y).direction(self.level.graph[Position(x, y)][0]).opposite()
                    )
                elif Position(x, y) in self.level.graph:
                    self.floor_texture.render(surface, Position(offset_x, offset_y))
                else:
                    self.brick_texture.render(surface, Position(offset_x, offset_y))

                offset_y += TILE_SIZE
            offset_y = self.render_position.y - (height_blocks * TILE_SIZE - self.render_height) // 2
            offset_x += TILE_SIZE


class LevelLayer(Layer):
    """
    A layer containing all the components that makes up the level exploring part of the game.
    """
    def __init__(self, level: Level, player: Player, width: int, height: int) -> None:
        """
        :param level: The level which will be displayed.
        :param player: The player exploring the level.
        :param width: The width of the render area.
        :param height: The height of the render area.
        """
        super().__init__(False, width, height)
        self.level_display = LevelComponent(level, list(level.graph.keys())[0], Position(0, 0), width, height)
        self.player_display = PlayerComponent(player, Position((width - TILE_SIZE) // 2, (height - TILE_SIZE) // 2), TILE_SIZE, TILE_SIZE)
        self.halo_effect = HaloComponent(Position(0, 0), width, height)
        self.info_box = BoxComponent(Position(0, int(height * 0.75)), width, int(height * 0.25))
        self.info_text = TextComponent("resources/font.ttf", 32, (0, 0, 0), Position(0, int(height * 0.75)), width, int(height * 0.25), True, 16.0)

    def update(self, events: list[event.Event]) -> None:
        """ Updates the layer.

        :param events: A list of the lastly pulled events.
        """
        super().update(events)
        self.level_display.update(events)
        self.player_display.update(events)
        self.level_display.center = self.player_display.player.position
        self.halo_effect.update(events)
        self.info_box.update(events)
        self.info_text.update(events)

    def render(self, surface: Surface) -> None:
        """ Renders the layer to the specified surface.

        :param surface: The surface on which the layer will be rendered.
        """
        super().render(surface)
        self.level_display.render(surface)
        self.player_display.render(surface)
        self.halo_effect.render(surface)
        self.info_box.render(surface)
        self.info_text.render(surface)
