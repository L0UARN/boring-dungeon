""" Resources used in the game, as constants.

Constants:
    - TEXTURES
"""

from source.core.texture import TextureBook


TEXTURES = TextureBook()
TEXTURES.load("resources/textures.json")
