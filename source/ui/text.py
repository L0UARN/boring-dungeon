"""
Classes:
    - TextComponent
"""

from time import time
from math import floor
from pygame.font import Font
from pygame import Surface, event
from source.core.component import Component
from source.core.tools import Position


class TextComponent(Component):
    """
    A component used to display text.
    """
    def __init__(self, font: str, size: int, color: tuple[int, int, int], render_position: Position, render_width: int, render_height: int, animated: bool = False, speed: float = 1.0) -> None:
        """
        :param font: The path of the font used.
        :param size: The size of the font.
        :param color: The color of the text.
        :param render_position: The position of the text box.
        :param render_width: The width of the text box.
        :param render_height: The height of the text box.
        :param animated: True if the text needs to appear in an animated way.
        :param speed: If `animated=True`, sets the speed of apparition of the text.
        """
        super().__init__(render_position, render_width, render_height)

        self.font = Font(font, size)
        self.color = color
        self.lines: list[str] = []
        self.rendered_lines: list[Surface] = []

        self.animated = animated
        self.current_lines: list[str] = []
        self.speed = speed
        self.apparition_time = -1

    def set_text(self, lines: list[str]) -> None:
        """ Change the text to display.

        :param lines: The lines of text which will be displayed.
        """
        self.lines = lines

        if not self.animated:
            self.pre_render()
        else:
            self.apparition_time = -1

    def set_color(self, color: tuple[int, int, int]) -> None:
        """ Changes the color of the text.

        :param color: The color of the text.
        """
        self.color = color
        self.pre_render()

    def pre_render(self) -> None:
        """
        Renders the text to a buffer.
        """
        self.rendered_lines = []
        for line in self.lines:
            self.rendered_lines.append(self.font.render(line, False, self.color))

    def update(self, events: list[event.Event]) -> None:
        """ Updates the text display.

        :param events: A list of the lastly pulled events.
        """
        pass

    def render(self, surface: Surface) -> None:
        """ Renders the text to the specified surface.

        :param surface: The surface on which to render the text.
        """
        if self.animated and self.current_lines != self.lines:
            if self.apparition_time == -1:
                self.apparition_time = time()
                self.current_lines = ["" for _ in range(len(self.lines))]

            amount = floor((time() - self.apparition_time) * self.speed)
            for i in range(len(self.lines)):
                if amount >= len(self.lines[i]):
                    self.current_lines[i] = self.lines[i]
                    amount -= len(self.lines[i])
                else:
                    self.current_lines[i] = self.lines[i][:amount]
                    break

            self.rendered_lines = []
            for line in self.current_lines:
                self.rendered_lines.append(self.font.render(line, False, self.color))

        offset = self.render_position.y + (self.render_height - (sum([line.get_height() + 16 for line in self.rendered_lines]) - 16)) / 2
        for line in self.rendered_lines:
            surface.blit(line, (self.render_position.x + (self.render_width - line.get_width()) / 2, offset))
            offset += line.get_height() + 16
