"""
Classes:
    - DarkenerComponent
"""

from pygame import Surface, event, draw, Rect
from source.core.component import Component
from source.core.tools import Position


class DarkenerComponent(Component):
    """
    A dark surface used, for example, to darken the background.
    """
    def __init__(self, render_position: Position, render_width: int, render_height: int) -> None:
        """
        :param render_position: The position at which the dark surface starts.
        :param render_width: The width of the surface.
        :param render_height: The height of the surface.
        """
        super().__init__(render_position, render_width, render_height)

    def update(self, events: list[event.Event]) -> None:
        """ Updates the component with the latest events.

        :param events: The list of events lastly pulled.
        """
        pass

    def render(self, surface: Surface) -> None:
        """ Renders the dark surface to the specified surface.

        :param surface: The surface on which the dark surface has to be rendered.
        """
        draw.rect(surface, (0, 0, 0, 160), Rect(self.render_position.x, self.render_position.y, self.render_width, self.render_height))
