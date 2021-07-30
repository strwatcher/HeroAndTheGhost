from typing import *
from constants import *


class Animation:
    def __init__(self,
                 sheet: pygame.surface.Surface,
                 sheet_size: Tuple[int, int],
                 sprite_size: Tuple[int, int], ):

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

                frame = pygame \
                    .transform \
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
                 ):
        super().__init__(animations, default_animation_name, groups, sprite_size, pos)
        self.speed = speed
        self.hp = hp

        self.__vision = None
        self.__velocity = None

        self.vision = DOWN
        self.velocity = ZERO

        self.groups = groups

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

    def get_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            for group in self.groups:
                group.remove(self)

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


class Camera:
    def __init__(self, groups_to_move: Tuple[pygame.sprite.Group], hunted_entity: Entity):
        self.groups = groups_to_move
        self.hunted = hunted_entity

    def move(self):
        if self.hunted.velocity != ZERO:
            for group in self.groups:
                for sprite in group:
                    sprite.rect = sprite.rect.move(self.hunted.velocity.normalize() * self.hunted.speed * -1)
