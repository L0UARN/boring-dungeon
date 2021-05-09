"""
Classes:
    - MenuLayer
"""

from pygame import event, Surface
from source.core.layer import Layer
from source.resources import TEXTURES as T
from source.ui.text import TextComponent
from source.core.tools import Position
from source.ui.input import InputComponent
from source.ui.button import ButtonComponent


class MenuLayer(Layer):
    """
    The game's main menu.
    """
    def __init__(self, width: int, height: int):
        super().__init__(False, width, height)
        self.background = T.get("menu_background")

        self.title = TextComponent("resources/font.ttf", 64, (255, 255, 255), Position(0, 0), width, int(height * 0.20), True, 8.0)
        self.title.set_text(["BORING DUNGEON"])

        self.input_hint = TextComponent("resources/font.ttf", 24, (255, 255, 255), Position(0, int(height * 0.33)), width, 24)
        self.input_hint.set_text(["Seed:"])
        self.input = InputComponent("resources/font.ttf", 24, (255, 255, 255), Position((width - 256) // 2, self.input_hint.render_position.y + 32), 256, 48)

        self.button = ButtonComponent((255, 255, 255), Position((width - 256) // 2, int(height * 0.50)), 256, 48)
        self.button_text = TextComponent("resources/font.ttf", 24, (255, 255, 255), Position((width - 256) // 2, int(height * 0.50)), 256, 48)
        self.button_text.set_text(["Play!"])

    def update(self, events: list[event.Event]) -> None:
        """ Updates the menu.

        :param events: A list of the lastly pulled events.
        """
        self.title.update(events)
        self.input_hint.update(events)
        self.input.update(events)

        self.button.update(events)
        if self.button.is_hovered and self.button_text.color == (255, 255, 255):
            self.button_text.set_color((0, 0, 0))
        elif not self.button.is_hovered and self.button_text.color == (0, 0, 0):
            self.button_text.set_color((255, 255, 255))
        self.button_text.update(events)

    def render(self, surface: Surface) -> None:
        """ Renders the menu to the specified surface.

        :param surface: The surface on which the menu will be rendered.
        """
        self.background.render(surface, Position(0, 0))
        self.title.render(surface)
        self.input_hint.render(surface)
        self.input.render(surface)
        self.button.render(surface)
        self.button_text.render(surface)
