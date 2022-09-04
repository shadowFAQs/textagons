import math
from random import choices
from string import ascii_uppercase

import pygame
from pygame import gfxdraw
from shapely.geometry import Polygon, Point

from assets.colors import *


LETTER_CHOICES = [c if c != 'Q' else 'Qu' for c in ascii_uppercase]
LETTER_WEIGHTS = { 'A': 0.09, 'B': 0.02, 'C': 0.02, 'D': 0.04, 'E': 0.12,
                   'F': 0.02, 'G': 0.03, 'H': 0.02, 'I': 0.09, 'J': 0.01,
                   'K': 0.01, 'L': 0.04, 'M': 0.03, 'N': 0.06, 'O': 0.08,
                   'P': 0.02, 'Qu': 0.01, 'R': 0.06, 'S': 0.05, 'T': 0.06,
                   'U': 0.04, 'V': 0.02, 'W': 0.02, 'X': 0.01, 'Y': 0.02,
                   'Z': 0.01 }


class Tile(pygame.sprite.Sprite):

    def __init__(self, tile_size: int, coords: tuple[float], column: int,
                 fonts: list[pygame.font.Font]) -> None:
        super().__init__()

        self.fonts = fonts
        self.image = pygame.Surface((tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=coords)
        self.column = column
        self.ay = 0
        self.border_color = light_gray
        self.burn_ready = False
        self.collision_poly = None
        self.fill_color = dark_gray
        self.flash_fire = False
        self.flash_timer = 0
        self.flash_timer_max = 5
        self.marked = False
        self.selected = False
        self.target_y = self.rect.y
        self.text_color = light_gray
        self.type = 1
        self.value = 0

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

    def collide_point(self, point: tuple[float]) -> bool:
        return self.collision_poly.contains(Point(point))

    def choose_letter(self) -> None:
        weights = [LETTER_WEIGHTS[l] for l in LETTER_CHOICES]
        self.letter = choices(population=LETTER_CHOICES,
                              weights=weights, k=1)[0]
        self.value = self.lookup_letter_value(self.letter)

    def deselect(self) -> None:
        self.selected = False

    def draw_poly_and_set_collision(self) -> pygame.Surface:
        '''
        Creates an antialiased hexagon inside a
        bounding box of size {{ self.image.get_width() }}.
        '''
        tile_size = self.image.get_width()
        hexagon = pygame.Surface((tile_size, tile_size))
        hexagon.fill(dark_gray)

        # Draw border hexagon
        if self.selected:
            self.border_color = green
        else:
            if self.marked:
                self.border_color = yellow
            elif self.type == 2:
                self.border_color = teal
            else:
                self.border_color = light_gray

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

        hexagon.set_colorkey(dark_gray)

        return hexagon

    def lookup_letter_value(self, letter: str) -> int:
        '''
        Crystal tiles are worth 2x normal value.
        Fire tiles are always worth 0 points.
        '''
        match letter:
            case 'A' | 'E' | 'I' | 'L' | 'N' | 'O' | 'R' | 'S' | 'T' | 'U':
                return 1 * self.type
            case 'D' | 'G':
                return 2 * self.type
            case 'B' | 'C' | 'M' | 'P':
                return 3 * self.type
            case 'F' | 'H' | 'V' | 'W' | 'Y':
                return 4 * self.type
            case 'K':
                return 5 * self.type
            case 'J' | 'X':
                return 8 * self.type
            case _:
                return 10 * self.type

    def move_toward_target(self) -> None:
        if self.rect.y < self.target_y:
            self.ay += .35
            self.rect.move_ip((0, self.ay))
        if self.rect.y >= self.target_y:
            self.ay = 0
            self.rect.y = self.target_y

    def remove(self) -> None:
        '''
        Resets tile state, chooses a new letter,
        and moves up off the top of the screen.
        '''
        self.rect.move_ip(
            (0, self.rect.y * -1 - self.rect.h))
        self.set_type(1)
        self.burn_ready = False
        self.scramble()

    def scramble(self) -> None:
        self.deselect()
        self.marked = False
        if not self.type == 0:  # Fire tiles can't be scrambled away
            self.choose_letter()

        if self.type == 2:
            self.set_type(1)

        self.update()

    def select(self) -> None:
        self.selected = True

    def set_collision_poly(self, points: list[tuple[float]]) -> None:
        updated_points = []
        for point in points:
            point_x = point[0] + self.rect.x
            point_y = point[1] + self.rect.y
            updated_points.append((point_x, point_y))
        self.collision_poly = Polygon(updated_points)

    def set_type(self, tile_type: int) -> None:
        self.type = tile_type

        match tile_type:
            case 0:
                self.text_color = red
            case 1:
                self.text_color = light_gray
            case 2:
                self.text_color = teal

    def update(self) -> None:
        self.image = self.draw_poly_and_set_collision()

        if self.type == 0 and self.flash_fire:
            self.flash_timer += 1
            if self.flash_timer == self.flash_timer_max:
                self.flash_timer = 0
                self.text_color = red \
                    if self.text_color == yellow else yellow

        # Smaller font for "Qu" tiles
        if self.letter == 'Qu':
            rendered = self.fonts['bold_sm'].render(self.letter, True,
                                                    self.text_color)
        else:
            rendered = self.fonts['bold'].render(self.letter, True,
                                                 self.text_color)

        tile_size = self.image.get_width()
        center_x = tile_size / 2 - rendered.get_width() / 2
        center_y = tile_size / 2 - rendered.get_height() / 2 + 2
        self.image.blit(rendered, (center_x, center_y))

        self.move_toward_target()

    def toggle_mark(self) -> None:
        if not self.selected:
            self.marked = not self.marked
