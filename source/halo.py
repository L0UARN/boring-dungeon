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
    def __init__(self, render_position: Position, render_width: int, render_height: int):
        super().__init__(render_position, render_width, render_height)
        self.buffer = Surface((1, 1))
        self.pre_render()

    def pre_render(self) -> None:
        self.buffer = Surface((self.render_width, self.render_height), SRCALPHA)
        halo_texture = T.get("halo")

        self.buffer.fill(halo_texture.surface.get_at((0, 0)))

        self.buffer.fill((0, 0, 0, 0), Rect(
            (self.render_width - halo_texture.get_width()) // 2,
            (self.render_height - halo_texture.get_height()) // 2,
            halo_texture.get_width(),
            halo_texture.get_height()
        ))

        halo_texture.render(self.buffer, Position(
            (self.render_width - halo_texture.get_width()) // 2,
            (self.render_height - halo_texture.get_height()) // 2
        ))

    def update(self, events: list[event.Event]) -> None:
        if self.buffer.get_width() != self.render_width or self.buffer.get_height() != self.render_height:
            self.pre_render()

    def render(self, surface: Surface) -> None:
        surface.blit(self.buffer, (self.render_position.x, self.render_position.y))
