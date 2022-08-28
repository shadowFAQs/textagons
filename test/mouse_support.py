import math
import pathlib
import random
from string import ascii_uppercase

import pygame
from pygame import gfxdraw
from shapely.geometry import Polygon, Point


COLOR_REF = {
    'beige': pygame.Color('#fee4cb'),
    'mid_purple': pygame.Color('#583dae'),
    'orange': pygame.Color('#f54b10'),
    'teal': pygame.Color('#32f9c0'),
    'transparent': pygame.Color('#ff00ff')
}
LETTER_CHOICES = [c if c != 'Q' else 'Qu' for c in ascii_uppercase]

class Tile(pygame.sprite.Sprite):

    def __init__(self, tile_size, coords):
        super().__init__()

        self.world_coords = coords
        self.image = pygame.Surface((tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.collision_poly = None

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
        self.border_color = COLOR_REF['orange']
        self.fill_color = COLOR_REF['beige']
        self.text_color = COLOR_REF['orange']

    def draw_poly_and_set_collision(self) -> pygame.Surface:
        '''
        Creates an antialiased hexagon inside a
        bounding box of size {{ self.image.get_width() }}.
        '''
        tile_size = self.image.get_width()
        hexagon = pygame.Surface((tile_size, tile_size))
        hexagon.fill(COLOR_REF['transparent'])

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

        hexagon.set_colorkey(COLOR_REF['transparent'])

        return hexagon

    def select(self) -> None:
        self.border_color = COLOR_REF['beige']
        self.fill_color = COLOR_REF['orange']
        self.text_color = COLOR_REF['beige']

    def set_collision_poly(self, points:list[tuple[float]]) -> None:
        updated_points = []
        for point in points:
            point_x = point[0] + self.world_coords[0]
            point_y = point[1] + self.world_coords[1]
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


def handle_mouse_down(tiles:list[Tile]) -> None:
    mouse_pos = pygame.mouse.get_pos()
    for tile in tiles:
        if tile.collide_point(mouse_pos):
            tile.select()
            return


def main():
    screen_dims = (256, 256)
    screen = pygame.display.set_mode(screen_dims)
    clock = pygame.time.Clock()

    tile_size = 64
    tiles = []
    for col in range(4):
        y_offset = tile_size / 2 - 6 if col % 2 else -2
        for row in range(4):
            coords = (col * tile_size - col * 13,
                      row * tile_size - row * 8 + y_offset)
            tiles.append(
                Tile(tile_size=tile_size, coords=coords))

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_down(tiles)

        screen.fill(COLOR_REF['mid_purple'])
        for tile in tiles:
            tile.update()
            screen.blit(tile.image, tile.world_coords)

        pygame.display.flip()


if __name__ == '__main__':
    global FONT_REG
    global FONT_BOLD

    pygame.init()
    pygame.display.set_caption("Hexagons")

    font_filepath = pathlib.Path(__file__).parent.parent / 'fonts'
    FONT_REG = pygame.font.Font(font_filepath / 'Comfortaa-Regular.ttf', 32)
    FONT_BOLD = pygame.font.Font(font_filepath / 'Comfortaa-Bold.ttf', 32)
    FONT_BOLD_SM = pygame.font.Font(font_filepath / 'Comfortaa-Bold.ttf', 26)

    main()
