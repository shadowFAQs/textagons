import pygame

from colors import *


class Textfield(pygame.sprite.Sprite):

    def __init__(self, label: str, font: pygame.font.Font, initial_text: str,
                 align: str, offset: tuple[float],
                 text_color: pygame.Color=light_gray,
                 static: bool=False, draw_border: bool=False) -> None:
        super().__init__()

        self.label = label
        self.font = font
        self.align = align
        self.offset = offset
        self.text_color = text_color
        self.static = static
        self.draw_border = draw_border

        self.set_text(initial_text)

    def collide_point(self, point: tuple[float]) -> bool:
        return self.rect.collidepoint(point)

    def set_alignment_and_rect(self, align: str, offset: tuple[float]) -> None:
        from main import SCREEN_WIDTH, SCREEN_HEIGHT
        screen_offset_x = SCREEN_WIDTH  - self.image.get_width() \
            if 'right' in align else 0
        screen_offset_y = SCREEN_HEIGHT - self.image.get_height() \
            if 'bottom' in align else 0

        self.rect = self.image.get_rect(
            topleft=(screen_offset_x + offset[0],
                     screen_offset_y + offset[1]))

    def set_text(self, text: str | int) -> None:
        self.text = str(text)

        if self.draw_border:
            text_surf = self.font.render(self.text, True, self.text_color)
            self.image = pygame.Surface(
                (text_surf.get_width() + 8, text_surf.get_height() + 8))
            self.image.fill(dark_gray)
            self.image.blit(text_surf, (4, 5))
        else:
            self.image = self.font.render(self.text, True, self.text_color)

        self.set_alignment_and_rect(self.align, self.offset)

        if self.draw_border:
            rect = pygame.Rect(0, 0, self.rect.w, self.rect.h)
            pygame.draw.rect(self.image, light_gray, rect, width=1,
                             border_radius=2)

    def update(self) -> None:
        pass


class UIGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def clear_text(self, textfield_label: str) -> None:
        textfield = [s for s in self.sprites() \
                     if s.label == textfield_label][0]
        textfield.set_text('')

    def update_text(self, textfield_label: str, text: str) -> None:
        textfield = [s for s in self.sprites() \
                     if s.label == textfield_label][0]
        textfield.set_text(text)
