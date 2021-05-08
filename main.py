from random import Random
import pygame as pg
from source.core.layer import LayerManager, Layer
from source.level import Level, LevelComponent
from source.player import Player, PlayerComponent
from source.halo import HaloComponent
from source.core.tools import Position, Direction
from source.core.texture import TILE_SIZE
from source.box import BoxComponent


if __name__ == '__main__':
    pg.init()

    window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    pg.display.set_caption("Boring")

    generation_rng = Random()
    generation_rng.seed(a="test", version=2)

    level = Level(1, generation_rng)
    level_display = LevelComponent(level, Position(0, 0), Position(0, 0), window.get_width(), window.get_height())
    player = Player(10, list(level.graph.keys())[0], Direction.NORTH, level.graph)
    player_display = PlayerComponent(player, Position((window.get_width() - TILE_SIZE) / 2, (window.get_height() - TILE_SIZE) / 2), TILE_SIZE, TILE_SIZE)
    halo = HaloComponent(Position(0, 0), window.get_width(), window.get_height())
    box = BoxComponent(Position(0, 0), window.get_width(), window.get_height() * 0.25)

    level_layer = Layer(False, window.get_width(), window.get_height())
    level_layer.add_component("level", level_display)
    level_layer.add_component("player", player_display)
    level_layer.add_component("halo", halo)
    level_layer.add_component("box", box)

    manager = LayerManager()
    manager.add_layer("level", level_layer)

    run = True
    while run:
        events: list[pg.event.Event] = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False

        manager.update(events)
        level_display.center = player.position

        manager.render(window)
        pg.display.update()

    pg.quit()
