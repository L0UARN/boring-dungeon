"""
Classes:
    - GameLayer
"""

from random import Random
from pygame import Surface, event
from source.core.layer import Layer
from source.player import Player, PlayerComponent
from source.level import Level, LevelComponent
from source.room import Room, RoomComponent
from source.core.tools import Position, Direction
from source.core.textures import TILE_SIZE
from source.halo import HaloComponent


class ExplorationLayer(Layer):
    """
    Controls the different components of the exploration sequence of gameplay (navigating the level and the rooms).
    """
    def __init__(self, seed: str, width: int, height: int) -> None:
        super().__init__(False, width, height)

        self.seed = seed
        self.difficulty = 1
        self.generation_rng = Random()
        self.generation_rng.seed(a=seed, version=2)

        self.level = Level(self.difficulty, self.generation_rng)
        self.rooms: dict[Position, Room] = {}
        for room_position in self.level.rooms:
            openings = [room_position.direction(linked) for linked in self.level.graph[room_position]]
            self.rooms[room_position] = Room(self.difficulty, self.generation_rng, openings)

        self.player = Player(10, list(self.level.graph.keys())[0], Direction.NORTH, self.level.graph)
        self.inside_room = False
        self.current_room = Position(0, 0)

        self.level_display = LevelComponent(
            self.level,
            list(self.level.graph.keys())[0],
            Position(0, 0),
            width,
            height
        )

        self.room_display = RoomComponent(
            list(self.rooms.values())[0],
            list(list(self.rooms.values())[0].graph.keys())[0],
            Position(0, 0),
            width,
            height
        )

        self.player_display = PlayerComponent(
            self.player,
            Position((width - TILE_SIZE) // 2, (height - TILE_SIZE) // 2),
            TILE_SIZE,
            TILE_SIZE
        )

        self.halo = HaloComponent(Position(0, 0), width, height)

    def level_down(self) -> None:
        """
        Go down a level in the dungeon. Loads a new level and its rooms.
        """
        self.difficulty += 1

        self.level = Level(self.difficulty, self.generation_rng)
        self.rooms: dict[Position, Room] = {}
        for room_position in self.level.rooms:
            openings = [linked.direction(room_position) for linked in self.level.graph[room_position]]
            self.rooms[room_position] = Room(self.difficulty, self.generation_rng, openings)

        self.player.position = list(self.level.graph.keys())[0]
        self.player.graph = self.level.graph

        self.level_display.level = self.level
        self.level_display.center = self.player.position
        self.room_display.room = list(self.rooms.values())[0]
        self.room_display.center = list(self.room_display.room.graph.keys())[0]

    def enter_room(self, position: Position, direction: Direction) -> None:
        """ Makes the player enter a room of the level.

        :param position: The position of the desired room.
        :param direction: The direction from which the player enters the room.
        """
        self.room_display.room = self.rooms[position]

        self.player.graph = self.room_display.room.graph
        direction_to_door = {self.room_display.room.doors[p]: p for p in self.room_display.room.doors}
        self.player.position = direction_to_door[direction.opposite()].next_in_direction(direction)

        self.room_display.center = self.player.position

        self.inside_room = True
        self.current_room = position

    def exit_room(self, direction: Direction) -> None:
        """ Makes the player exit a room.

        :param direction: The direction from which the player exited the room.
        """
        self.player.graph = self.level.graph
        self.player.position = self.current_room.next_in_direction(direction)
        self.level_display.center = self.player.position

        self.inside_room = False
        self.current_room = Position(0, 0)

    def update(self, events: list[event.Event]) -> None:
        super().update(events)

        self.player_display.update(events)
        self.halo.update(events)

        if not self.inside_room:
            self.level_display.update(events)
            self.level_display.center = self.player.position

            if self.player.position in self.level.stairs:
                self.level_down()
            elif self.player.position in self.level.rooms:
                self.enter_room(self.player.position, self.player.direction)
        else:
            self.room_display.update(events)
            self.room_display.center = self.player.position

            if self.player.position in self.room_display.room.doors:
                self.exit_room(self.player.direction)

    def render(self, surface: Surface) -> None:
        super().render(surface)

        if not self.inside_room:
            self.level_display.render(surface)
        else:
            self.room_display.render(surface)

        self.player_display.render(surface)
        self.halo.render(surface)
