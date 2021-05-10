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
from source.core.texture import TILE_SIZE
from source.resources import TEXTURES as T
from source.core.layer import Layer
from source.player import Player, PlayerComponent
from source.ui.halo import HaloComponent
from source.ui.box import BoxComponent
from source.ui.text import TextComponent


class Room:
    """
    Rooms are placed inside of levels, they contain items to loot and enemies to fight.
    """
    def __init__(self, difficulty: int, rng: Random, openings: list[Direction]) -> None:
        """
        :param difficulty: How complex and big the room is.
        :param rng: The random number generator used the generation process.
        """
        self.difficulty = difficulty
        self.rng = rng

        self.width = 0
        self.height = 0
        self.graph: dict[Position, list[Position]] = {}

        self.openings = openings
        self.doors: dict[Position, Direction] = {}

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
        self.width = self.rng.randint(8, 8 + self.difficulty * 2)
        self.height = self.rng.randint(8, 8 + self.difficulty * 2)

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

        deletions = self.rng.sample(list(self.graph.keys()), self.rng.randint(int(self.width * self.height * 0.10), int(self.width * self.height * 0.50)))
        for deletion in deletions:
            if 0 < deletion.x < self.width - 1 and 0 < deletion.y < self.height - 1:
                for direction in Direction:
                    if deletion.next_in_direction(direction) in self.graph:
                        self.graph[deletion.next_in_direction(direction)].remove(deletion)
                self.graph.pop(deletion)

    def _generate_doors(self) -> None:
        """
        Generates the exits on the sides of the room.
        """
        for opening in self.openings:
            position = Position(0, 0)
            if opening == Direction.NORTH:
                position = Position(self.rng.randint(0, self.width - 1), -1)
            elif opening == Direction.EAST:
                position = Position(self.width, self.rng.randint(0, self.height - 1))
            elif opening == Direction.SOUTH:
                position = Position(self.rng.randint(0, self.width - 1), self.height)
            elif opening == Direction.WEST:
                position = Position(-1, self.rng.randint(0, self.height - 1))

            self.doors[position] = opening
            self.graph[position] = [position.next_in_direction(opening.opposite())]
            self.graph[position.next_in_direction(opening.opposite())].append(position)


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

        self.door_texture = T.get("door")
        self.floor_texture = T.get("floor")
        self.brick_texture = T.get("brick")

    def update(self, events: list[event.Event]) -> None:
        """ Updates the room with the latest events.

        :param events: The list of the lastly pulled events.
        """
        pass

    def render(self, surface: Surface) -> None:
        """ Renders the room on the specified surface.

        :param surface: The surface on which to render the room.
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
                if Position(x, y) in self.room.doors:
                    self.door_texture.render(
                        surface,
                        Position(offset_x, offset_y),
                        Position(x, y).direction(self.room.graph[Position(x, y)][0])
                    )
                elif Position(x, y) in self.room.graph:
                    self.floor_texture.render(surface, Position(offset_x, offset_y))
                else:
                    self.brick_texture.render(surface, Position(offset_x, offset_y))

                offset_y += TILE_SIZE
            offset_y = self.render_position.y - (height_blocks * TILE_SIZE - self.render_height) // 2
            offset_x += TILE_SIZE


class RoomLayer(Layer):
    """
    A layer that contains every component related to the room exploring part of the game.
    """
    def __init__(self, room: Room, player: Player, width: int, height: int) -> None:
        """
        :param room: The room which will be displayed.
        :param player: The player exploring the room.
        :param width: The width of the render area.
        :param height: The height of the render area.
        """
        super().__init__(False, width, height)
        self.room_display = RoomComponent(room, list(room.graph.keys())[0], Position(0, 0), width, height)
        self.player_display = PlayerComponent(player, Position((width - TILE_SIZE) // 2, (height - TILE_SIZE) // 2), TILE_SIZE, TILE_SIZE)
        self.halo_effect = HaloComponent(Position(0, 0), width, height)
        self.info_box = BoxComponent(Position(0, int(height * 0.75)), width, int(height * 0.25))
        self.info_text = TextComponent("resources/font.ttf", 32, (0, 0, 0), Position(0, int(height * 0.75)), width, int(height * 0.25), True, 16.0)

    def update(self, events: list[event.Event]) -> None:
        """ Updates the layer.

        :param events: A list of the lastly pulled events.
        """
        super().update(events)
        self.room_display.update(events)
        self.player_display.update(events)
        self.room_display.center = self.player_display.player.position
        self.halo_effect.update(events)
        self.info_box.update(events)
        self.info_text.update(events)

    def render(self, surface: Surface) -> None:
        """ Renders the layer to the specified surface.

        :param surface: The surface on which the layer will be rendered.
        """
        super().render(surface)
        self.room_display.render(surface)
        self.player_display.render(surface)
        self.halo_effect.render(surface)
        self.info_box.render(surface)
        self.info_text.render(surface)
