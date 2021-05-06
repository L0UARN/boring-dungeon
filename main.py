from random import Random
import pygame as pg
from source.core.textures import TextureBook, Texture
from source.core.tools import Position, Direction
from source.core.layer import Layer, LayerManager
from source.level import Level, LevelComponent


if __name__ == '__main__':
    pg.init()

    window = pg.display.set_mode((1280, 720), pg.RESIZABLE)
    pg.display.set_caption("Boring")

    generation_rng = Random()
    generation_rng.seed(a="test", version=2)

    level = LevelComponent(Position(0, 0), window.get_width(), window.get_height())
    level.generate(1, generation_rng)

    game_layer = Layer(False, 2000, 2000)
    game_layer.add_component("level", level)

    manager = LayerManager()
    manager.add_layer("game", game_layer)

    run = True
    while run:
        events: list[pg.event.Event] = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False

        manager.update(events)

        manager.render(window)
        pg.draw.rect(window, (255, 0, 0), pg.Rect(window.get_rect().center[0], window.get_rect().center[1], 2, 2))
        pg.display.update()

    pg.quit()
