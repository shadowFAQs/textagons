from pathlib import Path
from random import choice

import pygame

from assets.colors import *
from assets.fonts import get_fonts
from tile import Tile
from tile_group import TileGroup
from ui import Textfield, UIGroup, Button


'''
"Textagons" is an updated implementation of the
classic PopCap game "Bookworm".

The longest word in the dictionary is
"electroencephalographic", which has 23 letters.
R_VALUES is a baseline for the rarity of letters
in a bonus word, and has 22 "levels".
Each word in dictionary.txt, and therefore in
WORDS_WITH_R_VALUES, is listed in lowercase along
with its computed rarity; this keeps the game
from choosing overly easy/common bonus words.
'''


SCREEN_WIDTH = 525
SCREEN_HEIGHT = 425
BONUS_WORD = ''
BONUS_WORD_LENGTH = 2
SCORE = 0
DICTIONARY = []
LONGEST = ''
HIGHEST_SCORING = {}
WORDS_WITH_R_VALUES = []
R_VALUES = [0, 0, 0, 0.16, 0.22, 0.28, 0.36, 0.42, 0.48, 0.55, 0.61, 0.68,
            0.74, 0.8, 0.87, 0.93, 0.99, 1.07, 1.13, 1.28, 1.31, 1.38]


def add_word_to_history(tiles: list[Tile], score: int, is_bonus: bool) -> None:
    global LONGEST
    global HIGHEST_SCORING

    if len(tiles) > len(LONGEST):
        LONGEST = get_word_from_tiles(tiles)

    if HIGHEST_SCORING:
        if score > HIGHEST_SCORING['value']:
            colors = []
            for tile in tiles:
                if tile.type == 1:
                    colors.append(yellow if is_bonus else light_gray)
                else:
                    colors.append(tile.text_color)

            entry = {
                'letters': [t.letter.upper() for t in tiles],
                'colors': colors,
                'value': score
            }
            HIGHEST_SCORING = entry
    else:
        colors = []
        for tile in tiles:
            if tile.type == 1:
                colors.append(yellow if is_bonus else light_gray)
            else:
                colors.append(tile.text_color)

        entry = {
            'letters': [t.letter.upper() for t in tiles],
            'colors': colors,
            'value': score
        }
        HIGHEST_SCORING = entry


def check_word_against_dictionaty(word: str) -> bool:
    return word.lower() in DICTIONARY


def choose_new_bonus_word(ui_group) -> None:
    global BONUS_WORD
    global BONUS_WORD_LENGTH
    BONUS_WORD_LENGTH += 1
    word_pool = [w[0] for w in WORDS_WITH_R_VALUES \
                 if len(w[0]) == BONUS_WORD_LENGTH \
                 and w[1] > R_VALUES[BONUS_WORD_LENGTH]]
    BONUS_WORD = choice(word_pool).upper()
    ui_group.bonus_word.set_text(BONUS_WORD)
    ui_group.bonus_word.flash(yellow)


def get_word_from_tiles(tiles: list[Tile]) -> str:
    return ''.join([t.letter for t in tiles]).upper()


def get_clicked_menu_button(group: UIGroup) -> Button | None:
    mouse_pos = pygame.mouse.get_pos()

    try:
        buttons_iter = iter(group.restart_menu().buttons())
    except AttributeError:
        buttons_iter = iter(group.history().buttons())

    while True:
        try:
            button = next(buttons_iter)
            if button.collide_point(mouse_pos):
                return button
        except StopIteration:
            return None


def get_clicked_sprite(
    group: pygame.sprite.Group) -> pygame.sprite.Sprite | None:
    mouse_pos = pygame.mouse.get_pos()

    sprites_iter = iter(group)
    while True:
        try:
            sprite = next(sprites_iter)
            if sprite.collide_point(mouse_pos):
                return sprite
        except StopIteration:
            return None


def handle_left_mouse_down(
    ui_group: UIGroup, tiles: TileGroup,
    selected: list[Tile]) -> Textfield | Tile | None:
    button = get_clicked_sprite(ui_group)
    if button:
        return button

    return get_clicked_sprite(tiles)

def load_dictionary() -> None:
    global DICTIONARY
    global WORDS_WITH_R_VALUES

    filepath = Path(__file__).parent / 'assets'
    with open(filepath / 'dictionary.txt') as file:
        for line in file.read().split('\n'):
            entry = line.split(',')
            DICTIONARY.append(entry[0])
            WORDS_WITH_R_VALUES.append([entry[0], float(entry[1])])


def restart_game(tiles: TileGroup, ui_group: UIGroup) -> None:
    global BONUS_WORD
    global BONUS_WORD_LENGTH
    global SCORE

    SCORE = 0
    BONUS_WORD = ''
    BONUS_WORD_LENGTH = 2
    choose_new_bonus_word(ui_group)
    ui_group.update_textfield_by_label(label='score', text=0)

    tiles.deselect()
    tiles.scramble()
    tiles.set_type(1)

    ui_group.hide_restart_menu()


def score_tiles(tiles: list[Tile], bonus_mult: int) -> int:
    return sum([t.value for t in tiles]) * len(tiles) * bonus_mult


def update_selected_tiles(clicked_tile: Tile, tiles: TileGroup,
                          selected: list[Tile],
                          ui_group: UIGroup) -> list[Tile]:
    global SCORE

    if selected:
        if clicked_tile == selected[-1]:
            if len(selected) > 2:
                word = get_word_from_tiles(selected)
                if check_word_against_dictionaty(word):
                    bonus_mult = 1
                    if word == BONUS_WORD:
                        bonus_mult = 3
                        choose_new_bonus_word(ui_group)
                    delta = score_tiles(selected, bonus_mult)
                    SCORE += delta
                    ui_group.show_score_delta(delta=str(delta))
                    add_word_to_history(tiles=selected, score=delta,
                                        is_bonus=bonus_mult == 3)
                    tiles.remove_selected(word_length=len(word),
                                          is_bonus=bonus_mult == 3)
                    return []
                else:
                    tiles.deselect()
                    ui_group.current_word.flash_and_clear(red)
                    return []
            elif len(selected) == 1:
                clicked_tile.deselect()
                return []
        if clicked_tile.selected:
            index = selected.index(clicked_tile)
            for tile in selected[index + 1:]:
                tile.deselect()
            return selected[:index + 1]
        if clicked_tile in tiles.get_neighbors(selected[-1]):
            clicked_tile.select()
            selected.append(clicked_tile)
            return selected
        else:
            tiles.deselect()
            clicked_tile.select()
            return [clicked_tile]
    else:
        clicked_tile.select()
        return [clicked_tile]


def main() -> None:
    screen_dims = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(screen_dims)
    clock = pygame.time.Clock()
    menu_open = False
    tiles_ready = True
    game_over = False

    fonts = get_fonts()

    load_dictionary()
    ui_group = UIGroup(fonts)
    choose_new_bonus_word(ui_group)

    tile_size = 64
    num_columns = 7
    num_rows = 7
    selected_tiles = []

    tiles = TileGroup(num_columns=num_columns)
    for col in range(num_columns):
        y_offset = tile_size / 2 - 6 if col % 2 else -2
        for row in range(num_rows):
            coords = (col * tile_size - col * 13,
                      row * tile_size - row * 8 + y_offset)
            tiles.add(
                Tile(tile_size=tile_size, coords=coords, column=col,
                     fonts=fonts))

    tiles.scramble()
    tiles.set_type(1)

    running = True
    while running:
        clock.tick(60)

        tiles_ready = tiles.is_all_at_target()

        if game_over:
            menu_open = True
            ui_group.show_restart_menu(fonts=fonts, game_over=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_open:
                    button = get_clicked_menu_button(ui_group)
                    if button:
                        if button.label == 'restart_yes':
                            selected_tiles = []
                            restart_game(tiles, ui_group)
                        elif button.label == 'restart_no':
                            ui_group.hide_restart_menu()
                        elif button.label == 'close_history':
                            ui_group.hide_history()
                        menu_open = False
                else:
                    if event.button == 3 and tiles_ready:  # Right click
                        tile = get_clicked_sprite(tiles)
                        if tile:
                            tile.toggle_mark()

                    elif event.button == 1:  # Left click
                        clicked_sprite = handle_left_mouse_down(
                            ui_group, tiles, selected_tiles)

                        if type(clicked_sprite) == Tile and tiles_ready:
                            ui_group.current_word.kill_flash()
                            selected_tiles = update_selected_tiles(
                                clicked_sprite, tiles, selected_tiles,
                                ui_group)
                            ui_group.current_word.set_text(
                                get_word_from_tiles(selected_tiles),
                                max_size=8)
                            ui_group.update_textfield_by_label(label='score',
                                                               text=SCORE)
                        elif type(clicked_sprite) == Textfield:
                            if clicked_sprite.label == 'btn_history':
                                ui_group.show_history(LONGEST, HIGHEST_SCORING,
                                                      fonts=fonts)
                                menu_open = True
                            elif clicked_sprite.label == 'btn_scramble' \
                                and tiles_ready:
                                ui_group.clear_text('current_word')
                                tiles.scramble()
                                selected_tiles = []
                            elif clicked_sprite.label == 'btn_unmark':
                                tiles.unmark()
                            elif clicked_sprite.label == 'btn_restart':
                                menu_open = True
                                ui_group.show_restart_menu(fonts=fonts)

        screen.fill(dark_gray)

        game_over = tiles.update()

        for tile in tiles:
            screen.blit(tile.image, (tile.rect.x, tile.rect.y))

        ui_group.update()
        for element in ui_group:
            screen.blit(element.image, (element.rect.x, element.rect.y))

        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Textagons")

    main()

# TODO: Be able to submit with 2 tiles if 1 is "Qu"
# Actually handle Game Over
