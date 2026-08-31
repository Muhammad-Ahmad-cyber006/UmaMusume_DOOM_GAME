import math
import pygame as pg
from settings import *


class HUD:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen

        self.hp_font = pg.font.SysFont('Arial', 30, bold=True)
        self.hp_font_small = pg.font.SysFont('Arial', 18, bold=True)

        self.game_over_image = self._get_texture('resources/textures/game_over.png', RES)
        self.win_image = self._get_texture('resources/textures/win.png', RES)
        self.blood_screen = self._get_texture('resources/textures/blood_screen.png', RES)

        self.minimap_scale = 6   # pixels per map cell
        self.minimap_margin = 14

        self.banner_font = pg.font.SysFont('Arial', 46, bold=True)
        self.banner_sub_font = pg.font.SysFont('Arial', 24, bold=True)

        self._banner_main = ''
        self._banner_sub = ''
        self._banner_start = 0
        self._banner_duration = 0
        self._banner_fade_ms = 350

    @staticmethod
    def _get_texture(path, res):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def draw(self):
        self.draw_player_health()
        self.draw_boss_health_bars()
        self.draw_minimap()
        self.draw_final_battle_banner()

    # --- player health -----------------------------------------------
    def draw_player_health(self):
        health = self.game.player.health
        max_health = PLAYER_MAX_HEALTH
        ratio = max(0, min(1, health / max_health))

        x, y = 20, 20
        bar_w, bar_h = 280, 40

        # solid opaque panel behind everything, guaranteed visible over any background
        panel = pg.Surface((bar_w + 20, bar_h + 44), pg.SRCALPHA)
        panel.fill((0, 0, 0, 220))
        self.screen.blit(panel, (x - 10, y - 10))
        pg.draw.rect(self.screen, (255, 255, 255), (x - 10, y - 10, bar_w + 20, bar_h + 44), 2)

        label = self.hp_font_small.render('HEALTH', True, (255, 255, 255))
        self.screen.blit(label, (x, y))

        bar_y = y + 24
        pg.draw.rect(self.screen, (60, 0, 0), (x, bar_y, bar_w, bar_h))
        if ratio > 0.6:
            fill_color = (60, 200, 60)
        elif ratio > 0.3:
            fill_color = (230, 200, 40)
        else:
            fill_color = (220, 40, 40)
        pg.draw.rect(self.screen, fill_color, (x, bar_y, int(bar_w * ratio), bar_h))
        pg.draw.rect(self.screen, (255, 255, 255), (x, bar_y, bar_w, bar_h), 2)

        text = f'{round(ratio * 100)}%'
        num_surf = self.hp_font.render(text, True, (255, 255, 255))
        outline_surf = self.hp_font.render(text, True, (0, 0, 0))
        tx = x + bar_w // 2 - num_surf.get_width() // 2
        ty = bar_y + bar_h // 2 - num_surf.get_height() // 2
        for ox, oy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            self.screen.blit(outline_surf, (tx + ox, ty + oy))
        self.screen.blit(num_surf, (tx, ty))

    # --- boss bars -----------------------------------------------------
    def draw_boss_health_bars(self):
        # each currently visible, still-alive boss gets its own stacked
        # slot, so two Gold Ships on screen at once show two separate
        # bars — and when one dies, only its bar disappears.
        visible_bosses = [
            npc for npc in self.game.object_handler.npc_list
            if getattr(npc, 'is_boss', False) and npc.alive and npc.is_visible_to_player
        ]
        for slot, npc in enumerate(visible_bosses):
            npc.draw_health_bar(slot)

    # --- minimap ---------------------------------------------------------
    def draw_minimap(self):
        game_map = self.game.map
        scale = self.minimap_scale
        margin = self.minimap_margin
        map_w = game_map.cols * scale
        map_h = game_map.rows * scale
        x0 = WIDTH - map_w - margin
        y0 = margin

        panel = pg.Surface((map_w + 8, map_h + 8), pg.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        self.screen.blit(panel, (x0 - 4, y0 - 4))

        for (cx, cy) in game_map.world_map:
            pg.draw.rect(self.screen, (120, 120, 120),
                         (x0 + cx * scale, y0 + cy * scale, scale, scale))

        for npc in self.game.object_handler.npc_list:
            if not npc.alive:
                continue
            is_boss = getattr(npc, 'is_boss', False)
            color = (230, 190, 30) if is_boss else (200, 40, 40)
            radius = 3 if is_boss else 2
            px = x0 + npc.x * scale
            py = y0 + npc.y * scale
            pg.draw.circle(self.screen, color, (int(px), int(py)), radius)

        player = self.game.player
        ppx = x0 + player.x * scale
        ppy = y0 + player.y * scale
        pg.draw.circle(self.screen, (60, 200, 255), (int(ppx), int(ppy)), 4)
        end_x = ppx + math.cos(player.angle) * 10
        end_y = ppy + math.sin(player.angle) * 10
        pg.draw.line(self.screen, (60, 200, 255), (ppx, ppy), (end_x, end_y), 2)

        pg.draw.rect(self.screen, (255, 255, 255), (x0 - 4, y0 - 4, map_w + 8, map_h + 8), 2)

    # --- full-screen overlays ------------------------------------------
    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    # --- reusable cinematic transformation banner -----------------------
    def show_transformation_banner(self, main_text, sub_text=None, duration_ms=2600):

        self._banner_main = main_text
        self._banner_sub = sub_text or ''
        self._banner_start = pg.time.get_ticks()
        self._banner_duration = duration_ms

    def draw_final_battle_banner(self):
        if not self._banner_main:
            return
        now = pg.time.get_ticks()
        elapsed = now - self._banner_start
        if elapsed >= self._banner_duration:
            self._banner_main = ''
            return

        fade = self._banner_fade_ms
        if elapsed < fade:
            alpha = elapsed / fade
        elif elapsed > self._banner_duration - fade:
            alpha = (self._banner_duration - elapsed) / fade
        else:
            alpha = 1.0
        alpha = max(0.0, min(1.0, alpha))

        main_surf = self.banner_font.render(self._banner_main, True, (255, 60, 60))
        main_outline = self.banner_font.render(self._banner_main, True, (0, 0, 0))
        main_surf.set_alpha(int(255 * alpha))
        main_outline.set_alpha(int(255 * alpha))

        x = HALF_WIDTH - main_surf.get_width() // 2
        y = HEIGHT // 3
        for ox, oy in ((-2, -2), (-2, 2), (2, -2), (2, 2)):
            self.screen.blit(main_outline, (x + ox, y + oy))
        self.screen.blit(main_surf, (x, y))

        if self._banner_sub and self._banner_sub != self._banner_main:
            sub_surf = self.banner_sub_font.render(self._banner_sub, True, (255, 220, 220))
            sub_outline = self.banner_sub_font.render(self._banner_sub, True, (0, 0, 0))
            sub_surf.set_alpha(int(255 * alpha))
            sub_outline.set_alpha(int(255 * alpha))
            sx = HALF_WIDTH - sub_surf.get_width() // 2
            sy = y + main_surf.get_height() + 8
            for ox, oy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                self.screen.blit(sub_outline, (sx + ox, sy + oy))
            self.screen.blit(sub_surf, (sx, sy))
