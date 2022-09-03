import pygame

from colors import *
from fonts import get_fonts
from tile import Tile
from tile_group import TileGroup
from ui import Textfield, UIGroup


SCREEN_WIDTH = 384
SCREEN_HEIGHT = 256
BONUS_WORD = ''
BONUS_WORD_LENGTH = 2


def check_word_against_dictionaty(word: str) -> bool:
    print(f'Submit word: "{word}"')
    return True  # TODO: Add dictionary here


def choose_new_bonus_word() -> None:
    global BONUS_WORD
    global BONUS_WORD_LENGTH
    BONUS_WORD_LENGTH += 1
    BONUS_WORD = 'NEW' + ''.join(['W' for _ in range(BONUS_WORD_LENGTH - 3)])
    print(f'Bonus word is "{BONUS_WORD}" (length: {BONUS_WORD_LENGTH})')


def get_word_from_tiles(tiles: list[Tile]) -> str:
    return ''.join([t.letter for t in tiles]).upper()


def handle_mouse_down(tiles: TileGroup, selected: list[Tile]) -> list[Tile]:
    mouse_pos = pygame.mouse.get_pos()

    tiles_iter = iter(tiles)
    while True:
        try:
            tile = next(tiles_iter)
            if tile.collide_point(mouse_pos):
                selected = select_tile(tile, tiles, selected)
                return selected
        except StopIteration:
            return selected


def select_tile(clicked_tile: Tile, tiles: TileGroup,
                selected: list[Tile]) -> list[Tile]:
    if selected:
        if clicked_tile == selected[-1]:
            if len(selected) > 2:
                word = get_word_from_tiles(selected)
                if check_word_against_dictionaty(word):
                    if word == BONUS_WORD:
                        print('Bonus word!')
                        choose_new_bonus_word()
                    tiles.remove_selected()
                    return []
                else:
                    print(f'Word "{get_word_from_tiles(selected)}" ' \
                          'not in dictionary')
                tiles.deselect()
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

    bg_color = dark_gray
    fonts = get_fonts()

    choose_new_bonus_word()

    ui_group = UIGroup()
    ui_group.add(Textfield(label='bonus_label', font=fonts['small'],
                           initial_text='Bonus word', align='topright',
                           offset=(-10, 20), static=True))
    ui_group.add(Textfield(label='bonus_word', font=fonts['bold_sm'],
                           initial_text=BONUS_WORD, align='topright',
                           offset=(-10, 44)))

    tile_size = 64
    num_columns = 4
    num_rows = 4
    selected_tiles = []

    tiles = TileGroup(num_columns=num_columns)
    for col in range(num_columns):
        y_offset = tile_size / 2 - 6 if col % 2 else -2
        for row in range(num_rows):
            coords = (col * tile_size - col * 13,
                      row * tile_size - row * 8 + y_offset)
            tiles.add(
                Tile(tile_size=tile_size, coords=coords, column=col,
                     bg_color=bg_color, fonts=fonts))

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                selected_tiles = handle_mouse_down(tiles, selected_tiles)

        screen.fill(bg_color)

        tiles.update()
        for tile in tiles:
            screen.blit(tile.image, (tile.rect.x, tile.rect.y))

        for element in ui_group:
            screen.blit(element.image, (element.rect.x, element.rect.y))

        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Textagons")

    main()
