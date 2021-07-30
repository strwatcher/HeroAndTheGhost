import pygame
import os
import traceback


def get_index(x, y, lvl_width):
    return y * lvl_width + x


def load_img(img_path, color_key=None) -> pygame.surface.Surface:
    full_path = os.path.join("res", img_path)
    img = None

    try:
        img = pygame.image.load(full_path)
    except (pygame.error, FileNotFoundError) as e:
        with open('logs.txt', 'w+') as logs:
            logs.write('Cannot load image with path: {}\n'.format(full_path))
            logs.write(traceback.format_exc())
            raise SystemExit(e)

    if color_key is not None:
        if color_key == -1:
            color_key = img.get_at((0, 0))
            img.set_colorkey(color_key)
    else:
        img = img.convert_alpha()
    return img
