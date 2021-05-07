"""
Classes:
    - Room
    - RoomComponent
"""

from random import Random
from math import ceil, floor
from pygame import event, Surface
from source.core.tools import Position, Direction
from source.core.component import Component
from source.core.textures import TILE_SIZE
from source.resources import TEXTURES as T


class Room:
    """
    Rooms are placed inside of levels, they contain items to loot and ennemies to fight.
    """
    def __init__(self, difficulty: int, rng: Random, openings: list[Direction]) -> None:
        """
        :param difficulty: How complex and big the room is.
        :param rng: The random number generator used the generation process.
        """
        self.difficulty = difficulty
        self.rng = rng

        self.graph: dict[Position, list[Position]] = {}
        self.doors: list[tuple[Position, Direction]] = [(Position(0, 0), d) for d in openings]
        self.width = 0
        self.height = 0

        self.generate()

    def generate(self) -> None:
        """
        Generates the room and its content.
        """
        self._generate_room()
        self._generate_doors()

    def _generate_room(self) -> None:
        """
        Generates an empty room.
        """
        self.width = self.rng.randint(8, 8 + self.difficulty * 4)
        self.height = self.rng.randint(8, 8 + self.difficulty * 4)

        for x in range(self.width):
            for y in range(self.height):
                if Position(x, y) not in self.graph:
                    self.graph[Position(x, y)] = []

                if y != 0:
                    self.graph[Position(x, y)].append(Position(x, y).next_in_direction(Direction.NORTH))
                if x != self.width - 1:
                    self.graph[Position(x, y)].append(Position(x, y).next_in_direction(Direction.EAST))
                if y != self.height - 1:
                    self.graph[Position(x, y)].append(Position(x, y).next_in_direction(Direction.SOUTH))
                if x != 0:
                    self.graph[Position(x, y)].append(Position(x, y).next_in_direction(Direction.WEST))

        deletions = self.rng.sample(list(self.graph.keys()), self.difficulty ** 2)
        for deletion in deletions:
            if deletion.x > 0 and deletion.x < self.width - 1:
                if deletion.y > 0 and deletion.y < self.height - 1:
                    for direction in Direction:
                        if deletion.next_in_direction(direction) in self.graph:
                            self.graph[deletion.next_in_direction(direction)].remove(deletion)
                    self.graph.pop(deletion)


    def _generate_doors(self) -> None:
        """
        Generates the exits on the sides of the room.
        """
        for i in range(len(self.doors)):
            if self.doors[i][1] == Direction.NORTH:
                self.doors[i] = (Position(self.rng.randint(0, self.width - 1), -1), self.doors[i][1])
            elif self.doors[i][1] == Direction.EAST:
                self.doors[i] = (Position(self.width, self.rng.randint(0, self.height - 1)), self.doors[i][1])
            elif self.doors[i][1] == Direction.SOUTH:
                self.doors[i] = (Position(self.rng.randint(0, self.width - 1), self.height), self.doors[i][1])
            elif self.doors[i][1] == Direction.WEST:
                self.doors[i] = (Position(-1, self.rng.randint(0, self.height - 1)), self.doors[i][1])

            self.graph[self.doors[i][0]] = [self.doors[i][0].next_in_direction(self.doors[i][1].opposite())]
            self.graph[self.doors[i][0].next_in_direction(self.doors[i][1].opposite())].append(self.doors[i][0])


class RoomComponent(Component):
    """
    Contains a room.
    """
    def __init__(self, room: Room, center: Position, render_position: Position, render_width: int, render_height: int):
        """
        :param room: The room to display.
        :param render_position: The position on the surface on which the component has to be rendered.
        :param render_width: A hint to the width of the rendered component.
        :param render_height: A hint to the height of the rendered component.
        """
        super().__init__(render_position, render_width, render_height)

        self.room = room
        self.center = center

    def update(self, events: list[event.Event]) -> None:
        pass

    def render(self, surface: Surface) -> None:
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
                is_door = False
                for door in self.room.doors:
                    if Position(x, y) == door[0]:
                        T.get("door").render_direction(
                            surface, Position(offset_x, offset_y),
                            door[1]
                        )
                        is_door = True
                        break

                if not is_door and Position(x, y) in self.room.graph:
                    T.get("floor").render(surface, Position(offset_x, offset_y))
                elif not is_door:
                    T.get("brick").render(surface, Position(offset_x, offset_y))

                offset_y += TILE_SIZE
            offset_y = self.render_position.y - (height_blocks * TILE_SIZE - self.render_height) // 2
            offset_x += TILE_SIZE