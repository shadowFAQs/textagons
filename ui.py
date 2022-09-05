import pygame

from assets.colors import *


class Menu(pygame.sprite.Sprite):

    def __init__(self, label: str, dimensions: tuple[int],
        offset: tuple[float]) -> None:
        super().__init__()

        self.label = label
        self.dimensions = dimensions
        self.offset = offset

        self.image = pygame.Surface(dimensions)
        self.rect = self.image.get_rect(topleft=offset)

        self.elements = []

    def add_button(self, text: str, coords: tuple[int],
                   font=pygame.font.Font,
                   color: pygame.Color=light_gray) -> None:
        text_surf = font.render(text, True, color)
        element = {
            'image': pygame.Surface(
                (text_surf.get_width() + 8, text_surf.get_height() + 8))
        }
        element['image'].fill(dark_gray)
        element['image'].blit(text_surf, (4, 5))
        element['rect'] = element['image'].get_rect(bottomleft=coords)
        border = pygame.Rect(0, 0, element['rect'].w, element['rect'].h)
        pygame.draw.rect(element['image'], color, border, width=1,
                         border_radius=2)

        self.elements.append(element)

    def add_centered_text(self, text: str, menu_dims: tuple[int],
                 font: pygame.font.Font,
                 color: pygame.Color=light_gray) -> None:
        element = {
            'image': font.render(text, True, color)
        }
        coords = (menu_dims[0] / 2 - element['image'].get_width() / 2, 20)
        element['rect'] = element['image'].get_rect(topleft=coords)

        self.elements.append(element)

    def update(self) -> None:
        self.image.fill(dark_gray)
        border = pygame.Rect(0, 0, self.rect.w, self.rect.h)
        pygame.draw.rect(self.image, light_gray, border, width=1)

        for element in self.elements:
            self.image.blit(element['image'], (element['rect'].x,
                                               element['rect'].y))


class Textfield(pygame.sprite.Sprite):

    def __init__(self, label: str, font: pygame.font.Font, initial_text: str,
                 align: str, offset: tuple[float],
                 text_color: pygame.Color=light_gray,
                 static: bool=False, draw_border: bool=False,
                 border_color: pygame.Color=light_gray) -> None:
        super().__init__()

        self.label = label
        self.font = font
        self.align = align
        self.offset = offset
        self.default_text_color = text_color
        self.static = static
        self.draw_border = draw_border
        self.border_color = border_color
        self.buffer_text = None
        self.flash_timer = 0
        self.flash_timer_max = 120
        self.flash_color = teal

        self.set_text(initial_text)

    def animate_flash(self) -> None:
        if self.flash_timer:
            self.flash_timer -= 1
            if not self.flash_timer % 5:
                self.text_color = self.flash_color \
                    if self.text_color == light_gray \
                    else self.default_text_color
            if not self.flash_timer:
                if self.buffer_text is not None:
                    self.text = self.buffer_text
                    self.buffer_text = None
        else:
            self.text_color = self.default_text_color

    def collide_point(self, point: tuple[float]) -> bool:
        return self.rect.collidepoint(point)

    def flash(self, flash_color: pygame.Color) -> None:
        self.flash_timer = self.flash_timer_max
        self.flash_color = flash_color

    def flash_and_clear(self, flash_color: pygame.Color) -> None:
        self.flash_timer = self.flash_timer_max
        self.flash_color = flash_color
        self.buffer_text = ''

    def kill_flash(self) -> None:
        self.flash_timer = 0
        self.text_color = light_gray

    def set_alignment_and_rect(self, align: str, offset: tuple[float]) -> None:
        from main import SCREEN_WIDTH, SCREEN_HEIGHT
        screen_offset_x = SCREEN_WIDTH  - self.image.get_width() \
            if 'right' in align else 0
        screen_offset_y = SCREEN_HEIGHT - self.image.get_height() \
            if 'bottom' in align else 0

        self.rect = self.image.get_rect(
            topleft=(screen_offset_x + offset[0],
                     screen_offset_y + offset[1]))

    def set_text(self, text: str | int, max_size: int = 99) -> None:
        '''
        Converts { text } to a str, truncates it
        if it's longer than 9 characters, and
        displays it.

        The "current word" textfield retains its
        text for a couple seconds after it's
        cleared so it can flash red to show that
        the entry wasn't in the dictionary. To
        allow for this, the new (empty) string is
        temporarily stored in { buffer_text }
        until { flash_timer } expires.
        '''
        text = str(text)

        if len(text) > max_size:
            text = f'{text[:3]}...{text[-3:]}'

        if self.label == 'current_word' and self.flash_timer:
            self.buffer_text = text
        else:
            self.text = text
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
            border = pygame.Rect(0, 0, self.rect.w, self.rect.h)
            pygame.draw.rect(self.image, self.border_color, border, width=1,
                             border_radius=2)


class UIGroup(pygame.sprite.Group):

    def __init__(self, fonts: list[pygame.font.Font]):
        super().__init__()

        # Score display
        self.add(Textfield(label='score_label', font=fonts['small'],
                           initial_text='Score', align='topright',
                           offset=(-10, 5), static=True))
        self.add(Textfield(label='score', font=fonts['bold_sm'],
                           initial_text=0, align='topright', offset=(-10, 29)))
        self.add(Textfield(label='score_delta', font=fonts['bold_sm'],
                           initial_text='', align='topright',
                           offset=(-75, 1), text_color=green))

        # Bonus word display
        self.add(Textfield(label='bonus_label', font=fonts['small'],
                           initial_text='Bonus word', align='topright',
                           offset=(-10, 71), static=True))
        self.add(Textfield(label='bonus_word', font=fonts['bold_sm'],
                           initial_text='', align='topright',
                           offset=(-10, 95)))

        # Currently selected word
        self.add(Textfield(label='current_word_label', font=fonts['small'],
                           initial_text='Current word', align='topright',
                           offset=(-10, 137), static=True))
        self.add(Textfield(label='current_word', font=fonts['bold_sm'],
                           initial_text='', align='topright',
                           offset=(-10, 161)))

        # Unmark button
        self.add(Textfield(label='btn_unmark', font=fonts['small'],
                           initial_text='UNMARK', align='bottomright',
                           offset=(-10, -86), static=True, draw_border=True))

        # Scramble button
        self.add(Textfield(label='btn_scramble', font=fonts['small'],
                           initial_text='SCRAMBLE', align='bottomright',
                           offset=(-10, -48), static=True, draw_border=True))

        # Restart button
        self.add(Textfield(label='btn_restart', font=fonts['small'],
                           initial_text='RESTART', align='bottomright',
                           offset=(-10, -10), text_color=red, static=True,
                           draw_border=True, border_color=red))

        # Convenience properties to easily access
        # "Current" and "Bonus" word Textfields.
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

    def show_score_delta(self, delta: str) -> None:
        textfield = [s for s in self.sprites() \
                     if s.label == 'score_delta'][0]
        textfield.set_text(f'+{delta}')
        textfield.flash_and_clear(green)

    def show_start_menu(self, fonts: list[pygame.font.Font],
                        restart: bool=False) -> None:
        dimensions = (261, 150)
        self.add(Menu(label='start_menu', dimensions=dimensions,
                      offset=(55, 132)))
        start_menu = self.start_menu()
        start_menu.add_centered_text(
            text=f'{"Res" if restart else "S"}tart game?',
            font=fonts['bold_sm'], menu_dims=dimensions)
        start_menu.add_button(text='YES', coords=(70, 112),
                              font=fonts['small'], color=red)
        start_menu.add_button(text='NO', coords=(155, 112),
                              font=fonts['small'])

    def start_menu(self) -> Menu | None:
        try:
            return [s for s in self.sprites() if s.label == 'start_menu'][0]
        except IndexError:
            return None

    def update_textfield_by_label(self, label: str, text: str) -> None:
        textfield = [s for s in self.sprites() if s.label == label][0]
        textfield.set_text(text)
