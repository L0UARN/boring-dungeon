import pygame as pg

from pygame import event, Surface
from source.core.textures import TextureBook, Texture
from source.core.tools import Position
from source.core.component import Component
from source.core.layer import Layer, LayerManager


class TextureComponent(Component):
    def __init__(self, texture: Texture, render_position: Position):
        super().__init__(render_position, texture.get_width(), texture.get_height())
        self.texture = texture

    def update(self, events: list[event.Event]) -> None:
        self.render_position.x += 0.1

    def render(self, surface: Surface) -> None:
        self.texture.render(surface, self.render_position)


if __name__ == '__main__':
    pg.init()

    book = TextureBook()
    book.load("resources/textures.json")

    thing = TextureComponent(book.get("test_tile"), Position(0, 0))
    layer = Layer(True, 1280, 720)
    layer.add_component("thing", thing)

    stuff = TextureComponent(book.get("test_ui"), Position(10, 10))
    layer_2 = Layer(False, 1280, 720)
    layer_2.add_component("stuff", stuff)

    manager = LayerManager()
    manager.add_layer("1", layer)
    manager.add_layer("2", layer_2)
    manager.set_focus("1")

    window = pg.display.set_mode((1280, 720))
    pg.display.set_caption("Boring")

    run = True
    while run:
        events: list[pg.event.Event] = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
            elif event.type == pg.KEYDOWN:
                manager.set_focus("2")

        manager.update(events)

        manager.render(window)
        pg.display.update()

    pg.quit()
