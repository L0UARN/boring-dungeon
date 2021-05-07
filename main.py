from random import Random
import pygame as pg
from source.core.tools import Position, Direction
from source.core.layer import Layer, LayerManager
from source.level import Level, LevelComponent
from source.player import Player, PlayerComponent
from source.halo import HaloComponent
from source.core.textures import TILE_SIZE
from source.room import Room, RoomComponent


if __name__ == '__main__':
    pg.init()

    window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    pg.display.set_caption("Boring")

    level_generation_rng = Random()
    level_generation_rng.seed(a="test", version=2)

    # level = Level(1, level_generation_rng)
    # level_display = LevelComponent(level, list(level.graph.keys())[0], Position(0, 0), window.get_width(), window.get_height())
    room = Room(1, Random(), [Direction.EAST, Direction.NORTH])
    room_display = RoomComponent(room, list(room.graph.keys())[0], Position(0, 0), window.get_width(), window.get_height())
    player = Player(10, list(room.graph.keys())[0], Direction.NORTH, room.graph)
    player_display = PlayerComponent(player, Position((room_display.render_width - TILE_SIZE) // 2, (room_display.render_height - TILE_SIZE) // 2), TILE_SIZE, TILE_SIZE)
    halo = HaloComponent(Position(0, 0), window.get_width(), window.get_height())

    game_layer = Layer(False, window.get_width(), window.get_height())
    # game_layer.add_component("level", level_display)
    game_layer.add_component("room", room_display)
    game_layer.add_component("player", player_display)
    game_layer.add_component("halo", halo)

    manager = LayerManager()
    manager.add_layer("game", game_layer)

    run = True
    while run:
        events: list[pg.event.Event] = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False

        manager.update(events)
        room_display.center = player.position

        manager.render(window)
        pg.display.update()

    pg.quit()
