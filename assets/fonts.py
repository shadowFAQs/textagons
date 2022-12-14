from pathlib import Path

from pygame import font


def get_fonts() -> list[font.Font]:
    font_filepath = Path(__file__).parent / 'fonts'
    return {
        'regular': font.Font(font_filepath / 'Comfortaa-Regular.ttf', 32),
        'bold': font.Font(font_filepath / 'Comfortaa-Bold.ttf', 32),
        'bold_sm': font.Font(font_filepath / 'Comfortaa-Bold.ttf', 26),
        'small': font.Font(font_filepath / 'Comfortaa-Regular.ttf', 18),
        'mini': font.Font(font_filepath / 'Comfortaa-Regular.ttf', 12)
    }
