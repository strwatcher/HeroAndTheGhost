from bases import *
from constants import *
from tools import *
import sys


class AttackArea(AnimatedSprite):
    def __init__(self,
                 animations: List[Tuple[pygame.surface.Surface, str, int, int]],
                 default_animation_name: str,
                 groups: Tuple[pygame.sprite.Group],
                 sprite_size: Tuple[int, int],
                 pos: Tuple[int, int],
                 angle: int,
                 ):
        super().__init__(animations, default_animation_name, groups, sprite_size, pos)

        self.image = pygame.transform.rotate(self.image, angle)
        self.angle = angle

    def next_frame(self) -> bool:
        if self.cur_animation.cur_frame_index == len(self.cur_animation.frames) - 1:
            return False
        else:
            super().next_frame()
            self.image = pygame.transform.rotate(self.image, self.angle)
            pygame.draw.rect(self.image, pygame.Color('red'), (0, 0, *self.sprite_size), 2)
            return True


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
                 attacks_group: pygame.sprite.Group
                 ):
        super().__init__(animations, default_animation_name, groups, sprite_size, pos, speed, hp)
        self.attack_strength = attack_strength
        self.hitbox = pygame.rect.Rect(20, 0, sprite_size[0] - 40, sprite_size[1] - 20)
        self.attacks_group = attacks_group
        self.cur_attack = None

    def get_damage(self, damage):
        super(Player, self).get_damage(damage)
        if self.hp < 0:
            sys.exit(0)

    def attack(self):
        pos = self.rect.x + self.sprite_size[0] * self.vision.x, self.rect.y + self.sprite_size[1] * self.vision.y
        angle = self.vision.angle_to(RIGHT)

        self.cur_attack = AttackArea([(load_img(os.path.join('knight', 'attack.png')), 'attack', 6, 1), ],
                                     'attack', tuple(), self.sprite_size, pos, angle)

        self.cur_attack.add(self.attacks_group)

    def next_frame(self):
        super(Player, self).next_frame()
        pygame.draw.rect(self.image, pygame.Color('yellow'), self.hitbox, 2)

    def process_attack(self):
        if self.cur_attack is not None:
            if not self.cur_attack.next_frame():
                self.attacks_group.remove(self.cur_attack)
                self.cur_attack = None
                return False
            else:
                return True
        return False

    def process_click(self, pressed_keys):
        if pressed_keys[pygame.K_w]:
            if pressed_keys[pygame.K_a]:
                self.velocity = LEFTUP
            elif pressed_keys[pygame.K_d]:
                self.velocity = RIGHTUP
            else:
                self.velocity = UP
        elif pressed_keys[pygame.K_s]:
            if pressed_keys[pygame.K_a]:
                self.velocity = LEFTDOWN
            elif pressed_keys[pygame.K_d]:
                self.velocity = RIGHTDOWN
            else:
                self.velocity = DOWN
        elif pressed_keys[pygame.K_a]:
            self.velocity = LEFT
        elif pressed_keys[pygame.K_d]:
            self.velocity = RIGHT
        else:
            self.velocity = ZERO

        if pressed_keys[pygame.K_SPACE]:
            self.attack()

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
                Tile(self.tile_size, (j, i), self.image, (self.__tiles,))

    @property
    def tiles(self):
        return self.__tiles
