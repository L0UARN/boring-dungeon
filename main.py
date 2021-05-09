from random import Random
import pygame as pg
from source.core.layer import LayerManager
from source.level import Level, LevelLayer
from source.room import Room, RoomLayer
from source.player import Player
from source.core.tools import Position, Direction


if __name__ == '__main__':
    pg.init()

    window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    pg.display.set_caption("Boring")

    generation_rng = Random()
    generation_rng.seed(a="test", version=2)

    level = Level(5, generation_rng)
    rooms = [Room(5, generation_rng, [Direction.NORTH, Direction.SOUTH]) for room in level.rooms]
    player = Player(10, list(rooms[0].graph.keys())[0], Direction.NORTH, rooms[0].graph)

    level_layer = LevelLayer(level, player, window.get_width(), window.get_height())
    room_layer = RoomLayer(rooms[0], player, window.get_width(), window.get_height())

    manager = LayerManager()
    manager.add_layer("level", level_layer)
    manager.add_layer("room", room_layer)
    manager.set_focus("room")

    run = True
    count = 0

    while run:
        events: list[pg.event.Event] = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False

        manager.update(events)

        manager.render(window)
        pg.display.update()

    pg.quit()
