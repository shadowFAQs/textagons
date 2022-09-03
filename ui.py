import pygame

from assets.colors import *


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
        self.buffer_text = ''
        self.flash_timer = 0
        self.flash_timer_max = 120
        self.flash_color = teal

        self.set_text(initial_text)

    def animate_flash(self) -> None:
        if self.flash_timer:
            self.flash_timer -= 1
            if not self.flash_timer % 5:
                self.text_color = self.flash_color \
                    if self.text_color == light_gray else light_gray
            if not self.flash_timer:
                self.text = self.buffer_text
        else:
            self.text_color = light_gray

    def collide_point(self, point: tuple[float]) -> bool:
        return self.rect.collidepoint(point)

    def flash(self, flash_color: pygame.Color) -> None:
        self.flash_timer = self.flash_timer_max
        self.flash_color = flash_color

    def kill_flash(self) -> None:
        self.flash_timer = 0
        self.text_color = light_gray
        if self.buffer_text:
            self.text = self.buffer_text
        self.buffer_text = ''

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
        if self.label == 'current_word' and self.flash_timer:
            self.buffer_text = text
        else:
            self.text = str(text)
        self.update()

    def update(self) -> None:
        self.animate_flash()

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


class UIGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def post_init(self) -> Textfield:
        '''
        Convenience properties to easily access
        "Current" and "Bonus" word Textfields.
        '''
        for sprite in self.sprites():
            if sprite.label == 'bonus_word':
                self.bonus_word = sprite
            elif sprite.label == 'current_word':
                self.current_word = sprite

    def clear_text(self, textfield_label: str) -> None:
        textfield = [s for s in self.sprites() \
                     if s.label == textfield_label][0]
        textfield.set_text('')

    def flash(self, textfield_label: str, flash_color: pygame.Color) -> None:
        textfield = [s for s in self.sprites() \
                     if s.label == textfield_label][0]
        textfield.flash(flash_color)

    def update_textfield_by_label(self, label: str, text: str) -> None:
        textfield = [s for s in self.sprites() if s.label == label][0]
        textfield.set_text(text)
