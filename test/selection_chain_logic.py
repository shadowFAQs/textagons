import math
import pathlib
import random
from string import ascii_uppercase

import pygame
from pygame import gfxdraw
from shapely.geometry import Polygon, Point


COLOR_REF = {
    'bright_green': pygame.Color('#78e2a0'),
    'dark_gray': pygame.Color('#1f222a'),
    'light_gray': pygame.Color('#aaaaaa'),
    'mid_gray': pygame.Color('#75715e'),
    'teal': pygame.Color('#66d9ef'),
    'transparent': pygame.Color('#ff00ff'),
    'yellow': pygame.Color('#e6db74'),
}
LETTER_CHOICES = [c if c != 'Q' else 'Qu' for c in ascii_uppercase]

class Tile(pygame.sprite.Sprite):

    def __init__(self, tile_size, coords, bg_color):
        super().__init__()

        self.bg_color = bg_color
        self.image = pygame.Surface((tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=coords)
        self.collision_poly = None
        self.selected = False

        self.choose_letter()
        self.deselect()
        self.update()

    @staticmethod
    def calculate_hexagon_points(center_x: float, center_y: float,
                                 radius: float) -> list[float]:
        points = []

        for a in range(6):
            points.append(
                (center_x + radius * math.cos(a * 60 * math.pi / 180),
                 center_y + radius * math.sin(a * 60 * math.pi / 180))
            )

        return points

    def collide_point(self, point:tuple[float]) -> bool:
        return self.collision_poly.contains(Point(point))

    def choose_letter(self) -> None:
        self.letter = random.choice(LETTER_CHOICES)

    def deselect(self) -> None:
        self.selected = False
        self.border_color = COLOR_REF['light_gray']
        self.fill_color = COLOR_REF['dark_gray']
        self.text_color = COLOR_REF['light_gray']

    def draw_poly_and_set_collision(self) -> pygame.Surface:
        '''
        Creates an antialiased hexagon inside a
        bounding box of size {{ self.image.get_width() }}.
        '''
        tile_size = self.image.get_width()
        hexagon = pygame.Surface((tile_size, tile_size))
        hexagon.fill(self.bg_color)

        # Debug: Draw rect border
        # pygame.draw.rect(hexagon, COLOR_REF['teal'], pygame.Rect(0, 0, tile_size, tile_size), width=1)

        # Draw border hexagon
        points = self.calculate_hexagon_points(
            center_x=tile_size / 2, center_y=tile_size / 2,
            radius=tile_size / 2 - 4)
        pygame.gfxdraw.aapolygon(hexagon, points, self.border_color)
        pygame.gfxdraw.filled_polygon(hexagon, points, self.border_color)

        # Set collision poly from outer shape for mouse event handling
        self.set_collision_poly(points)

        # Draw inner hexagon
        points = self.calculate_hexagon_points(
            center_x=tile_size / 2, center_y=tile_size / 2,
            radius=tile_size / 2 - 8)
        pygame.gfxdraw.aapolygon(hexagon, points, self.fill_color)
        pygame.gfxdraw.filled_polygon(hexagon, points, self.fill_color)

        hexagon.set_colorkey(COLOR_REF['dark_gray'])

        return hexagon

    def select(self) -> None:
        self.selected = True
        self.border_color = COLOR_REF['bright_green']
        self.fill_color = COLOR_REF['dark_gray']
        self.text_color = COLOR_REF['bright_green']

    def set_collision_poly(self, points:list[tuple[float]]) -> None:
        updated_points = []
        for point in points:
            point_x = point[0] + self.rect.x
            point_y = point[1] + self.rect.y
            updated_points.append((point_x, point_y))
        self.collision_poly = Polygon(updated_points)

    def update(self) -> None:
        self.image = self.draw_poly_and_set_collision()

        # Smaller font for "Qu" tiles
        if self.letter == 'Qu':
            rendered = FONT_BOLD_SM.render(self.letter, True, self.text_color)
        else:
            rendered = FONT_BOLD.render(self.letter, True, self.text_color)

        tile_size = self.image.get_width()
        center_x = tile_size / 2 - rendered.get_width() / 2
        center_y = tile_size / 2 - rendered.get_height() / 2 + 2
        self.image.blit(rendered, (center_x, center_y))


class TileGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def deselect(self) -> None:
        for tile in self.sprites():
            tile.deselect()

    def get_neighbors(self, tile:Tile) -> list[Tile]:
        return pygame.sprite.spritecollide(tile, self.sprites(), False)


def handle_mouse_down(tiles:TileGroup, selected:list[Tile]) -> list[Tile]:
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


def select_tile(clicked_tile:Tile, tiles:TileGroup,
                selected:list[Tile]) -> list[Tile]:
    if selected:
        if clicked_tile == selected[-1]:
            if len(selected) > 2:
                submit_word(selected)
                tiles.deselect()
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


def submit_word(selected_tiles:list[Tile]) -> None:
    word = ''.join([t.letter for t in selected_tiles])
    print(f'Submit word: "{word}"')


def main():
    screen_dims = (256, 256)
    screen = pygame.display.set_mode(screen_dims)
    clock = pygame.time.Clock()

    bg_color = COLOR_REF['dark_gray']

    selected_tiles = []
    tile_size = 64
    tiles = TileGroup()
    for col in range(4):
        y_offset = tile_size / 2 - 6 if col % 2 else -2
        for row in range(4):
            coords = (col * tile_size - col * 13,
                      row * tile_size - row * 8 + y_offset)
            tiles.add(
                Tile(tile_size=tile_size, coords=coords, bg_color=bg_color))

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

        pygame.display.flip()


if __name__ == '__main__':
    global FONT_REG
    global FONT_BOLD

    pygame.init()
    pygame.display.set_caption("Textagons")

    font_filepath = pathlib.Path(__file__).parent.parent / 'fonts'
    FONT_REG = pygame.font.Font(font_filepath / 'Comfortaa-Regular.ttf', 32)
    FONT_BOLD = pygame.font.Font(font_filepath / 'Comfortaa-Bold.ttf', 32)
    FONT_BOLD_SM = pygame.font.Font(font_filepath / 'Comfortaa-Bold.ttf', 26)

    main()
