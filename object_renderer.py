import pygame as pg
import math
from settings import *


class ObjectRenderer:


    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.hill_image = self.build_hill_image()
        self.floor_gradient = self.build_floor_gradient()

    def draw(self):
        self.draw_background()
        self.render_game_objects()

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        hill_offset = (self.sky_offset * 0.3) % WIDTH
        hill_y = HALF_HEIGHT - self.hill_image.get_height() + 18
        self.screen.blit(self.hill_image, (-hill_offset, hill_y))
        self.screen.blit(self.hill_image, (-hill_offset + WIDTH, hill_y))

        # shaded floor (subtle gradient instead of one flat color band)
        self.screen.blit(self.floor_gradient, (0, HALF_HEIGHT))

    def build_hill_image(self):
        h = 110
        surf = pg.Surface((WIDTH, h), pg.SRCALPHA)
        base_y = h - 15
        step = 4
        far_poly = [(0, h)]
        near_poly = [(0, h)]
        for x in range(0, WIDTH + 1, step):
            far_y = base_y - 22 * math.sin(2 * math.pi * 3 * x / WIDTH)
            near_y = base_y - 34 * math.sin(2 * math.pi * 3 * x / WIDTH + 1.3) \
                     - 12 * math.sin(2 * math.pi * 7 * x / WIDTH + 0.4)
            far_poly.append((x, far_y))
            near_poly.append((x, near_y))
        far_poly.append((WIDTH, h))
        near_poly.append((WIDTH, h))
        pg.draw.polygon(surf, (34, 46, 30), far_poly)   # distant hill layer
        pg.draw.polygon(surf, (46, 60, 36), near_poly)  # nearer hill layer
        return surf

    def build_floor_gradient(self):
        floor_h = HEIGHT - HALF_HEIGHT
        surf = pg.Surface((WIDTH, floor_h))
        bands = 30
        band_h = floor_h // bands + 1
        base_r, base_g, base_b = FLOOR_COLOR
        for i in range(bands):
            t = i / bands
            r = int(base_r * (0.6 + 0.4 * t))
            g = int(base_g * (0.6 + 0.4 * t))
            b = int(base_b * (0.6 + 0.4 * t))
            y = i * band_h
            pg.draw.rect(surf, (r, g, b), (0, y, WIDTH, band_h))
        return surf

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
        }