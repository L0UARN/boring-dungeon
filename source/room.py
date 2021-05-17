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
from source.core.texture import Texture
from source.resources import TEXTURES as T
from source.core.layer import Layer
from source.player import Player, ExploringPlayerComponent
from source.ui.halo import HaloComponent
from source.ui.box import BoxComponent
from source.ui.text import TextComponent
from source.loot import LootTable
from source.item import Item
from source.enemy import Enemy, EnemyComponent
from source.inventory import Inventory


class Room:
    """
    Rooms are placed inside of levels, they contain items to loot and enemies to fight.
    """
    def __init__(self, difficulty: int, generation_rng: Random, ai_rng: Random, loot_table: LootTable, openings: list[Direction]) -> None:
        """
        :param difficulty: How complex and big the room is.
        :param generation_rng: The random number generator used the generation process.
        """
        self.difficulty = difficulty
        self.rng = generation_rng

        self.width = 0
        self.height = 0
        self.graph: dict[Position, list[Position]] = {}

        self.openings = openings
        self.doors: dict[Position, Direction] = {}
        self.loot_table = loot_table
        self.items: dict[Position, Item] = {}
        self.ai_rng = ai_rng
        self.enemies: list[Enemy] = []

        self.generate()

    def generate(self) -> None:
        """
        Generates the room and its content.
        """
        self._generate_room()
        self._generate_doors()
        self._generate_items()
        self._generate_enemies()

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

    def _generate_items(self) -> None:
        """
        Generates the items in the room, based on the provided loot table.
        """
        items = self.loot_table.get_items()

        available_spots = list(self.graph.keys())
        for door in self.doors:
            available_spots.remove(door)
        spots = self.rng.sample(available_spots, len(items))

        self.items = {spots[i]: items[i] for i in range(len(items)) if items[i] is not None}

    def _generate_enemies(self) -> None:
        if self.difficulty == 1:
            self.enemies = []
            return

        enemy_graph = {p: [l for l in self.graph[p] if l not in self.doors] for p in self.graph if p not in self.doors}
        self.enemies = [Enemy(
            self.rng.randint(5 + self.difficulty, 5 + self.difficulty * 2),
            self.rng.randint(5 + self.difficulty, 5 + self.difficulty * 2),
            self.rng.choice(list(enemy_graph.keys())),
            self.rng.choice(list(Direction)),
            enemy_graph,
            self.ai_rng
        ) for _ in range(0, self.rng.randint(0, self.difficulty // 2))]

        for enemy in self.enemies:
            enemy.inventory.set_weapon(self.loot_table.get_weapon(), False)
            enemy.inventory.set_armor(self.loot_table.get_armor(), False)


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
        self.item_texture = T.get("item")

    def update(self, events: list[event.Event]) -> None:
        """ Updates the room with the latest events.

        :param events: The list of the lastly pulled events.
        """
        pass

    def render(self, surface: Surface) -> None:
        """ Renders the room on the specified surface.

        :param surface: The surface on which to render the room.
        """
        width_blocks: int = ceil(self.render_width / Texture.TileSize)
        if width_blocks % 2 == 0:
            width_blocks += 1
        height_blocks: int = ceil(self.render_height / Texture.TileSize)
        if height_blocks % 2 == 0:
            height_blocks += 1

        offset_x = self.render_position.x - (width_blocks * Texture.TileSize - self.render_width) // 2
        offset_y = self.render_position.y - (height_blocks * Texture.TileSize - self.render_height) // 2

        for x in range(self.center.x - floor(width_blocks / 2), self.center.x + ceil(width_blocks / 2)):
            for y in range(self.center.y - floor(height_blocks / 2), self.center.y + ceil(height_blocks / 2)):
                if Position(x, y) in self.room.doors:
                    self.door_texture.render(
                        surface,
                        Position(offset_x, offset_y),
                        Position(x, y).direction_of(self.room.graph[Position(x, y)][0])
                    )
                elif Position(x, y) in self.room.items:
                    self.item_texture.render(surface, Position(offset_x, offset_y))
                elif Position(x, y) in self.room.graph:
                    self.floor_texture.render(surface, Position(offset_x, offset_y))
                else:
                    self.brick_texture.render(surface, Position(offset_x, offset_y))

                offset_y += Texture.TileSize
            offset_y = self.render_position.y - (height_blocks * Texture.TileSize - self.render_height) // 2
            offset_x += Texture.TileSize


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
        self.player_display = ExploringPlayerComponent(player, Position((width - Texture.TileSize) // 2, (height - Texture.TileSize) // 2), Texture.TileSize, Texture.TileSize)
        self.enemy_displays = [EnemyComponent(enemy, Position(0, 0)) for enemy in self.room_display.room.enemies]
        print(len(self.enemy_displays))
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

        for i in range(len(self.enemy_displays)):
            self.enemy_displays[i].update(events)

            if self.enemy_displays[i].enemy.direction == self.player_display.player.position.direction_of(self.enemy_displays[i].enemy.position) and \
               self.enemy_displays[i].enemy.position.distance(self.player_display.player.position) <= 3 and \
               self.enemy_displays[i].enemy.has_path(self.player_display.player.position) and \
               not self.enemy_displays[i].enemy.has_target:
                self.player_display.movement_locked = True
                self.enemy_displays[i].enemy_texture = T.get("enemy_aggro")
                self.enemy_displays[i].enemy.has_target = True
                self.enemy_displays[i].enemy.destination = self.player_display.player.position

                for j in range(len(self.enemy_displays)):
                    if j != i:
                        self.enemy_displays[j].enemy.ai_locked = True

                break

        self.room_display.center = self.player_display.player.position
        self.halo_effect.update(events)
        self.info_box.update(events)
        self.info_text.update(events)

        if self.player_display.player.position in self.room_display.room.items:
            if self.player_display.player.inventory.add_item(self.room_display.room.items[self.player_display.player.position]) != -1:
                self.room_display.room.items.pop(self.player_display.player.position)

    def render(self, surface: Surface) -> None:
        """ Renders the layer to the specified surface.

        :param surface: The surface on which the layer will be rendered.
        """
        super().render(surface)
        self.room_display.render(surface)
        self.player_display.render(surface)

        for enemy in self.enemy_displays:
            enemy.render_position = Position(
                self.player_display.render_position.x + (enemy.enemy.position.x - self.room_display.center.x) * Texture.TileSize,
                self.player_display.render_position.y + (enemy.enemy.position.y - self.room_display.center.y) * Texture.TileSize
            )
            enemy.render(surface)

        self.halo_effect.render(surface)
        self.info_box.render(surface)
        self.info_text.render(surface)
