""" Texture-loading and texture-displaying set of tools.

Classes:
    - Texture
    - TileTexture
    - UITexture
    - TextureBook

Constants:
    - UI_SCALE
    - TILE_SIZE
"""

from abc import abstractmethod
from json import loads
from pygame import Surface, image, transform
from source.core.tools import Position, Direction


UI_SCALE: float = 1.0
TILE_SIZE: int = 48


class Texture:
    @abstractmethod
    def load(self, path: str) -> None:
        """ Loads the texture from a file.

        :param path: The path of the file to load the texture from.
        """

    @abstractmethod
    def render(self, surface: Surface, position: Position) -> None:
        """ Renders the texture to the surface.

        :param surface: The surface on which the texture has to be rendered.
        :param position: The position of the texture on the surface.
        """

    @abstractmethod
    def get_width(self) -> int:
        """ Get the width of the texture.

        :return: The width of the texture.
        """

    @abstractmethod
    def get_height(self) -> int:
        """ Get the height of the texture.

        :return: The height of the texture.
        """


class TileTexture(Texture):
    """
    A texture which is to be displayed as a tile in the game.
    """
    def __init__(self, path: str) -> None:
        """
        :param path: The path from which the texture will be loaded.
        """
        self.surfaces: dict[Direction, Surface] = {}
        self.load(path)

    def load(self, path: str) -> None:
        loaded: Surface = transform.scale(image.load(path), (TILE_SIZE, TILE_SIZE))
        self.surfaces = {Direction(i): transform.rotate(loaded, 90 * i) for i in range(0, 4)}

    def render(self, surface: Surface, position: Position) -> None:
        surface.blit(list(self.surfaces.values())[0], (position.x, position.y))

    def render_direction(self, surface: Surface, position: Position, direction: Direction) -> None:
        """ Renders the texture to the screen with a specific rotation.

        :param surface: The surface on which the texture has to be rendered.
        :param position: The position of the texture on the surface.
        :param direction: The direction in which the texture should be facing.
        """
        surface.blit(self.surfaces[direction], (position.x, position.y))

    def get_width(self) -> int:
        return TILE_SIZE

    def get_height(self) -> int:
        return TILE_SIZE


class UITexture(Texture):
    """
    A texture which is to be displayed as a part of the user interface.
    """
    def __init__(self, path: str) -> None:
        """
        :param path: The path from which the texture will be loaded.
        """
        self.surface: Surface = Surface((1, 1))
        self.load(path)

    def load(self, path: str) -> None:
        loaded: Surface = image.load(path)
        self.surface = transform.scale(loaded, (
            int(loaded.get_width() * UI_SCALE),
            int(loaded.get_height() * UI_SCALE)
        ))

    def render(self, surface: Surface, position: Position) -> None:
        surface.blit(self.surface, (position.x, position.y))

    def get_width(self) -> int:
        return self.surface.get_width()

    def get_height(self) -> int:
        return self.surface.get_height()


class TextureBook:
    """
    A collection of textures, which can be loaded from a JSON file.
    """
    def __init__(self) -> None:
        self.book: dict[str, Texture] = {}

    def load(self, path: str):
        """ Loads textures from a JSON file.

        :param path: the path of the JSON file to load the textures from.
        """
        file = open(path, "r")
        data: dict = loads(file.read())
        file.close()

        for texture in data:
            if data[texture]["type"] == "tile":
                self.book[texture] = TileTexture(data[texture]["path"])
            else:
                self.book[texture] = UITexture(data[texture]["path"])

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
        return self.book[name]
