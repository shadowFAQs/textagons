import pygame

from tile import Tile


class TileGroup(pygame.sprite.Group):
    def __init__(self, num_columns: int) -> None:
        super().__init__()
        self.num_columns = num_columns

    def deselect(self) -> None:
        for tile in self.sprites():
            tile.deselect()

    def get_neighbors(self, tile: Tile) -> list[Tile]:
        return pygame.sprite.spritecollide(tile, self.sprites(), False)

    def get_tiles_above_tile(self, tile: Tile) -> list[Tile]:
        return [t for t in self.sprites() if t.column == tile.column \
                and t.rect.y < tile.rect.y]

    def is_all_at_target(self) -> bool:
        '''
        Checks if all tiles are on their Y target
        positions. Used for disabling input while
        tiles are falling.

        '''
        return all([t.rect.y == t.target_y for t in self.sprites()])

    def remove_selected(self) -> None:
        '''
        Counts the number of tiles in each column,
        sets these tiles' Y positions up off the
        screen, and adjusts Y positions according
        to the column counts. This way tiles aren't
        stacked on top of each other, and fall in
        columns rather than bunches.

        This method also sets new Y targets for
        the tiles above these, allowing them to
        drop down to their correct positions.
        '''
        selected_tiles_by_column = [0 for _ in range(self.num_columns)]
        for tile in [t for t in self.sprites() if t.selected]:
            for tile_above in self.get_tiles_above_tile(tile):
                if not tile_above.selected:
                    tile_above.target_y += tile_above.rect.h - 8

            selected_tiles_by_column[tile.column] += 1
            tile.remove(y_offset=selected_tiles_by_column[tile.column])
            tile.target_y = tile.rect.h / 2 - 6 if tile.column % 2 else -2
