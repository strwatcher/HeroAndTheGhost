import pygame
from tools import *
from templs import *


class Game:
    def __init__(self):
        pygame.init()
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
        player_size = p_w, p_h = 38 * 4, 52 * 4
        pos = (window_width // 2 - p_w // 2, window_height // 2 - p_h // 2)
        self.player_group = pygame.sprite.Group()
        self.attacks_group = pygame.sprite.Group()
        self.player = Player(player_animations,
                             'idle-down',
                             (self.player_group,),
                             player_size,
                             pos,
                             5,
                             100,
                             10,
                             self.attacks_group)

        self.camera = Camera((self.tile_group,), self.player)

    def mainloop(self):
        running = True
        while running:
            fps = pygame.time.Clock().tick(15)
            attack_playing = self.player.process_attack()
            keys = pygame.key.get_pressed()
            if not attack_playing:
                self.player.process_click(keys)
            else:
                self.player.velocity = ZERO

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.player.update()
            self.camera.move()
            self.display.fill(pygame.Color('white'))
            self.tile_group.draw(self.display)
            self.player_group.draw(self.display)
            self.attacks_group.draw(self.display)

            pygame.display.flip()
