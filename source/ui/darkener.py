"""
Classes:
    - DarkenerComponent
"""

from time import time
from pygame import Surface, event, draw, Rect
from source.core.component import Component
from source.core.tools import Position


class DarkenerComponent(Component):
    """
    A dark surface used, for example, to darken the background.
    """
    def __init__(self, render_position: Position, render_width: int, render_height: int, animated: bool = False, start: int = 0, end: int = 255, duration: float = 0.0) -> None:
        """
        :param render_position: The position at which the dark surface starts.
        :param render_width: The width of the surface.
        :param render_height: The height of the surface.
        """
        super().__init__(render_position, render_width, render_height)

        self.animated = animated
        self.start = start
        self.end = end
        self.duration = duration
        self.start_time = -1

    def update(self, events: list[event.Event]) -> None:
        """ Updates the component with the latest events.

        :param events: The list of events lastly pulled.
        """
        pass

    def render(self, surface: Surface) -> None:
        """ Renders the dark surface to the specified surface.

        :param surface: The surface on which the dark surface has to be rendered.
        """
        if not self.animated:
            draw.rect(surface, (0, 0, 0, 160), Rect(self.render_position.x, self.render_position.y, self.render_width, self.render_height))
            return

        if self.start_time == -1:
            self.start_time = time()

        value: int
        if time() - self.start_time >= self.duration:
            value = self.end - self.start
        else:
            value = int(((time() - self.start_time) / self.duration) * (self.end - self.start))

        draw.rect(surface, (0, 0, 0, self.start + value), Rect(self.render_position.x, self.render_position.y, self.render_width, self.render_height))
