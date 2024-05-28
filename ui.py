import pygame

from typing import Optional

from assets.colors import *


class Button(pygame.sprite.Sprite):
    """
    Class for button sprites embedded in menus. The clickable, bordered text boxes on the main screen are
    Textfield instances.
    """

    def __init__(self, label: str, text: str, coords: tuple[int], offset: tuple[float], font: pygame.font.Font,
                 color: pygame.Color=light_gray):
        super().__init__()

        self.label = label
        self.text = text
        self.coords = coords
        self.parent_offset = offset
        self.font = font
        self.text_color = color

    def collide_point(self, point: tuple[float]) -> bool:
        """ References self.parent_offset since Buttons are placed inside Menu sprites. """
        return self.rect.collidepoint((point[0] - self.parent_offset[0], point[1] - self.parent_offset[1]))

    def update(self):
        """
        A Button's size is determined by the dimensions of {{ self.text }} as rendered in {{ self.font }}, plus 8px of
        width and 8px of height.
        """
        text_surf = self.font.render(self.text, True, self.text_color)
        self.image = pygame.Surface((text_surf.get_width() + 8,
                                     text_surf.get_height() + 8))
        self.image.fill(dark_gray)
        self.rect = self.image.get_rect(bottomleft=self.coords)

        border = pygame.Rect(0, 0, self.rect.w, self.rect.h)
        pygame.draw.rect(self.image, self.text_color, border, width=1, border_radius=2)
        self.image.blit(text_surf, (4, 5))


class Textfield(pygame.sprite.Sprite):
    """
    Class for static and dynamic text boxes. May be responsive to click events or not. All of the "buttons" on the
    main screen are actually instances of this class.
    """

    def __init__(self, label: str, font: pygame.font.Font, initial_text: str, align: str, offset: tuple[float],
                 text_color: pygame.Color=light_gray, static: bool=False, draw_border: bool=False,
                 border_color: pygame.Color=light_gray, small_font: pygame.font.Font=None):
        super().__init__()

        self.label = label
        self.font = font
        self.align = align
        self.offset = offset
        self.default_text_color = text_color
        self.static = static
        self.draw_border = draw_border
        self.border_color = border_color
        self.small_font = small_font
        self.buffer_text = None
        self.current_font = self.font
        self.flash_timer = 0
        self.flash_timer_max = 120
        self.flash_color = teal
        self.screen_offset = None

        self.set_text(initial_text)

    def animate_flash(self):
        """
        Counts down {{ self.flash_timer }}, changing the Textfield's text color every 5 frames. Sets text to
        {{ self.buffer_text }} when the timer reaches 0.
        """
        if self.flash_timer:
            self.flash_timer -= 1
            if not self.flash_timer % 5:
                self.text_color = self.flash_color if self.text_color == light_gray else self.default_text_color
            if not self.flash_timer:
                if self.buffer_text is not None:
                    self.text = self.buffer_text
                    self.buffer_text = None
        else:
            self.text_color = self.default_text_color

    def clear(self):
        self.set_text('')

    def collide_point(self, point: tuple[float]) -> bool:
        """ Not really needed, but keeps Textfield in line with Tile. """
        return self.rect.collidepoint(point)

    def flash(self, flash_color: pygame.Color):
        """ Turns on flashing text. """
        self.flash_timer = self.flash_timer_max
        self.flash_color = flash_color

    def flash_and_clear(self, flash_color: pygame.Color):
        """
        Turns on flashing text and loads an empty string into {{ self.buffer_text }}, clearing the Textfield
        after the flash timer reaches 0.
        """
        self.flash_timer = self.flash_timer_max
        self.flash_color = flash_color
        self.buffer_text = ''

    def kill_flash(self):
        self.flash_timer = 0
        self.text_color = light_gray

    def set_alignment_and_rect(self, align: str, offset: tuple[float]):
        from main import SCREEN_WIDTH, SCREEN_HEIGHT

        screen_offset_x = SCREEN_WIDTH - self.image.get_width() if 'right' in align else 0
        screen_offset_y = SCREEN_HEIGHT - self.image.get_height() if 'bottom' in align else 0

        self.rect = self.image.get_rect(topleft=(screen_offset_x + offset[0], screen_offset_y + offset[1]))

    def set_text(self, text: str | int, max_size: int = 99, resize: bool = False):
        """
        Converts {{ text }} to a str, truncates it if it's longer than {{ max_size }}, and displays it.
        The "current word" textfield retains its text for a couple seconds after it's cleared so it can flash red to
        show that the entry wasn't in the dictionary. To allow for this, the new (empty) string is temporarily stored
        in {{ self.buffer_text }} until the flash timer expires.
        """
        text = str(text)
        if len(text) > max_size:
            if resize:
                self.current_font = self.small_font
            else:
                text = f'{text[:3]}...{text[-3:]}'

        if self.label == 'current_word' and self.flash_timer:
            self.buffer_text = text
        else:
            self.text = text

        self.update()

    def update(self):
        self.animate_flash()

        if self.draw_border:
            text_surf = self.current_font.render(self.text, True, self.text_color)
            self.image = pygame.Surface((text_surf.get_width() + 8, text_surf.get_height() + 8))
            self.image.fill(dark_gray)
            self.image.blit(text_surf, (4, 5))
        else:
            self.image = self.current_font.render(self.text, True, self.text_color)

        self.set_alignment_and_rect(self.align, self.offset)

        if self.draw_border:
            border = pygame.Rect(0, 0, self.rect.w, self.rect.h)
            pygame.draw.rect(self.image, self.border_color, border, width=1, border_radius=2)


class Menu(pygame.sprite.Sprite):
    """
    Class for "modal" style popup menus, which can contain multicolored text and buttons.
    Each sprite contained within a Menu is stored in its {{ elements }} list; this list is iterated over every frame
    for drawing.
    """

    def __init__(self, label: str, dimensions: tuple[int],
        offset: tuple[float]):
        super().__init__()

        self.label = label
        self.dimensions = dimensions
        self.offset = offset

        self.image = pygame.Surface(dimensions)
        self.rect = self.image.get_rect(topleft=offset)

        self.elements = []

    def add_button(self, label: str, text: str, coords: tuple[int], font: pygame.font.Font,
                   color: pygame.Color=light_gray):
        self.elements.append(Button(label, text, coords, self.offset, font, color))

    def add_multicolor_text(self, text_obj: dict, font: pygame.font.Font, coords: tuple[int]):
        """
        Special method to support "Highest scoring" words in the history menu; these are displayed with each letter
        the color of the tile type (bonus, crystal, etc.) when it was submitted.
        """
        x_offset = 0
        for index, letter in enumerate(text_obj['letters']):
            self.elements.append(Textfield(label='', font=font, initial_text=letter, align='topleft',
                                           offset=(coords[0] + x_offset, coords[1]),
                                           text_color=text_obj['colors'][index]))
            x_offset += self.elements[-1].rect.w

        value_text = f' ({text_obj["value"]} pts)'
        self.elements.append(Textfield(label='', font=font, initial_text=value_text, align='topleft',
                                       offset=(coords[0] + x_offset, coords[1])))

    def add_text(self, text: str, coords: tuple[int], font: pygame.font.Font, color: pygame.Color=light_gray):
        self.elements.append(Textfield(label='', font=font, initial_text=text, align='topleft', offset=coords))

    def add_centered_text(self, text: str, font: pygame.font.Font, y_position: int=20, color: pygame.Color=light_gray):
        temp = font.render(text, True, color)
        offset = (self.rect.w / 2 - temp.get_width() / 2, y_position)
        self.elements.append(Textfield(label='', font=font, initial_text=text, align='topleft', offset=offset))

    def buttons(self) -> list[Button]:
        return [e for e in self.elements if isinstance(e, Button)]

    def update(self):
        self.image.fill(dark_gray)
        border = pygame.Rect(0, 0, self.rect.w, self.rect.h)
        pygame.draw.rect(self.image, light_gray, border, width=1)

        for element in self.elements:
            element.update()
            self.image.blit(element.image, (element.rect.x, element.rect.y))


class UIGroup(pygame.sprite.Group):
    """ Class to store and manipulate the Textfield objects shown on the main game screen. """

    def __init__(self, fonts: list[pygame.font.Font]):
        super().__init__()

        # Score display
        self.add(Textfield(label='score_label', font=fonts['small'], initial_text='Score', align='topright',
                           offset=(-10, 5), static=True))
        self.add(Textfield(label='score', font=fonts['bold_sm'], initial_text=0, align='topright', offset=(-10, 29)))
        self.add(Textfield(label='score_delta', font=fonts['bold_sm'], initial_text='', align='topright',
                           offset=(-75, 1), text_color=green))

        # Bonus word display
        self.add(Textfield(label='bonus_label', font=fonts['small'], initial_text='Bonus word', align='topright',
                           offset=(-10, 71), static=True))
        self.add(Textfield(label='bonus_word', font=fonts['bold_sm'], initial_text='', align='topright',
                           offset=(-10, 95), small_font=fonts['small']))

        # Currently selected word
        self.add(Textfield(label='current_word_label', font=fonts['small'], initial_text='Current word',
                           align='topright', offset=(-10, 137), static=True))
        self.add(Textfield(label='current_word', font=fonts['bold_sm'], initial_text='', align='topright',
                           offset=(-10, 161)))

        # History
        self.add(Textfield(label='btn_history', font=fonts['small'], initial_text='HISTORY', align='bottomright',
                           offset=(-10, -124), static=True, draw_border=True))

        # Unmark button
        self.add(Textfield(label='btn_unmark', font=fonts['small'], initial_text='UNMARK', align='bottomright',
                           offset=(-10, -86), static=True, draw_border=True))

        # Scramble button
        self.add(Textfield(label='btn_scramble', font=fonts['small'], initial_text='SCRAMBLE', align='bottomright',
                           offset=(-10, -48), static=True, draw_border=True))

        # Restart button
        self.add(Textfield(label='btn_restart', font=fonts['small'], initial_text='RESTART', align='bottomright',
                           offset=(-10, -10), text_color=red, static=True, draw_border=True, border_color=red))

    def bonus_word(self) -> Textfield:
        return [e for e in self.sprites() if e.label == 'bonus_word'][0]

    def current_word(self) -> Textfield:
        return [e for e in self.sprites() if e.label == 'current_word'][0]

    def flash(self, textfield_label: str, flash_color: pygame.Color):
        textfield = [s for s in self.sprites() if s.label == textfield_label][0]
        textfield.flash(flash_color)

    def game_over_menu(self) -> Optional[Menu]:
        try:
            return [s for s in self.sprites() if s.label == 'game_over_menu'][0]
        except IndexError:
            return None

    def hide_menus(self):
        self.remove(self.history())
        self.remove(self.restart_menu())
        self.remove(self.game_over_menu())

    def history(self) -> Optional[Menu]:
        try:
            return [s for s in self.sprites() if s.label == 'history'][0]
        except IndexError:
            return None

    def restart_menu(self) -> Optional[Menu]:
        try:
            return [s for s in self.sprites() if s.label == 'restart_menu'][0]
        except IndexError:
            return None

    def score(self) -> Textfield:
        return [e for e in self.sprites() if e.label == 'score'][0]

    def show_game_over_menu(self, longest_word: str, highest_scoring: dict, fonts: list[pygame.font.Font]):
        menu_dimensions = (261, 220)
        self.add(Menu(label='game_over_menu', dimensions=menu_dimensions, offset=(55, 132)))
        menu = self.game_over_menu()
        menu.add_centered_text(text='Game over', font=fonts['bold_sm'])

        menu.add_text(text='Longest word', font=fonts['mini'], coords=(10, 70))

        if longest_word:
            menu.add_text(text=longest_word, font=fonts['small'], coords=(25, 86))
        else:
            menu.add_text(text='...', font=fonts['small'], coords=(25, 86))
        menu.add_text(text='Highest scoring word', font=fonts['mini'], coords=(10, 120))

        if highest_scoring:
            menu.add_multicolor_text(text_obj=highest_scoring, font=fonts['small'], coords=(25, 136))
        else:
            menu.add_text(text='...', font=fonts['small'], coords=(25, 136))

        menu.add_button(label='restart_yes', text='RESTART', coords=(88, 204), font=fonts['small'])

    def show_history(self, longest_word: str, highest_scoring: dict, fonts: list[pygame.font.Font]):
        dimensions = (300, 180)
        self.add(Menu(label='history', dimensions=dimensions, offset=(40, 119)))
        history = self.history()

        history.add_centered_text(text='Word history', font=fonts['bold_sm'], y_position=10)
        history.add_text(text='Longest word', font=fonts['mini'], coords=(10, 50))

        if longest_word:
            history.add_text(text=longest_word, font=fonts['small'], coords=(25, 66))
        else:
            history.add_text(text='...', font=fonts['small'], coords=(25, 66))

        history.add_text(text='Highest scoring word', font=fonts['mini'], coords=(10, 100))
        if highest_scoring:
            history.add_multicolor_text(text_obj=highest_scoring, font=fonts['small'], coords=(25, 116))
        else:
            history.add_text(text='...', font=fonts['small'], coords=(25, 116))

        history.add_button(label='close_history', text='CLOSE', coords=(220, 174), font=fonts['small'])

    def show_restart_menu(self, fonts: list[pygame.font.Font]):
        menu_dimensions = (261, 150)

        self.add(Menu(label='restart_menu', dimensions=menu_dimensions, offset=(55, 132)))

        restart_menu = self.restart_menu()
        restart_menu.add_centered_text(text='Restart game?', font=fonts['bold_sm'])
        restart_menu.add_button(label='restart_yes', text='YES', coords=(70, 112), font=fonts['small'], color=red)
        restart_menu.add_button(label='restart_no', text='NO', coords=(155, 112), font=fonts['small'])

    def show_score_delta(self, delta: str):
        """ Show timed "+X" text next to score display. """
        textfield = [s for s in self.sprites() if s.label == 'score_delta'][0]
        textfield.set_text(f'+{delta}')
        textfield.flash_and_clear(green)
