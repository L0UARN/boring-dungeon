"""
Classes:
    - PauseLayer
"""

from pygame import event
from source.core.layer import Layer
from source.ui.button import ButtonComponent
from source.ui.text import TextComponent
from source.ui.darkener import DarkenerComponent
from source.core.tools import Position


class PauseLayer(Layer):
    """
    The pause menu.
    """
    def __init__(self, width: int, height: int) -> None:
        """
        :param width: The width of the screen.
        :param height: The height of the screen.
        """
        super().__init__(True, width, height)

        self.background = DarkenerComponent(Position(0, 0), width, height, True, 0, 160, 1.0)
        self.title = TextComponent("resources/font.ttf", 48, (255, 255, 255), Position(0, 0), width, height * 0.10, True, 16.0)
        self.title.set_text(["PAUSED"])

        self.resume_button = ButtonComponent((255, 255, 255), Position(width / 2 - 128, height * 0.45), 256, 48)
        self.resume_text = TextComponent("resources/font.ttf", 24, (255, 255, 255), self.resume_button.render_position, 256, 48)
        self.resume_text.set_text(["Resume"])

        self.quit_button = ButtonComponent((255, 255, 255), Position(width / 2 - 128, height * 0.55), 256, 48)
        self.quit_text = TextComponent("resources/font.ttf", 24, (255, 255, 255), self.quit_button.render_position, 256, 48)
        self.quit_text.set_text(["Exit game"])

        self.add_component("background", self.background)
        self.add_component("title", self.title)
        self.add_component("resume", self.resume_button)
        self.add_component("resume_text", self.resume_text)
        self.add_component("quit", self.quit_button)
        self.add_component("quit_text", self.quit_text)

    def update(self, events: list[event.Event]) -> None:
        super().update(events)

        if self.resume_button.is_hovered and self.resume_text.color == (255, 255, 255):
            self.resume_text.set_color((0, 0, 0))
        elif not self.resume_button.is_hovered and self.resume_text.color == (0, 0, 0):
            self.resume_text.set_color((255, 255, 255))

        if self.quit_button.is_hovered and self.quit_text.color == (255, 255, 255):
            self.quit_text.set_color((0, 0, 0))
        elif not self.quit_button.is_hovered and self.quit_text.color == (0, 0, 0):
            self.quit_text.set_color((255, 255, 255))
