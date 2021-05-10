""" Texture-loading and texture-displaying set of tools.

Classes:
    - TextureType
    - Texture
    - TextureBook

Constants:
    - UI_SCALE
    - TILE_SIZE
"""

from json import loads
from enum import Enum
from time import time
from math import floor
from copy import copy
from pygame import Surface, image, transform, Rect
from source.core.tools import Position, Direction


UI_SCALE: float = 1.0
TILE_SIZE: int = 48


class TextureType(Enum):
    """
    The type of a specific texture.
    """
    UI = 0
    TILE = 1


class Texture:
    """
    A texture which can be loaded from a file and rendered on a surface.
    """
    def __init__(self, path: str, texture_type: TextureType, animated: bool = False, animation_duration: float = 1.0, frame_count: int = 1, loop_animation: bool = False) -> None:
        """
        :param path: The path of the image to load.
        :param texture_type: The type of the texture; this will determine how it is loaded.
        :param animated: If the texture must play an animation.
        :param animation_duration: The duration in seconds of the animation cycle.
        :param loop_animation: If the animation must repeat once it ends.
        """
        self.path = path
        self.surfaces: dict[Direction, Surface] = {}
        self.texture_type = texture_type

        self.animated = animated
        self.animation_duration = animation_duration
        self.frame_count = frame_count
        self.loop_animation = loop_animation
        self.animation_start = -1

        self.load()

    def load(self) -> None:
        """
        Loads the texture from the path specified at initialization.
        """
        original: Surface = image.load(self.path)
        if self.texture_type == TextureType.UI:
            original = transform.scale(
                original,
                (int(original.get_width() * UI_SCALE), int(original.get_height() * UI_SCALE))
            )
        elif self.texture_type == TextureType.TILE:
            original = transform.scale(
                original,
                (TILE_SIZE, int(original.get_height() / original.get_width() * TILE_SIZE))
            )
        else:
            print("not working")

        self.surfaces = {Direction(i): transform.rotate(original, -90 * i) for i in range(4)}

    def get_width(self) -> int:
        """ Get the width of the texture.

        :return: The width of the texture.
        """
        return list(self.surfaces.values())[0].get_width()

    def get_height(self) -> int:
        """ Get the height of the texture.

        :return: The height of the texture.
        """
        if self.animated:
            return list(self.surfaces.values())[0].get_height() // self.frame_count
        return list(self.surfaces.values())[0].get_height()

    def render(self, surface: Surface, position: Position, direction: Direction = Direction.NORTH) -> None:
        """ Renders the texture to the specified surface.

        :param surface: The surface on which to render the texture.
        :param position: The position on the surface where the texture will be rendered.
        :param direction: The direction towards which the texture will be oriented.
        """
        if not self.animated:
            surface.blit(self.surfaces[direction], (position.x, position.y))
            return

        if self.animation_start == -1:
            self.animation_start = time()

        frame = 0
        if self.loop_animation:
            frame = floor(self.frame_count / self.animation_duration * ((time() - self.animation_start) % self.animation_duration)) % self.frame_count
        elif time() - self.animation_start < self.animation_duration:
            frame = floor(self.frame_count / self.animation_duration * (time() - self.animation_start) % self.frame_count)

        frame_rect = Rect(0, 0, self.get_width(), self.get_height())
        if direction == Direction.NORTH:
            frame_rect.y = frame * self.get_height()
        elif direction == Direction.EAST:
            frame_rect.x = (self.get_height() * self.frame_count - self.get_height()) - frame * self.get_height()
            frame_rect.w = self.get_height()
            frame_rect.h = self.get_width()
        elif direction == Direction.SOUTH:
            frame_rect.y = (self.get_height() * self.frame_count - self.get_height()) - frame * self.get_height()
        elif direction == Direction.WEST:
            frame_rect.x = frame * self.get_height()
            frame_rect.w = self.get_height()
            frame_rect.h = self.get_width()

        surface.blit(self.surfaces[direction], (position.x, position.y), frame_rect)


class TextureBook:
    """
    A collection of textures, which can be loaded from a JSON file.
    """
    def __init__(self) -> None:
        self.book: dict[str, Texture] = {}

    def load(self, path: str) -> None:
        """ Loads textures from a JSON file.

        :param path: the path of the JSON file to load the textures from.
        """
        file = open(path, "r")
        data: dict = loads(file.read())
        file.close()

        for texture in data:
            texture_type = TextureType.TILE
            if data[texture]["type"] == "ui":
                texture_type = TextureType.UI

            if "animated" in data[texture] and data[texture]["animated"]:
                self.book[texture] = Texture(
                    data[texture]["path"],
                    texture_type,
                    data[texture]["animated"],
                    data[texture]["animation_duration"],
                    data[texture]["frame_count"],
                    data[texture]["loop_animation"]
                )
            else:
                self.book[texture] = Texture(data[texture]["path"], texture_type)

    def add(self, name: str, texture: Texture) -> None:
        """ Adds a texture to the book.

        :param name: The name by which the texture will be accessed.
        :param texture: The texture to be added to the book.
        """
        self.book[name] = texture

    def get(self, name: str) -> Texture:
        """ Get a texture from the book.

        :param name: The name of the desired texture.
        :return: The texture corresponding to the given name.
        """
        if self.book[name].animated:
            return copy(self.book[name])
        return self.book[name]
