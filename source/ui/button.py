"""
Classes:
    - ButtonComponent
"""

from pygame import Surface, event, draw, Rect, mouse, MOUSEBUTTONDOWN
from source.core.component import Component
from source.core.tools import Position


class ButtonComponent(Component):
    """
    A clickable button.
    """
    def __init__(self, color, render_position: Position, render_width: int, render_height: int) -> None:
        """
        :param color: The color of the button.
        :param render_position: The position at which the button will be rendered.
        :param render_width: The width of the button.
        :param render_height: The height of the button.
        """
        super().__init__(render_position, render_width, render_height)
        self.color = color
        self.is_hovered = False
        self.is_clicked = False

    def set_color(self, color: tuple[int, int, int]) -> None:
        """ Changes the color of the button.

        :param color: The new color.
        """
        self.color = color

    def update(self, events: list[event.Event]) -> None:
        """ Updates the button.

        :param events: A list of the lastly pulled events.
        """
        for e in events:
            if e.type == MOUSEBUTTONDOWN:
                mouse_position = mouse.get_pos()
                if self.render_position.x < mouse_position[0] < self.render_position.x + self.render_width:
                    if self.render_position.y < mouse_position[1] < self.render_position.y + self.render_height:
                        self.is_clicked = True

        mouse_position = mouse.get_pos()
        if self.render_position.x <= mouse_position[0] <= self.render_position.x + self.render_width and \
           self.render_position.y <= mouse_position[1] <= self.render_position.y + self.render_height:
            self.is_hovered = True
        else:
            self.is_hovered = False

    def render(self, surface: Surface) -> None:
        """ Renders the button to the specified surface.

        :param surface: The surface on which the button will be rendered.
        """
        if self.is_hovered:
            draw.rect(surface, self.color, Rect(self.render_position.x, self.render_position.y, self.render_width, self.render_height))
        else:
            draw.rect(surface, self.color, Rect(self.render_position.x, self.render_position.y, self.render_width, self.render_height), 2)