"""
Classes:
    - BoxComponent
"""

from pygame import Surface, SRCALPHA, event
from source.core.component import Component
from source.core.tools import Position, Direction
from source.resources import TEXTURES as T


class BoxComponent(Component):
    """
    A dynamic-sized box, for UI purposes.
    """
    def __init__(self, render_position: Position, render_width: int, render_height: int) -> None:
        super().__init__(render_position, int(render_width), int(render_height))
        self.buffer = Surface((int(render_width), int(render_height)), SRCALPHA)

        self.corner_texture = T.get("box_corner")
        self.side_texture = T.get("box_side")
        self.inside_texture = T.get("box_inside")

        self.pre_render()

    def pre_render(self) -> None:
        """
        Renders the box to an internal buffer, in order to minimize the time it takes to render it every frame (because
        rendering a box with the adapted size is quite slow to do).
        """
        self.buffer.fill((0, 0, 0, 0))

        self.corner_texture.render(self.buffer, Position(0, 0), Direction.NORTH)
        self.corner_texture.render(self.buffer, Position(self.render_width - self.corner_texture.get_width(), 0), Direction.EAST)
        self.corner_texture.render(self.buffer, Position(self.render_width - self.corner_texture.get_width(), self.render_height - self.corner_texture.get_height()), Direction.SOUTH)
        self.corner_texture.render(self.buffer, Position(0, self.render_height - self.corner_texture.get_height()), Direction.WEST)

        for i in range(self.corner_texture.get_width(), self.render_width - self.corner_texture.get_width(), self.side_texture.get_width()):
            self.side_texture.render(self.buffer, Position(i, 0), Direction.NORTH)
        for i in range(self.corner_texture.get_height(), self.render_height - self.corner_texture.get_height(), self.side_texture.get_width()):
            self.side_texture.render(self.buffer, Position(self.render_width - self.corner_texture.get_height(), i), Direction.EAST)
        for i in range(self.corner_texture.get_height(), self.render_height - self.corner_texture.get_height(), self.side_texture.get_width()):
            self.side_texture.render(self.buffer, Position(0, i), Direction.WEST)
        for i in range(self.corner_texture.get_width(), self.render_width - self.corner_texture.get_width(), self.side_texture.get_width()):
            self.side_texture.render(self.buffer, Position(i, self.render_height - self.corner_texture.get_height()), Direction.SOUTH)

        for x in range(self.corner_texture.get_width(), self.render_width - self.corner_texture.get_width(), self.inside_texture.get_width()):
            for y in range(self.corner_texture.get_height(), self.render_height - self.corner_texture.get_height(), self.inside_texture.get_height()):
                self.inside_texture.render(self.buffer, Position(x, y))

    def update(self, events: list[event.Event]) -> None:
        """ Updates the box and re-renders it if the size has changed.

        :param events: A list of the lastly pulled events.
        """
        if self.render_width != self.buffer.get_width() or self.render_height != self.buffer.get_height():
            self.pre_render()

    def render(self, surface: Surface) -> None:
        """ Renders the box to the specified surface.

        :param surface: The surface on which to render the box.
        """
        surface.blit(self.buffer, (self.render_position.x, self.render_position.y))
