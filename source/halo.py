"""
Classes:
    - HaloComponent
"""

from pygame import Surface, event, SRCALPHA, Rect
from source.core.component import Component
from source.core.tools import Position
from source.resources import TEXTURES as T


class HaloComponent(Component):
    """
    A halo of light visual effect.
    """
    def __init__(self, render_position: Position, render_width: int, render_height: int) -> None:
        """
        :param render_position: The position at which to render the halo.
        :param render_width: The width of the halo.
        :param render_height: The height of the halo.
        """
        super().__init__(render_position, render_width, render_height)
        self.buffer = Surface((1, 1))
        self.halo_texture = T.get("halo")
        self.pre_render()

    def pre_render(self) -> None:
        """
        Loads a buffer with the render of the darkening around the halo.
        """
        self.buffer = Surface((self.render_width, self.render_height), SRCALPHA)
        self.buffer.fill(list(self.halo_texture.surfaces.values())[0].get_at((0, 0)))

        self.buffer.fill((0, 0, 0, 0), Rect(
            (self.render_width - self.halo_texture.get_width()) // 2,
            (self.render_height - self.halo_texture.get_height()) // 2,
            self.halo_texture.get_width(),
            self.halo_texture.get_height()
        ))

    def update(self, events: list[event.Event]) -> None:
        """ Updates the halo's size if it has changed.

        :param events: A list of the lasted pulled events.
        """
        if self.buffer.get_width() != self.render_width or self.buffer.get_height() != self.render_height:
            self.pre_render()

    def render(self, surface: Surface) -> None:
        """ Renders the halo on the desired surface.

        :param surface: The surface on which to render the halo.
        """
        surface.blit(self.buffer, (self.render_position.x, self.render_position.y))
        self.halo_texture.render(surface, Position(
            (self.render_width - self.halo_texture.get_width()) // 2,
            (self.render_height - self.halo_texture.get_height()) // 2
        ))
