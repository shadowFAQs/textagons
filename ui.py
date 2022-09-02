import pygame

from colors import *


class Textfield(pygame.sprite.Sprite):

    def __init__(self, label: str, font: pygame.font.Font, initial_text: str,
                 align: str, offset: tuple[float],
                 text_color: pygame.Color=light_gray,
                 static: bool=False) -> None:
        super().__init__()

        self.label = label
        self.font = font
        self.align = align
        self.offset = offset
        self.text_color = text_color
        self.static = static

        self.set_text(initial_text)

    def set_alignment(self, align: str, offset: tuple[float]) -> None:
        from main import SCREEN_WIDTH, SCREEN_HEIGHT
        screen_offset_x = SCREEN_WIDTH  - self.image.get_width() \
            if 'right' in align else 0
        screen_offset_y = SCREEN_HEIGHT - self.image.get_height() \
            if 'bottom' in align else 0
        self.rect = self.image.get_rect(
            topleft=(screen_offset_x + offset[0],
                     offset[1]))

    def set_text(self, text: str) -> None:
        self.text = text
        self.image = self.font.render(self.text, True, self.text_color)
        self.set_alignment(self.align, self.offset)

    def update(self) -> None:
        pass


class UIGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()
