""" Tools used on game components.

Classes:
    - Component
"""

from abc import abstractmethod
from pygame import event, Surface
from source.core.tools import Position


class Component:
    """ A component represents a game element which is to be displayed on-screen, such as an UI element or the player
    representation.
    """
    def __init__(self, render_position: Position, render_width: int, render_height: int) -> None:
        """
        :param render_position: The position on the surface on which the component has to be rendered.
        :param render_width: A hint to the width of the rendered component.
        :param render_height: A hint to the height of the rendered component.
        """
        self.render_position = render_position
        self.render_width = render_width
        self.render_height = render_height

    @abstractmethod
    def update(self, events: list[event.Event]) -> None:
        """ Updates the component with the latest events.

        :param events: The list of events lastly pulled.
        """
        pass

    @abstractmethod
    def render(self, surface: Surface) -> None:
        """ Renders the visual elements of the component to the screen.

        :param surface: The surface on which the elements have to be rendered.
        """
        pass
