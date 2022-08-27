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


def calculate_hexagon_points(center_x: float, center_y: float,
                             radius: float) -> list[float]:
    points = []

    for a in range(6):
        points.append(
            (center_x + radius * math.cos(a * 60 * math.pi / 180),
             center_y + radius * math.sin(a * 60 * math.pi / 180))
        )

    return points


def draw_hexagon() -> pygame.Surface:
    '''
    Creates an antialiased hexagon inside a
    bounding box of size {{ tile_size }}.
    '''
    tile_size = 32
    hexagon = pygame.Surface((tile_size, tile_size))
    hexagon.fill(COLOR_REF['transparent'])

    # Draw outer orange shape
    points = calculate_hexagon_points(
        center_x=tile_size / 2, center_y=tile_size / 2,
        radius = tile_size / 2 - 2)
    pygame.gfxdraw.aapolygon(hexagon, points, COLOR_REF['orange'])
    pygame.gfxdraw.filled_polygon(hexagon, points, COLOR_REF['orange'])
    # Draw inner beige shape
    points = calculate_hexagon_points(
        center_x=tile_size / 2, center_y=tile_size / 2,
        radius = tile_size / 2 - 4)
    pygame.gfxdraw.aapolygon(hexagon, points, COLOR_REF['beige'])
    pygame.gfxdraw.filled_polygon(hexagon, points, COLOR_REF['beige'])

    hexagon.set_colorkey(COLOR_REF['transparent'])

    return hexagon


def main():
    screen_dims = (256, 256)
    screen = pygame.display.set_mode(screen_dims, pygame.SCALED)
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(COLOR_REF['mid_purple'])
        screen.blit(draw_hexagon(), (128 - 12, 128 - 12))

        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Hexagons")
    main()
