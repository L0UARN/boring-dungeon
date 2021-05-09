"""
Classes:
    - InputComponent
"""

from pygame import Surface, event, draw, Rect
from pygame.font import Font
from external.text_input import TextInput
from source.core.component import Component
from source.core.tools import Position


class InputComponent(Component):
    def __init__(self, font: str, size: int, color: tuple[int, int, int], render_position: Position, render_width: int, render_height: int) -> None:
        """
        :param font: The path of the font to use.
        :param size: The size of the font.
        :param color: The color of the text.
        :param render_position: The position at which to render the text input.
        :param render_width: The width of the box. This value will limit the amount of characters it is possible to input.
        :param render_height: The height of the box.
        """
        super().__init__(render_position, render_width, render_height)

        self.color = color
        self.size = size

        char_length = Font(font, size).render(" ", False, (0, 0, 0)).get_width()
        self.text_input = TextInput(
            font_family=font,
            font_size=size,
            antialias=False,
            text_color=color,
            cursor_color=color,
            max_string_length=(render_width - 16) // char_length
        )

    def set_color(self, color: tuple[int, int, int]) -> None:
        """ Changes the color of the input and the text inside.

        :param color: The new color.
        """
        self.color = color
        self.text_input.set_text_color(color)
        self.text_input.set_cursor_color(color)

    def get_text(self) -> str:
        """ Get the text inputted.

        :return: The text present inside of the input.
        """
        return self.text_input.get_text()

    def update(self, events: list[event.Event]) -> None:
        """ Updates the input.

        :param events: A list of the lastly pulled events.
        """
        self.text_input.update(events)

    def render(self, surface: Surface) -> None:
        """ Renders the input to the specified surface.

        :param surface: The surface on which the input will be rendered.
        """
        draw.rect(surface, self.color, Rect(self.render_position.x, self.render_position.y, self.render_width, self.render_height), 2)
        surface.blit(self.text_input.surface, (self.render_position.x + 8, self.render_position.y + self.render_height - self.size - 8))
