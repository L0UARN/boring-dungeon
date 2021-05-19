"""
Classes:
    - EndLayer
"""

from pygame import event
from source.core.layer import Layer
from source.player import Player
from source.ui.text import TextComponent
from source.core.tools import Position
from source.ui.button import ButtonComponent
from source.ui.darkener import DarkenerComponent


class EndLayer(Layer):
    """
    A layer representing the end screen of the game.
    """
    def __init__(self, player: Player, depth: int, width: int, height: int):
        super().__init__(True, width, height)
        self.player = player
        self.depth = depth

        self.background = DarkenerComponent(Position(0, 0), width, height, True, 0, 255, 4.0)

        self.title = TextComponent("resources/font.ttf", 48, (255, 255, 255), Position(0, height // 4), width, 64, True, 4.0)
        self.title.set_text(["You died..."])

        self.stats = TextComponent("resources/font.ttf", 24, (255, 255, 255), Position(0, height // 2), width, 96, True, 12.0)
        self.stats.set_text([
            f"Player level: {self.player.exp_level}",
            f"Level reached: {depth}"
        ])

        self.button = ButtonComponent((255, 255, 255), Position(width // 2 - 128, height // 4 * 3), 256, 64)
        self.button_text = TextComponent("resources/font.ttf", 24, (255, 255, 255), self.button.render_position, self.button.render_width, self.button.render_height)
        self.button_text.set_text(["Menu"])

        self.add_component("background", self.background)
        self.add_component("title", self.title)
        self.add_component("stats", self.stats)
        self.add_component("button", self.button)
        self.add_component("button_text", self.button_text)

    def update(self, events: list[event.Event]) -> None:
        super().update(events)

        if self.button.is_hovered and self.button_text.color == (255, 255, 255):
            self.button_text.set_color((0, 0, 0))
        elif not self.button.is_hovered and self.button_text.color == (0, 0, 0):
            self.button_text.set_color((255, 255, 255))