import pygame as pg
from source.exploration import ExplorationLayer
from source.core.layer import LayerManager


if __name__ == '__main__':
    pg.init()

    window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    pg.display.set_caption("Boring")

    exploration = ExplorationLayer("test", window.get_width(), window.get_height())

    manager = LayerManager()
    manager.add_layer("game", exploration)

    run = True
    while run:
        events: list[pg.event.Event] = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False

        manager.update(events)

        manager.render(window)
        pg.display.update()

    pg.quit()
