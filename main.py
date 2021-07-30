import sys
import traceback

import pygame
import os
from typing import *

pygame.init()

UP = pygame.Vector2(0, -1)
DOWN = pygame.Vector2(0, 1)
RIGHT = pygame.Vector2(1, 0)
LEFT = pygame.Vector2(-1, 0)
ZERO = pygame.Vector2(0, 0)


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


class Game:
    def __init__(self):
        self.display = pygame.display.set_mode(flags=pygame.WINDOWMAXIMIZED)
        window_width, window_height = self.display.get_size()

        tile_size = t_w, t_h = 64, 64
        map_size = (window_width // t_w, window_height // t_h)
        tile_image = load_img(os.path.join('env', 'water-tile.png'))
        self.tile_map = TileMap(tile_size, map_size, tile_image)
        self.tile_group = self.tile_map.tiles

        player_animations = [
            (load_img(os.path.join('knight', 'idle_down.png')), 'idle-down', 8, 1),
            (load_img(os.path.join('knight', 'idle_top.png')), 'idle-up', 8, 1),
            (load_img(os.path.join('knight', 'idle_right.png')), 'idle-right', 8, 1),
            (load_img(os.path.join('knight', 'idle_left.png')), 'idle-left', 8, 1),
            (load_img(os.path.join('knight', 'walk_down.png')), 'walk-down', 8, 1),
            (load_img(os.path.join('knight', 'walk_top.png')), 'walk-up', 8, 1),
            (load_img(os.path.join('knight', 'walk_right.png')), 'walk-right', 8, 1),
            (load_img(os.path.join('knight', 'walk_left.png')), 'walk-left', 8, 1),
        ]
        player_size = p_w, p_h = 256, 256
        pos = (window_width // 2 - p_w // 2, window_height // 2 - p_h // 2)
        self.player_group = pygame.sprite.Group()
        self.player = Player(player_animations, 'idle-down', (self.player_group,), player_size, pos, 5, 100, 10)

        self.camera = Camera((self.tile_group, ), self.player)

    def mainloop(self):
        running = True
        while running:
            fps = pygame.time.Clock().tick(15)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type in (pygame.KEYUP, pygame.KEYDOWN):
                    self.player.process_click(event)

            self.player.update()
            self.camera.move()
            self.display.fill(pygame.Color('white'))
            self.tile_group.draw(self.display)
            self.player_group.draw(self.display)

            pygame.display.flip()


class Animation:
    def __init__(self,
                 sheet: pygame.surface.Surface,
                 sheet_size: Tuple[int, int],
                 sprite_size: Tuple[int, int],):

        self.frames: List[pygame.surface.Surface] = list()

        self.cut_sheet(sheet, sheet_size, sprite_size)

        self.cur_frame_index = -1
        self.__cur_frame = None
        self.next_frame()

    def cut_sheet(self, sheet: pygame.surface.Surface, sheet_size: Tuple[int, int], sprite_size: Tuple[int, int]):
        columns, rows = sheet_size
        rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)

                frame = pygame\
                    .transform\
                    .scale(sheet.subsurface(pygame.Rect(frame_location, rect.size)), sprite_size)

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
                 sprite_size: Tuple[int, int],
                 pos: Tuple[int, int],
                 ):
        super().__init__(*groups)

        self.animations: Dict[str, Animation] = dict()
        self.read_animations(animations, sprite_size)
        self.sprite_size = sprite_size
        self.cur_animation = self.animations.get(default_animation_name)
        self.image = self.cur_animation.cur_frame
        self.__rect = pygame.rect.Rect(*pos, *sprite_size)

    def read_animations(self,
                        animations: List[Tuple[pygame.surface.Surface, str, int, int]],
                        sprite_size: Tuple[int, int]
                        ):
        for anim in animations:
            sheet, key, *size = anim
            animation = Animation(sheet, size, sprite_size)
            self.animations.update({key: animation})

    def next_frame(self):
        self.cur_animation.next_frame()
        self.image = self.cur_animation.cur_frame

    def set_animation(self, animation_name: str):
        self.cur_animation = self.animations[animation_name]
        self.image = self.cur_animation.cur_frame

    @property
    def rect(self):
        return self.__rect

    @rect.setter
    def rect(self, value):
        self.__rect = value


class StaticSprite(pygame.sprite.Sprite):
    def __init__(self, size: Tuple[int, int], pos: Tuple[int, int], image: pygame.surface.Surface, groups: Tuple):
        super().__init__(*groups)
        self.width, self.height = self.size = size
        self.x, self.y = self.pos = pos
        self.image = pygame.transform.scale(image, self.size)
        self.rect = image.get_rect().move(self.width * self.x, self.height * self.y)


class Entity(AnimatedSprite):
    def __init__(self,
                 animations: List[Tuple[pygame.surface.Surface, str, int, int]],
                 default_animation_name: str,
                 groups: Tuple[pygame.sprite.Group],
                 sprite_size: Tuple[int, int],
                 pos: Tuple[int, int],
                 speed: int,
                 hp: int,
                 attack_strength: int,
                 ):
        super().__init__(animations, default_animation_name, groups, sprite_size, pos)
        self.speed = speed
        self.hp = hp
        self.attack_strength = attack_strength

        self.__vision = None
        self.__velocity = None

        self.vision = DOWN
        self.velocity = ZERO

    def move(self):
        if self.velocity != ZERO:
            self.rect = self.rect.move(*(self.velocity.normalize() * self.speed))
            self.vision = pygame.Vector2(0, 0) + self.velocity
            print(self.vision == self.velocity)

    def switch_animation(self):
        pass

    def update(self):
        self.move()
        self.switch_animation()
        self.next_frame()

    @property
    def velocity(self):
        return self.__velocity

    @velocity.setter
    def velocity(self, value: pygame.Vector2):
        self.__velocity = pygame.Vector2(0, 0) + value

    @property
    def vision(self):
        return self.__vision

    @vision.setter
    def vision(self, value):
        self.__vision = pygame.Vector2(0, 0) + value

    # def attack(self, direction: pygame.Vector2):
    # def get_damage(self, attacked: Entity)


class Player(Entity):
    def __init__(self,
                 animations: List[Tuple[pygame.surface.Surface, str, int, int]],
                 default_animation_name: str,
                 groups: Tuple[pygame.sprite.Group],
                 sprite_size: Tuple[int, int],
                 pos: Tuple[int, int],
                 speed: int,
                 hp: int,
                 attack_strength: int,
                 ):
        super().__init__(animations, default_animation_name, groups, sprite_size, pos, speed, hp, attack_strength)
        self.hitbox = pygame.rect.Rect(50, 0, sprite_size[0] - 100, sprite_size[1] - 40)

    def next_frame(self):
        super(Player, self).next_frame()
        pygame.draw.rect(self.image, pygame.Color('yellow'), self.hitbox, 2)

    def process_click(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.velocity += UP
            elif event.key == pygame.K_s:
                self.velocity += DOWN
            elif event.key == pygame.K_a:
                self.velocity += LEFT
            elif event.key == pygame.K_d:
                self.velocity += RIGHT

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.velocity -= UP
            elif event.key == pygame.K_s:
                self.velocity -= DOWN
            elif event.key == pygame.K_a:
                self.velocity -= LEFT
            elif event.key == pygame.K_d:
                self.velocity -= RIGHT

    def switch_animation(self):
        next_animation = 'idle-down'
        if self.vision.y == 1:
            next_animation = 'idle-down'
        elif self.vision.y == -1:
            next_animation = 'idle-up'
        if self.vision.x == 1:
            next_animation = 'idle-right'
        elif self.vision.x == -1:
            next_animation = 'idle-left'

        if self.velocity.y == 1:
            next_animation = 'walk-down'
        elif self.velocity.y == -1:
            next_animation = 'walk-up'

        if self.velocity.x == 1:
            next_animation = 'walk-right'
        elif self.velocity.x == -1:
            next_animation = 'walk-left'

        self.set_animation(next_animation)


class Camera:
    def __init__(self, groups_to_move: Tuple[pygame.sprite.Group], player: Player):
        self.groups = groups_to_move
        self.player = player

    def move(self):
        if self.player.velocity != ZERO:
            for group in self.groups:
                for sprite in group:
                    sprite.rect = sprite.rect.move(self.player.velocity.normalize() * self.player.speed * -1)


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


# Create common class for menus ?
class MainMenu:
    def __init__(self):
        pass


class RestartMenu:
    def __init__(self):
        pass


if __name__ == '__main__':
    Game().mainloop()
