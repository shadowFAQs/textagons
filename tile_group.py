from random import choice

import pygame

from tile import Tile


class TileGroup(pygame.sprite.Group):

    def __init__(self, num_columns: int) -> None:
        super().__init__()
        self.num_columns = num_columns

    @staticmethod
    def roll_for_crystal_tile(word_length: int) -> int:
        '''
        Check if the submitted word will result
        in a crystal tile being created. If so,
        this method will return the index of that
        tile among selected tiles; otherwise it
        will return 99.

        * Words shorter than 5 letters will not
        produce a crystal tile.

        '''                  # Odds of crystal tile
                             # --------------------
        if word_length < 5:       # 0%
            return 99

        match word_length:
            case 5:               # 40%
                roll_target = 13
            case 6:               # 70%
                roll_target = 7
            case 7:               # 90%
                roll_target = 6   # 100%
            case _:
                return choice(range(word_length))

        if choice(range(20)) + 1 >= roll_target:
            return choice(range(word_length))
        else:
            return 99

    @staticmethod
    def roll_for_fire_tile(word_length: int) -> int:
        '''
        Check if the submitted word will result
        in a fire tile being created. If so, this
        method will return the index of that tile
        among selected tiles; otherwise it will
        return 99.

        * Words longer than 5 letters never
        produce a fire tile.
        * 5-letter words have a 5% chance to
        produce a fire tile, up to 80% for
        3-letter words.
        '''
        match word_length:
            case 3:
                roll_target = 4
            case 4:
                roll_target = 17
            case 5:
                roll_target = 20
            case _:
                return 99

        if choice(range(20)) + 1 >= roll_target:
            return choice(range(word_length))
        else:
            return 99

    def bottom_row(self) -> list[Tile]:
        return [t for t in self.sprites() if not self.get_tiles_below_tile(t)]

    def burn_down(self, fire_tile: Tile) -> bool:
        '''
        Causes individual fire tiles to burn
        through their neighbors below.

        Also checks for and returns "Game Over"
        condition and returns that as a boolean.
        '''
        fire_tile.burn_ready = False

        if self.get_tiles_below_tile(fire_tile):
            tiles_below = self.get_tiles_below_tile(fire_tile)
            if tiles_below:
                self.remove_tile(tiles_below[0])
                return False
        else:
            return True  # Game over

    def deselect(self) -> None:
        for tile in self.sprites():
            tile.deselect()

    def fire_tiles(self) -> list[Tile]:
        return [t for t in self.sprites() if t.type == 0]

    def get_neighbors(self, tile: Tile) -> list[Tile]:
        return pygame.sprite.spritecollide(tile, self.sprites(), False)

    def get_tiles_above_tile(self, tile: Tile) -> list[Tile]:
        '''
        Returns a list of tiles in the same
        column as {{ tile }}, with lower Y
        values, sorted so that the tile directly
        above {{ tile }} is at index 0.
        '''
        tiles = [t for t in self.sprites() if t.column == tile.column \
                and t.rect.y < tile.rect.y]
        return sorted(tiles, key=lambda tile: tile.rect.y, reverse=True)

    def get_tiles_below_tile(self, tile: Tile) -> list[Tile]:
        '''
        Returns a list of tiles in the same
        column as {{ tile }}, with higher Y
        values, sorted so that the tile directly
        below {{ tile }} is at index 0.
        '''
        tiles = [t for t in self.sprites() if t.column == tile.column \
                and t.rect.y > tile.rect.y]
        return sorted(tiles, key=lambda tile: tile.rect.y)

    def is_all_at_target(self) -> bool:
        '''
        Checks if all tiles are at their Y target
        positions. Used for disabling input while
        tiles are falling.

        '''
        return all([t.rect.y == t.target_y for t in self.sprites()])

    def remove_selected(self, word_length: int, is_bonus: bool) -> None:
        '''
        Checks {{ word_length }} to see if
        special tile types should be created. A
        crystal tile and a fire tile will not be
        created at the same time. A fire tile
        will not be created if the player has
        just submitted the bonus word.

        Also sets fire tiles ready to burn down,
        but bypasses any that have just been
        created, or whose neighbor tile directly
        below was just submitted in a word.
        '''
        crystal_tile_index = self.roll_for_crystal_tile(word_length)
        if crystal_tile_index == 99 and not is_bonus:
            fire_tile_index = self.roll_for_fire_tile(word_length)
        else:
            fire_tile_index = 99

        bypassed_fire_tiles = []

        for index, tile in enumerate(self.selected()):
            tiles_above = self.get_tiles_above_tile(tile)
            if tiles_above:
                tile_above = tiles_above[0]
                if tile_above.type == 0:
                    bypassed_fire_tiles.append(tile_above)

            self.remove_tile(tile)

            if index == crystal_tile_index:
                tile.set_type(2)
            elif index == fire_tile_index:
                tile.set_type(0)
                bypassed_fire_tiles.append(tile)

        self.set_fire_tiles_ready(bypassed=bypassed_fire_tiles)

    def remove_tile(self, tile: Tile) -> None:
        '''
        Moves a tile up off the top of the screen
        to "remove" it. If there are other tiles
        already up there, we back this tile up
        farther so the "new" tiles don't fall in
        a bunch.
        '''
        tile.remove()

        while len(pygame.sprite.spritecollide(
            tile, self.sprites(), dokill=False)) > 1:
            tile.rect.move_ip((0, -32))

    def scramble(self) -> None:
        '''
        Changes all tiles' letters. Raises tiles
        in the bottom row up 8px, causing a
        "bump" animation to occur across all
        tiles on the board.
        Scrambling also has a 90% chance to
        create a fire tile in the top row. These
        tiles will not replace crystal or
        existing fire tiles.
        New fire tiles will not burn down through
        their neighbors on the first turn they
        appear.
        '''
        for tile in self.bottom_row():
            tile.rect.y -= 8  # Bump animation

        for tile in self.sprites():
            tile.scramble()

        top_row_tiles = [t for t in self.top_row() if t.type == 1]
        bypassed = []
        if choice(range(10)) >= 2:
            fire_tile = top_row_tiles[choice(range(len(top_row_tiles)))]
            fire_tile.set_type(0)
            bypassed = [fire_tile]

        self.set_fire_tiles_ready(bypassed=bypassed)

    def selected(self) -> None:
        return [t for t in self.sprites() if t.selected]

    def set_fire_tiles_ready(self, bypassed: list[Tile] | None = None) -> None:
        bypassed = [] if bypassed is None else bypassed

        for fire_tile in self.fire_tiles():
            if not fire_tile in bypassed:
                if self.will_burn_down(fire_tile, self.selected()):
                    fire_tile.burn_ready = True

    def set_type(self, tile_type: int) -> None:
        for tile in self.sprites():
            tile.set_type(tile_type)

    def top_row(self) -> list[Tile]:
        return [t for t in self.sprites() if not self.get_tiles_above_tile(t)]

    def update(self) -> bool:
        '''
        Called every frame.
        Calls update() for each tile, updates Y
        target positions, checks if bottom row
        fire tiles will burn through the "floor",
        resulting in a Game Over state, and
        handles the flashing effect for these
        bottom row fire tiles.
        '''
        game_over = False

        self.update_tile_targets()

        for fire_tile in self.fire_tiles():
            fire_tile.flash_fire = not bool(
                self.get_tiles_below_tile(fire_tile)) and \
                fire_tile.rect.y == fire_tile.target_y
            if fire_tile.rect.y == fire_tile.target_y and fire_tile.burn_ready:
                burn_through_bottom_row = self.burn_down(fire_tile)
                if burn_through_bottom_row and not game_over:
                    game_over = True

        super().update()  # Calls update() for all child sprites

        return game_over

    def update_tile_targets(self) -> None:
        '''
        Sets "floor" targets for tiles in the
        bottom row, then sets all above these
        accordingly so they stack up.
        '''
        bottom_row = self.bottom_row()
        for tile in bottom_row:
            y_offset = tile.rect.h / 2 - 6 if tile.column % 2 else -2
            tile.target_y = 6 * tile.rect.h - 48 + y_offset

        for tile in [t for t in self.sprites() if t not in bottom_row]:
            tile.target_y = self.get_tiles_below_tile(tile)[0].rect.y \
                - (tile.rect.h - 8)

    def will_burn_down(self, tile: Tile, selected: list[Tile]) -> bool:
        '''
        Checks if a fire tile will burn through
        its neighbor below. Fire tiles will not
        burn through crystal tiles or other fire
        tiles.
        Returns False if the fire tile in
        question is selected, since it will be
        removed before the "burn down phase" is
        reached.
        Returns True if the fire tile has no
        neighbor below, since a fire tile burning
        through the bottom row ends the game.
        '''
        if not tile.type == 0 or tile in selected:
            return False

        try:
            return self.get_tiles_below_tile(tile)[0].type == 1
        except IndexError:
            return True

    def unmark(self) -> None:
        for tile in self.sprites():
            tile.marked = False
