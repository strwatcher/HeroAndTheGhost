from bases import *
from constants import *
from tools import *
import game


###############################################
# Enemy
################################################

class Enemy(Entity):
    def __init__(self,
                 animations: List[Tuple[pygame.surface.Surface, str, int, int]],
                 default_animation_name: str,
                 groups: Tuple[pygame.sprite.Group],
                 sprite_size: Tuple[int, int],
                 pos: Tuple[int, int],
                 speed: int,
                 hp: int,
                 attack_strength: int,
                 hunted: Entity
                 ):
        super().__init__(animations, default_animation_name, groups, sprite_size, pos, speed, hp)
        self.hunted = hunted
        self.attack_strength = attack_strength

    def calc_velocity(self):
        hunted_pos = self.hunted.rect.center
        pos = self.rect.center
        motion_line = pygame.Vector2(hunted_pos[0] - pos[0], hunted_pos[1] - pos[1])
        if motion_line != ZERO:
            self.velocity = (motion_line.normalize() * self.speed)

    def attack(self):
        if self.rect.colliderect(self.hunted.rect):
            self.hunted.get_damage(self.attack_strength)

    def update(self):
        self.calc_velocity()
        self.attack()
        super(Enemy, self).update()

    def get_damage(self, damage):
        super(Enemy, self).get_damage(damage)
        if self.hp < 0:
            self.attack_strength = 0


################################################
# AttackArea and Player
################################################
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
        self.pos = pos
        self.angle = angle

    def next_frame(self) -> bool:
        if self.cur_animation.cur_frame_index == len(self.cur_animation.frames) - 1:
            return False
        else:
            super().next_frame()
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.move_ip(self.pos)
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
                 enemies: List[Enemy]
                 ):
        super().__init__(animations, default_animation_name, groups, sprite_size, pos, speed, hp)
        self.attack_strength = attack_strength
        self.attacked_group = enemies
        self.cur_attack = None

    def get_damage(self, damage):
        super(Player, self).get_damage(damage)
        if self.hp < 0:
            pygame.quit()
            game.Game().mainloop()

    def attack(self):
        pos = self.hitbox.x + self.sprite_size[0] // 2 * self.vision.x,\
              self.hitbox.y + self.sprite_size[1] // 2 * self.vision.y
        angle = self.vision.angle_to(RIGHT)

        self.cur_attack = AttackArea([(load_img(os.path.join('knight', 'attack.png')), 'attack', 6, 1), ],
                                     'attack', self.groups, self.sprite_size, pos, angle)

        for enemy in self.attacked_group:
            if self.cur_attack.rect.colliderect(enemy.rect):
                enemy.get_damage(self.attack_strength)

    def process_attack(self, group):
        if self.cur_attack is not None:
            if not self.cur_attack.next_frame():
                group.remove(self.cur_attack)
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


################################################
# Tile and TileMap
################################################

class Tile(StaticSprite):
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


class HillBar:
    def __init__(self, player: Player):
        self.pl = player
        self.hp = pygame.font.Font(None, 48)

    def update(self, display):
        text = self.hp.render(str(self.pl.hp), True, pygame.Color('red'))
        display.blit(text, (50, 50))
