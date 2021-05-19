"""
Classes:
    - Game
"""

from random import Random, choice
from time import time
from os import listdir
import pygame as pg
from source.core.layer import LayerManager
from source.player import Player
from source.level import Level, LevelLayer
from source.core.tools import Position, Direction
from source.room import Room, RoomLayer
from source.menu import MenuLayer
from source.core.texture import Texture
from source.resources import TEXTURES
from source.inventory import InventoryLayer
from source.loot import ITEMS, LootTable
from source.enemy import RoamingEnemyComponent, Enemy
from source.fight import FightLayer
from source.item import ArmorSlot
from source.end import EndLayer


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
        self.ai_rng: Random = None
        self.seed: str = None
        self.player: Player = None
        self.level: Level = None
        self.level_layer: LevelLayer = None
        self.current_room: Position = None
        self.rooms: dict[Position, Room] = None
        self.room_layer: RoomLayer = None
        self.inventory_layer: InventoryLayer = None
        self.fight_layer: FightLayer = None
        self.end_layer: EndLayer = None

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
        self.ai_rng = Random()
        if self.menu_layer.input.get_text() == "":
            file = open("data/seeds.txt", "r")
            self.seed = choice(file.read().split("\n"))
            file.close()
        else:
            self.seed = self.menu_layer.input.get_text()
        self.generation_rng.seed(a=self.seed, version=2)
        self.ai_rng.seed(a=self.seed, version=2)

        ITEMS.load("data/items.json")
        self.loot_tables = [LootTable(f"data/loot_tables/{file}", self.generation_rng) for file in sorted(listdir("data/loot_tables/")) if file.split(".")[-1] == "json"]

        self.level = Level(1, self.generation_rng)
        self.player = Player(15, 5, list(self.level.graph.keys())[0], Direction.NORTH, self.level.graph)
        self.level_layer = LevelLayer(self.level, self.player, self.window.get_width(), self.window.get_height())
        self.rooms = {self.level.rooms[i]: Room(1, self.generation_rng, self.ai_rng, self.loot_tables[0], [p.direction_of(self.level.rooms[i]) for p in self.level.graph[self.level.rooms[i]]]) for i in range(len(self.level.rooms))}
        self.current_room = list(self.rooms.keys())[0]
        self.room_layer = RoomLayer(list(self.rooms.values())[0], self.player, self.window.get_width(), self.window.get_height())
        self.inventory_layer = InventoryLayer(self.player, self.player.inventory, self.window.get_width(), self.window.get_height())
        self.fight_layer = FightLayer(self.player, Enemy(1, 1, Position(0, 0), Direction.NORTH, {"a": 0}, Random()), self.window.get_width(), self.window.get_height())
        self.end_layer = EndLayer(self.player, 0, self.window.get_width(), self.window.get_height())

        self.level_layer.info_text.set_text([
            f"Level: {self.level.difficulty}",
            f"Seed: {self.seed}"
        ])

        self.add_layer("level", self.level_layer)
        self.add_layer("room", self.room_layer)
        self.add_layer("inventory", self.inventory_layer)
        self.add_layer("fight", self.fight_layer)
        self.add_layer("end", self.end_layer)
        self.set_focus("level")

    def _level_down(self) -> None:
        """
        Loads the next level's components.
        """
        self.level = Level(self.level.difficulty + 1, self.generation_rng)

        self.player.position = list(self.level.graph.keys())[0]
        self.player.graph = self.level.graph
        self.level_layer.player_display.last_moved = time() + 0.2

        loot_table_index = self.level.difficulty - 1 if self.level.difficulty - 1 < len(self.loot_tables) else -1
        self.rooms = {self.level.rooms[i]: Room(self.level.difficulty, self.generation_rng, self.ai_rng, self.loot_tables[loot_table_index], [p.direction_of(self.level.rooms[i]) for p in self.level.graph[self.level.rooms[i]]]) for i in range(len(self.level.rooms))}
        self.current_room = list(self.rooms.keys())[0]

        self.level_layer.level_display.level = self.level
        self.room_layer.room_display.room = self.rooms[self.current_room]
        self.room_layer.enemy_displays = [RoamingEnemyComponent(enemy, Position(0, 0)) for enemy in self.rooms[self.current_room].enemies]

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
        self.room_layer.enemy_displays = [RoamingEnemyComponent(enemy, Position(0, 0)) for enemy in self.rooms[self.current_room].enemies]

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

    def _enter_fight(self, enemy: Enemy) -> None:
        """
        Make the player fight with an enemy.
        """
        self.fight_layer = FightLayer(self.player, enemy, self.window.get_width(), self.window.get_height())
        self.layers["fight"] = self.fight_layer
        self.set_focus("fight")

    def _exit_fight(self) -> None:
        """
        Stops the fight screen and goes back to room exploration.
        """
        if self.fight_layer.enemy_display.enemy.speed >= self.fight_layer.enemy_display.enemy.inventory.get_protection():
            weapon = self.fight_layer.enemy_display.enemy.inventory.get_weapon()
            if weapon is not None:
                self.room_layer.room_display.room.items[self.player.position] = weapon
        else:
            pieces = [self.fight_layer.enemy_display.enemy.inventory.get_armor(s) for s in ArmorSlot]
            while None in pieces:
                pieces.remove(None)
            if len(pieces) >= 1:
                self.room_layer.room_display.room.items[self.player.position] = pieces[0]

        self.player.give_exp(self.fight_layer.enemy_display.enemy.speed + self.fight_layer.enemy_display.enemy.max_health)

        self.room_layer.player_display.movement_locked = False
        for enemy in self.room_layer.enemy_displays:
            enemy.ai_locked = False

        self.set_focus("room")

    def _end(self) -> None:
        self.end_layer = EndLayer(self.player, self.level_layer.level_display.level.difficulty, self.window.get_width(), self.window.get_height())
        self.layers["end"] = self.end_layer
        self.set_focus("end")

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
            else:
                enemy_id = -1
                for i in range(len(self.room_layer.enemy_displays)):
                    if self.room_layer.enemy_displays[i].enemy.position == self.player.position:
                        self._enter_fight(self.room_layer.enemy_displays[i].enemy)
                        enemy_id = i
                        break

                if enemy_id != -1:
                    self.room_layer.enemy_displays.pop(enemy_id)
        elif self.get_focus() == "fight":
            if self.fight_layer.ended:
                self._exit_fight()
                if self.player.health == 0:
                    self._end()
        elif self.get_focus() == "end":
            if self.end_layer.button.is_clicked:
                self.set_focus("menu")

        for event in events:
            if event.type == pg.KEYDOWN:
                if (event.key == pg.K_e or event.key == pg.K_i) and (self.get_focus() == "level" or self.get_focus() == "room" or self.get_focus() == "fight"):
                    self.set_focus("inventory")
                elif (event.key == pg.K_ESCAPE or event.key == pg.K_e or event.key == pg.K_i) and self.get_focus() == "inventory":
                    self.unfocus()
