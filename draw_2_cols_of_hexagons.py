import math

import pygame
from pygame import gfxdraw


COLOR_REF = {
    'beige': pygame.Color('#fee4cb'),
    'mid_purple': pygame.Color('#583dae'),
    'orange': pygame.Color('#f54b10'),
    'teal': pygame.Color('#32f9c0'),
    'transparent': pygame.Color('#ff00ff')
}


class Tile():

    def __init__(self, tile_size, coords):
        self.tile_size = tile_size
        self.draw_coords = coords
        self.surface = self.draw_hexagon()

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

    def draw_hexagon(self) -> pygame.Surface:
        '''
        Creates an antialiased hexagon inside a
        bounding box of size {{ self.tile_size }}.
        '''
        hexagon = pygame.Surface((self.tile_size, self.tile_size))
        hexagon.fill(COLOR_REF['transparent'])

        # Debug: Draw border
        # pygame.draw.rect(hexagon, COLOR_REF['teal'], pygame.Rect(0, 0, self.tile_size, self.tile_size), width=1)

        # # Draw outer orange shape
        points = self.calculate_hexagon_points(
            center_x=self.tile_size / 2, center_y=self.tile_size / 2,
            radius=self.tile_size / 2 - 4)
        pygame.gfxdraw.aapolygon(hexagon, points, COLOR_REF['orange'])
        pygame.gfxdraw.filled_polygon(hexagon, points, COLOR_REF['orange'])
        # # Draw inner beige shape
        points = self.calculate_hexagon_points(
            center_x=self.tile_size / 2, center_y=self.tile_size / 2,
            radius=self.tile_size / 2 - 8)
        pygame.gfxdraw.aapolygon(hexagon, points, COLOR_REF['beige'])
        pygame.gfxdraw.filled_polygon(hexagon, points, COLOR_REF['beige'])

        hexagon.set_colorkey(COLOR_REF['transparent'])

        return hexagon


def main():
    screen_dims = (256, 256)
    screen = pygame.display.set_mode(screen_dims)
    clock = pygame.time.Clock()

    tile_size = 64
    tiles = []
    for col in range(2):
        y_offset = tile_size / 2 - 4 if col % 2 else 0
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

        screen.fill(COLOR_REF['mid_purple'])
        for tile in tiles:
            screen.blit(tile.surface, tile.draw_coords)

        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Hexagons")
    main()
