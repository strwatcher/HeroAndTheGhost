import traceback

import pygame
import os
from typing import *


def get_index(x, y, lvl_width):
    return y * lvl_width + x


def load_img(img_path, color_key=None) -> pygame.surface.Surface:
    full_path = os.path.join("res", img_path)
    img = None

    try:
        img = pygame.image.load(full_path).convert()
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


class Game:
    def __init__(self):
        self.display = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self.tile_size = (64, 64)
        self.map_size = (20, 20)
        self.tile_image = load_img(os.path.join('env', 'water-tile.png'))
        self.tile_map = TileMap(self.tile_size, self.map_size, self.tile_image)

        self.tile_group = self.tile_map.tiles

        self.tile_group.draw(self.display)
        while True:
            pygame.display.flip()


class Animation:
    def __init__(self, sheet: pygame.surface.Surface, sheet_size: Tuple[int, int], sprite_size: Tuple[int, int]):
        columns, rows = sheet_size

        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        self.frames: List[pygame.surface.Surface] = list()

        self.cut_sheet(sheet, sheet_size, sprite_size)

        self.cur_frame_index = -1
        self.__cur_frame = None
        self.next_frame()

    def cut_sheet(self, sheet: pygame.surface.Surface, sheet_size: Tuple[int, int], sprite_size: Tuple[int, int]):
        columns, rows = sheet_size
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)

                frame = pygame\
                    .transform\
                    .scale(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)), sprite_size)

                self.frames.append(frame)

    def next_frame(self):
        self.cur_frame_index = (self.cur_frame_index + 1) % len(self.frames)
        self.__cur_frame = self.frames[self.cur_frame_index]

    @property
    def cur_frame(self):
        return self.__cur_frame


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self,
                 animations: List[Tuple[pygame.surface.Surface, str, int, int]],
                 default_animation_name: str,
                 groups: Tuple[pygame.sprite.Group],
                 # Probably need to add pos to AnimatedSprite
                 ):
        super().__init__(*groups)

        self.animations: Dict[str, Animation] = dict()
        self.read_animations(animations)

        self.cur_animation = self.animations.get(default_animation_name)
        self.cur_frame = self.cur_animation.cur_frame

    def read_animations(self, animations: List[Tuple[pygame.surface.Surface, str, int, int]]):
        for anim in animations:
            sheet, key, *size = anim
            animation = Animation(sheet, size)
            self.animations.update({key: animation})


class StaticSprite(pygame.sprite.Sprite):
    def __init__(self, size: Tuple[int, int], pos: Tuple[int, int], image: pygame.surface.Surface, groups: Tuple):
        super().__init__(*groups)
        self.width, self.height = self.size = size
        self.x, self.y = self.pos = pos
        self.image = pygame.transform.scale(image, self.size)
        self.rect = image.get_rect().move(self.width * self.x, self.height * self.y)


class Entity:
    def __init__(self):
        pass


class Player(Entity):
    def __init__(self):
        super().__init__()


class Warrior(Player):
    def __init__(self):
        super().__init__()


class Enemy(Entity):
    def __init__(self):
        super().__init__()


class Tile(StaticSprite):
    # need to create entity game_object and add possibility to create tiles with animation
    def __init__(self, size: Tuple[int, int], pos: Tuple[int, int], image: pygame.surface.Surface, groups: Tuple):
        super().__init__(size, pos, image, groups)


class TileMap:
    def __init__(self, tile_size: Tuple[int, int], map_markup: Tuple[int, int], image):
        self.__tiles = pygame.sprite.Group()

        self.tile_size = tile_size
        self.width, self.height = map_markup
        self.image = image

        self.fill_map()

        tile_width, tile_height = tile_size
        self.map_size = self.width * tile_width, self.height * tile_height

    def fill_map(self):
        for i in range(self.height):
            for j in range(self.width):
                Tile(self.tile_size, (j, i), self.image, (self.__tiles, ))

    @property
    def tiles(self):
        return self.__tiles


# Create common class for menus
class MainMenu:
    def __init__(self):
        pass


class RestartMenu:
    def __init__(self):
        pass


if __name__ == '__main__':
    pygame.init()
    Game()
