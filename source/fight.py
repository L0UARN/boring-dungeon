"""
- Classes:
    - FightLayer
"""

from time import time
from pygame import event
from source.core.layer import Layer
from source.player import Player, FightingPlayerComponent
from source.enemy import Enemy, FightingEnemyComponent
from source.core.tools import Position
from source.ui.box import BoxComponent
from source.ui.text import TextComponent
from source.resources import TEXTURES as T
from source.core.texture import TextureComponent


class FightLayer(Layer):
    """
    The view of a fight between the player and an enemy.
    """
    def __init__(self, player: Player, enemy: Enemy, width: int, height: int) -> None:
        """
        :param player: The player fighting.
        :param enemy: The enemy the player will fight.
        :param width: The width of the screen.
        :param height: The height of the screen.
        """
        super().__init__(False, width, height)
        self.start_time = time()
        self.end_time = -1
        self.ended = False

        self.background = TextureComponent(Position(0, 0), T.get("fight"))
        self.title_text = TextComponent("resources/font.ttf", 48, (255, 255, 255), Position(0, int(height * 0.10)), width, 56, True, 16.0)
        self.title_text.set_text(["Ready..."])

        self.player_display = FightingPlayerComponent(player, enemy, Position(0, 0))
        self.player_display.can_attack = False
        self.player_display.render_position = Position(
            width // 4 - self.player_display.render_width // 2,
            (height - self.player_display.render_height) // 2
        )
        self.player_box = BoxComponent(Position(
            self.player_display.render_position.x - 160,
            self.player_display.render_position.y + int(self.player_display.render_height * 1.5)
        ), self.player_display.render_width + 320, 256)
        self.player_text = TextComponent("resources/font.ttf", 24, (0, 0, 0), Position(
            self.player_display.render_position.x - 160,
            self.player_display.render_position.y + int(self.player_display.render_height * 1.5)
        ), self.player_display.render_width + 320, 256)
        self.player_text.set_text([
            "PLAYER",
            f"Health: {player.health}/{player.max_health}",
            f"Speed: {player.speed - player.inventory.get_equipped_weight()}"
        ])

        self.enemy_display = FightingEnemyComponent(enemy, player, Position(0, 0))
        self.enemy_display.can_attack = False
        self.enemy_display.render_position = Position(
            width // 4 * 3 - self.enemy_display.render_width // 2,
            (height - self.enemy_display.render_height) // 2
        )
        self.enemy_box = BoxComponent(Position(
            self.enemy_display.render_position.x - 160,
            self.enemy_display.render_position.y + int(self.enemy_display.render_height * 1.5)
        ), self.enemy_display.render_width + 320, 256)
        self.enemy_text = TextComponent("resources/font.ttf", 24, (0, 0, 0), Position(
            self.enemy_display.render_position.x - 160,
            self.enemy_display.render_position.y + int(self.enemy_display.render_height * 1.5)
        ), self.enemy_display.render_width + 320, 256, True, 12.0)
        self.enemy_text.set_text([
            "ENEMY",
            f"Health: {enemy.health}/{enemy.max_health}",
            f"Speed: {enemy.speed - enemy.inventory.get_equipped_weight()}"
        ])

        self.add_component("background", self.background)
        self.add_component("title", self.title_text)
        self.add_component("player_display", self.player_display)
        self.add_component("player_box", self.player_box)
        self.add_component("player_text", self.player_text)
        self.add_component("enemy_display", self.enemy_display)
        self.add_component("enemy_box", self.enemy_box)
        self.add_component("enemy_text", self.enemy_text)

    def update(self, events: list[event.Event]) -> None:
        """ Updates the ongoing fight.

        :param events: A list of the lastly pulled events.
        """
        super().update(events)

        if time() - self.start_time >= 3.0 and self.end_time == -1:
            self.player_display.can_attack = True
            self.enemy_display.can_attack = True

            if time() - self.player_display.player.last_attack <= 0.35:
                self.player_display.render_position = Position(
                    self.width // 4 - self.player_display.render_width // 2 + int(-16384 * (time() - self.player_display.player.last_attack - 0.177) ** 2 + 512),
                    (self.height - self.player_display.render_height) // 2
                )
            else:
                self.player_display.render_position = Position(
                    self.width // 4 - self.player_display.render_width // 2,
                    (self.height - self.player_display.render_height) // 2
                )

            if time() - self.enemy_display.enemy.last_attack <= 0.35:
                self.enemy_display.render_position = Position(
                    self.width // 4 * 3 - self.enemy_display.render_width // 2 - int(-16384 * (time() - self.enemy_display.enemy.last_attack - 0.177) ** 2 + 512),
                    (self.height - self.enemy_display.render_height) // 2
                )
            else:
                self.enemy_display.render_position = Position(
                    self.width // 4 * 3 - self.enemy_display.render_width // 2,
                    (self.height - self.enemy_display.render_height) // 2
                )

            self.title_text.animated = False
            self.title_text.set_text(["Fight!"])

            self.player_text.set_text([
                "PLAYER",
                f"Health: {self.player_display.player.health}/{self.player_display.player.max_health}",
                f"Speed: {self.player_display.player.speed - self.player_display.player.inventory.get_equipped_weight()}"
            ])

            self.enemy_text.animated = False
            self.enemy_text.set_text([
                "ENEMY",
                f"Health: {self.enemy_display.enemy.health}/{self.enemy_display.enemy.max_health}",
                f"Speed: {self.enemy_display.enemy.speed - self.enemy_display.enemy.inventory.get_equipped_weight()}"
            ])

        if self.end_time == -1:
            if self.player_display.player.health == 0:
                self.lock_component("player_display")
                self.title_text.set_text(["You lost..."])
                self.end_time = time()
            elif self.enemy_display.enemy.health == 0:
                self.lock_component("enemy_display")
                self.title_text.set_text(["You won!"])
                self.end_time = time()

        if self.end_time != -1 and time() - self.end_time >= 2.0:
            self.ended = True
