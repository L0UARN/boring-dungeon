"""
Classes:
    - Game
"""

from random import Random, choice
from time import time
import pygame as pg
from source.core.layer import LayerManager
from source.player import Player
from source.level import Level, LevelLayer
from source.core.tools import Position, Direction
from source.room import Room, RoomLayer
from source.menu import MenuLayer
from source.core.texture import Texture
from source.resources import TEXTURES
from source.inventory import InventoryLayer, Inventory
from source.item import Weapon


class Game(LayerManager):
    """
    Manages the game's flow and states.
    """
    def __init__(self) -> None:
        super().__init__()

        pg.init()
        self.window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        pg.display.set_caption("Boring Dungeon")
        pg.display.set_icon(pg.transform.scale(pg.image.load("resources/icon.png"), (64, 64)))

        Texture.UIScale = self.window.get_width() / 1920
        Texture.TileSize = self.window.get_width() // 40
        TEXTURES.load("resources/textures.json")

        self.generation_rng: Random = None
        self.seed: str = None
        self.player: Player = None
        self.level: Level = None
        self.level_layer: LevelLayer = None
        self.current_room: Position = None
        self.rooms: dict[Position, Room] = None
        self.room_layer: RoomLayer = None
        self.inventory_layer: InventoryLayer = None

        self.menu_layer = MenuLayer(self.window.get_width(), self.window.get_height())

        self.add_layer("menu", self.menu_layer)
        self.set_focus("menu")

    def start(self) -> None:
        """
        Starts the game's loop.
        """
        run = True
        while run:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    run = False

            self.update(events)
            self.render(self.window)
            pg.display.update()

        pg.quit()

    def _initial_load(self) -> None:
        """
        Loads the game's component after the menu phase.
        """
        self.generation_rng = Random()
        if self.menu_layer.input.get_text() == "":
            file = open("resources/seeds.txt", "r")
            self.seed = choice(file.read().split("\n"))
            file.close()
        else:
            self.seed = self.menu_layer.input.get_text()
        self.generation_rng.seed(a=self.seed, version=2)

        self.level = Level(1, self.generation_rng)
        self.player = Player(10, list(self.level.graph.keys())[0], Direction.NORTH, self.level.graph)
        self.level_layer = LevelLayer(self.level, self.player, self.window.get_width(), self.window.get_height())
        self.rooms = {self.level.rooms[i]: Room(1, self.generation_rng, [p.direction(self.level.rooms[i]) for p in self.level.graph[self.level.rooms[i]]]) for i in range(len(self.level.rooms))}
        self.current_room = list(self.rooms.keys())[0]
        self.room_layer = RoomLayer(list(self.rooms.values())[0], self.player, self.window.get_width(), self.window.get_height())

        inventory = Inventory()
        inventory.add_item(Weapon("sword", 1, 3))
        self.player.inventory = inventory

        self.inventory_layer = InventoryLayer(self.player.inventory, self.window.get_width(), self.window.get_height())

        self.level_layer.info_text.set_text([
            f"Level: {self.level.difficulty}",
            f"Seed: {self.seed}"
        ])

        self.add_layer("level", self.level_layer)
        self.add_layer("room", self.room_layer)
        self.add_layer("inventory", self.inventory_layer)
        self.set_focus("level")

    def _level_down(self) -> None:
        """
        Loads the next level's components.
        """
        self.level = Level(self.level.difficulty + 1, self.generation_rng)

        self.player.position = list(self.level.graph.keys())[0]
        self.player.graph = self.level.graph
        self.level_layer.player_display.last_moved = time() + 0.2

        self.rooms = {self.level.rooms[i]: Room(self.level.difficulty, self.generation_rng, [p.direction(self.level.rooms[i]) for p in self.level.graph[self.level.rooms[i]]]) for i in range(len(self.level.rooms))}
        self.current_room = list(self.rooms.keys())[0]

        self.level_layer.level_display.level = self.level
        self.room_layer.room_display.room = self.rooms[self.current_room]

        self.level_layer.info_text.set_text([
            f"Level: {self.level.difficulty}",
            f"Seed: {self.seed}"
        ])

    def _enter_room(self, room: Position) -> None:
        """
        Sets up a room in order to display it.

        :param room: The index of the room inside of `self.rooms`
        """
        self.current_room = room
        self.room_layer.room_display.room = self.rooms[self.current_room]

        direction_to_pos_doors = {self.rooms[self.current_room].doors[p]: p for p in self.rooms[self.current_room].doors}
        self.player.position = direction_to_pos_doors[self.player.direction.opposite()].next_in_direction(self.player.direction)
        self.player.graph = self.rooms[self.current_room].graph
        self.room_layer.player_display.last_moved = time() + 0.2

        self.room_layer.info_text.set_text([
            f"Level: {self.level.difficulty}",
            f"Room: {list(self.rooms.keys()).index(self.current_room) + 1}",
            f"Seed: {self.seed}"
        ])

        self.set_focus("room")

    def _exit_room(self) -> None:
        """
        Exit a room to go back to the level exploring part of the game.
        """
        self.player.position = self.current_room.next_in_direction(self.player.direction)
        self.player.graph = self.level.graph
        self.level_layer.player_display.last_moved = time() + 0.2

        self.level_layer.info_text.set_text([
            f"Level: {self.level.difficulty}",
            f"Seed: {self.seed}"
        ])

        self.set_focus("level")

    def update(self, events: list[pg.event.Event]) -> None:
        """ Updates the game.

        :param events: A list of the lastly pulled events.
        """
        super().update(events)

        if self.get_focus() == "menu":
            if self.menu_layer.button.is_clicked:
                self._initial_load()
                self.menu_layer.button.is_clicked = False
                self.menu_layer.input.clear_text()
        elif self.get_focus() == "level":
            if self.player.position in self.level.stairs:
                self._level_down()
            elif self.player.position in self.level.rooms:
                self._enter_room(self.player.position)
        elif self.get_focus() == "room":
            if self.player.position in self.rooms[self.current_room].doors:
                self._exit_room()

        for event in events:
            if event.type == pg.KEYDOWN:
                if (event.key == pg.K_e or event.key == pg.K_i) and (self.get_focus() == "level" or self.get_focus() == "room"):
                    self.set_focus("inventory")
                elif (event.key == pg.K_ESCAPE or event.key == pg.K_e or event.key == pg.K_i) and self.get_focus() == "inventory":
                    self.unfocus()
