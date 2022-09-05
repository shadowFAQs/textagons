from pathlib import Path
from random import choice

import pygame

from assets.colors import *
from assets.fonts import get_fonts
from tile import Tile
from tile_group import TileGroup
from ui import Textfield, UIGroup


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
WORDS_WITH_R_VALUES = []
R_VALUES = [0, 0, 0, 0.16, 0.22, 0.28, 0.36, 0.42, 0.48, 0.55, 0.61, 0.68,
            0.74, 0.8, 0.87, 0.93, 0.99, 1.07, 1.13, 1.28, 1.31, 1.38]


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
    click_enabled = True
    tiles_ready = True


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

    running = True
    while running:
        clock.tick(60)

        tiles_ready = tiles.is_all_at_target()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if click_enabled:

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
                            if clicked_sprite.label == 'btn_scramble' \
                                and tiles_ready:
                                ui_group.clear_text('current_word')
                                tiles.scramble()
                                selected_tiles = []

        screen.fill(dark_gray)

        tiles.update()
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
