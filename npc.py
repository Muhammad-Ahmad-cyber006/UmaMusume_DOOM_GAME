from sprite_object import *
from random import randint, random, choice, uniform
from enemy_config import (
    SOLDIER_STATS, CACO_DEMON_STATS, CYBER_DEMON_STATS,
    get_npc_awareness_radius, NPC_STUCK_FRAMES_THRESHOLD,
    GOLDSHIP_STATS, GOLDSHIP_SCALE, GOLDSHIP_IDLE_SHIFT, GOLDSHIP_ENCOUNTER_SOUND_CHANCE,
    GOLDSHIP_WALK_SHIFT, GOLDSHIP_DEATH_SHIFT,
    MINION_STATS, MINION_SCALE, MINION_SHIFT, MINION_BOB_AMPLITUDE, MINION_BOB_PERIOD_MS,
    MINION_PROJECTILE_SPEED, MINION_PROJECTILE_SCALE,
    MINION_PROJECTILE_LIFETIME_MS, MINION_PROJECTILE_HIT_RADIUS, MINION_CORPSE_LINGER_MS,
    MEISHO_DOTO_STATS, MEISHO_DOTO_STAGES, MEISHO_DOTO_TOTAL_HEALTH,
    MEISHO_DOTO_TRANSFORM_DURATION_MS,
    STAGE1_HUGE_ASSET, STAGE1_HUGE_COOLDOWN_MS, STAGE1_HUGE_DAMAGE, STAGE1_HUGE_COUNT,
    STAGE1_HUGE_SPREAD_DEG, STAGE1_HUGE_SPEED, STAGE1_HUGE_SCALE, STAGE1_HUGE_HIT_RADIUS,
    STAGE1_HUGE_LIFETIME_MS,
    STAGE1_SPREAD_ASSET, STAGE1_SPREAD_COOLDOWN_MS, STAGE1_SPREAD_DAMAGE, STAGE1_SPREAD_COUNT,
    STAGE1_SPREAD_DEG, STAGE1_SPREAD_SPEED, STAGE1_SPREAD_SCALE, STAGE1_SPREAD_HIT_RADIUS,
    STAGE1_SPREAD_LIFETIME_MS,
    STAGE2_HUGE_ASSET, STAGE2_HUGE_COOLDOWN_MS, STAGE2_HUGE_DAMAGE, STAGE2_HUGE_COUNT,
    STAGE2_HUGE_SPREAD_DEG, STAGE2_HUGE_SPEED, STAGE2_HUGE_SCALE, STAGE2_HUGE_HIT_RADIUS,
    STAGE2_HUGE_LIFETIME_MS,
    STAGE2_SPREAD_ASSET, STAGE2_SPREAD_COOLDOWN_MS, STAGE2_SPREAD_DAMAGE, STAGE2_SPREAD_COUNT,
    STAGE2_SPREAD_DEG, STAGE2_SPREAD_SPEED, STAGE2_SPREAD_SCALE, STAGE2_SPREAD_HIT_RADIUS,
    STAGE2_SPREAD_LIFETIME_MS,
    STAGE2_CROSS_COOLDOWN_MS, STAGE2_CROSS_ARMS, STAGE2_CROSS_DAMAGE, STAGE2_CROSS_SPEED,
    STAGE2_CROSS_SCALE, STAGE2_CROSS_HIT_RADIUS, STAGE2_CROSS_LIFETIME_MS,
    STAGE3_HUGE_ASSET, STAGE3_HUGE_COOLDOWN_MS, STAGE3_HUGE_DAMAGE, STAGE3_HUGE_COUNT,
    STAGE3_HUGE_SPREAD_DEG, STAGE3_HUGE_SPEED, STAGE3_HUGE_SCALE, STAGE3_HUGE_HIT_RADIUS,
    STAGE3_HUGE_LIFETIME_MS,
    STAGE3_SPREAD_ASSET, STAGE3_SPREAD_COOLDOWN_MS, STAGE3_SPREAD_DAMAGE, STAGE3_SPREAD_COUNT,
    STAGE3_SPREAD_DEG, STAGE3_SPREAD_SPEED, STAGE3_SPREAD_SCALE, STAGE3_SPREAD_HIT_RADIUS,
    STAGE3_SPREAD_LIFETIME_MS,
    STAGE3_CROSS_COOLDOWN_MS, STAGE3_CROSS_ARMS, STAGE3_CROSS_DAMAGE, STAGE3_CROSS_SPEED,
    STAGE3_CROSS_SCALE, STAGE3_CROSS_HIT_RADIUS, STAGE3_CROSS_LIFETIME_MS,
    STAGE3_COMBO_DELAY_MS, STAGE3_COMBO_SPREAD_COUNT, STAGE3_COMBO_SPREAD_DEG,
    OMNI_ASSET, OMNI_RING_COOLDOWN_MS, OMNI_RING_COUNT, OMNI_RING_DAMAGE, OMNI_RING_SPEED,
    OMNI_RING_SCALE, OMNI_RING_SPAWN_RADIUS, OMNI_RING_HIT_RADIUS, OMNI_RING_LIFETIME_MS,
    OMNI_RING_ROTATION_STEP_DEGREES, OMNI_RING_FIRST_CAST_DELAY_MS,
    OMNI_BURST_COOLDOWN_MS, OMNI_BURST_COUNT, OMNI_BURST_SPREAD_DEG, OMNI_BURST_DAMAGE,
    OMNI_BURST_SPEED, OMNI_BURST_SCALE, OMNI_BURST_HIT_RADIUS, OMNI_BURST_LIFETIME_MS,
)



_FONT_CACHE = {}


def get_cached_font(name, size, bold=False):
    key = (name, size, bold)
    font = _FONT_CACHE.get(key)
    if font is None:
        font = pg.font.SysFont(name, size, bold=bold)
        _FONT_CACHE[key] = font
    return font


class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

        self.attack_dist = randint(3, 6)
        self.size = 20
        self.apply_stats(SOLDIER_STATS)
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False

    def apply_stats(self, stats):
        """Copy a stat dict (see enemy_config.py) onto this instance."""
        for key, value in stats.items():
            setattr(self, key, value)

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self):
        next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos

        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
        else:
            angle = math.atan2(self.game.player.y - self.y, self.game.player.x - self.x)

        if getattr(self, '_stuck_frames', 0) >= NPC_STUCK_FRAMES_THRESHOLD:
            angle += math.pi / 2 if (self._stuck_frames % 2 == 0) else -math.pi / 2
            self._stuck_frames = 0

        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed

        pos_before = (self.x, self.y)
        self.check_wall_collision(dx, dy)
        if (self.x, self.y) == pos_before:
            self._stuck_frames = getattr(self, '_stuck_frames', 0) + 1
        else:
            self._stuck_frames = 0

    def attack(self):
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            # a minimum hit-window floor so small/distant enemies (like
            # minions) are not nearly impossible to actually land a shot on
            hit_half_width = max(self.sprite_half_width, 34)
            if HALF_WIDTH - hit_half_width < self.screen_x < HALF_WIDTH + hit_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.check_health()

    def check_health(self):
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()

    def run_logic(self):
        if self.alive:
            self.ray_cast_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()

            if self.pain:
                self.animate_pain()

            elif self.ray_cast_value or self.dist < self._current_awareness_radius():
                # either a clear sightline, or just close enough to sense

                self.player_search_trigger = True

                if self.dist < self.attack_dist and self.ray_cast_value:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.movement()

            elif self.player_search_trigger:
                self.animate(self.walk_images)
                self.movement()

            else:
                self.animate(self.idle_images)
        else:
            self.animate_death()

    def _current_awareness_radius(self):

        remaining_alive = sum(1 for npc in self.game.object_handler.npc_list if npc.alive)
        return get_npc_awareness_radius(remaining_alive)

    @property
    def map_pos(self):
        return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        # guard against exact 0 to avoid ZeroDivisionError on axis-aligned rays
        if sin_a == 0:
            sin_a = 1e-9
        if cos_a == 0:
            cos_a = 1e-9

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False

    def draw_ray_cast(self):
        pg.draw.circle(self.game.screen, 'red', (100 * self.x, 100 * self.y), 15)
        if self.ray_cast_player_npc():
            pg.draw.line(self.game.screen, 'orange', (100 * self.game.player.x, 100 * self.game.player.y),
                         (100 * self.x, 100 * self.y), 2)


class SoldierNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)

class CacoDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/caco_demon/0.png', pos=(10.5, 6.5),
                 scale=0.7, shift=0.27, animation_time=250):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.apply_stats(CACO_DEMON_STATS)

class CyberDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/cyber_demon/0.png', pos=(11.5, 6.0),
                 scale=1.0, shift=0.04, animation_time=210):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.apply_stats(CYBER_DEMON_STATS)


class MinionNPC(NPC):
    ASSET_DIR = 'resources/MEISH_DOTO/'

    def __init__(self, game, pos, scale=MINION_SCALE, shift=MINION_SHIFT,
                 animation_time=200, tier_multiplier=1.0):

        SpriteObject.__init__(self, game, path=self.ASSET_DIR + 'minion.png',
                               pos=pos, scale=scale, shift=shift)
        self.animation_time = animation_time
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

        img = self.image
        defeat_img = load_cached_image(self.ASSET_DIR + 'defeat.png')
        self.idle_images = deque([img])
        self.walk_images = deque([img])
        self.attack_images = deque([img])
        self.pain_images = deque([img])
        self.death_images = deque([defeat_img, defeat_img])

        self.apply_stats(MINION_STATS)
 
        self.tier_multiplier = tier_multiplier
        if tier_multiplier != 1.0:
            self.health = max(1, round(self.health * tier_multiplier))
            self.attack_damage = round(self.attack_damage * tier_multiplier)
        self.max_health = self.health
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False

        self._last_attack_time = 0
        self._death_time = None
        self._base_shift = shift
        self._is_moving = False

    def movement(self):
        super().movement()
        self._is_moving = True

    def update(self):

        if self._is_moving:
            t = pg.time.get_ticks()
            bob = math.sin(t * math.tau / MINION_BOB_PERIOD_MS) * MINION_BOB_AMPLITUDE
            self.SPRITE_HEIGHT_SHIFT = self._base_shift + bob
        else:
            self.SPRITE_HEIGHT_SHIFT = self._base_shift
        self._is_moving = False
        super().update()

    def check_health(self):
        if self.health < 1:
            if self.alive:
                self.alive = False
                self.game.sound.npc_death.play()
                self._death_time = pg.time.get_ticks()

    def should_be_removed(self):
 
        if self.alive or self._death_time is None:
            return False
        return pg.time.get_ticks() - self._death_time >= MINION_CORPSE_LINGER_MS

    def attack(self):
        if not self.animation_trigger:
            return
        now = pg.time.get_ticks()
        if now - self._last_attack_time < self.attack_cooldown_ms:
            return
        self._last_attack_time = now
        self.game.sound.npc_shot.play()
        angle = math.atan2(self.player.y - self.y, self.player.x - self.x)
        self.game.object_handler.spawn_projectile(
            path=self.ASSET_DIR + 'minion_attack.png', pos=(self.x, self.y), angle=angle,
            speed=MINION_PROJECTILE_SPEED, damage=self.attack_damage,
            scale=MINION_PROJECTILE_SCALE, lifetime_ms=MINION_PROJECTILE_LIFETIME_MS,
            hit_radius=MINION_PROJECTILE_HIT_RADIUS)


class BossNPC(NPC):
    is_boss = True
    boss_label = 'ELITE BOSS'

    def check_health(self):
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()
            self.game.object_handler.boss_defeated()

    def draw_health_bar(self, slot=0):
        if not self.alive:
            return
        bar_w, bar_h = 460, 30
        x = HALF_WIDTH - bar_w // 2
        y = 40 + slot * 68  # stack additional bosses bars below the first

        ratio = max(0, self.health / self.max_health)
        pg.draw.rect(self.game.screen, (40, 30, 0), (x, y, bar_w, bar_h))
        pg.draw.rect(self.game.screen, (230, 180, 20), (x, y, int(bar_w * ratio), bar_h))
        pg.draw.rect(self.game.screen, (255, 255, 255), (x, y, bar_w, bar_h), 3)

        name_font = get_cached_font('Arial', 22, bold=True)
        name_surf = name_font.render(self.boss_label, True, (255, 255, 255))
        self.game.screen.blit(name_surf, (HALF_WIDTH - name_surf.get_width() // 2, y - 26))

        pct_font = get_cached_font('Arial', 20, bold=True)
        pct_text = f'{round(ratio * 100)}%'
        pct_surf = pct_font.render(pct_text, True, (255, 255, 255))
        pct_outline = pct_font.render(pct_text, True, (0, 0, 0))
        px = HALF_WIDTH - pct_surf.get_width() // 2
        py = y + bar_h // 2 - pct_surf.get_height() // 2
        for ox, oy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            self.game.screen.blit(pct_outline, (px + ox, py + oy))
        self.game.screen.blit(pct_surf, (px, py))

    @property
    def is_visible_to_player(self):
        return self.alive and (self.ray_cast_value or self.player_search_trigger)


class GoldShipNPC(BossNPC):
    boss_label = 'GOLD SHIP - ELITE'
    ASSET_DIR = 'resources/GoldShip/'

    def __init__(self, game, pos=(15.5, 28.0), scale=GOLDSHIP_SCALE, shift=GOLDSHIP_IDLE_SHIFT, animation_time=220):

        SpriteObject.__init__(self, game, path=self.ASSET_DIR + 'goldship.png',
                               pos=pos, scale=scale, shift=shift)
        self.animation_time = animation_time
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

        idle_img = self.image  
        walk_img = load_cached_image(self.ASSET_DIR + 'walk.png')
        death_img = load_cached_image(self.ASSET_DIR + 'death.png')

        self.idle_images = deque([idle_img])
        self.walk_images = deque([walk_img])
        self.attack_images = deque([idle_img, walk_img])  # simple lunge using the existing art
        self.pain_images = deque([walk_img])
        self.death_images = deque([death_img, death_img])  # 2 copies so the death pose actually shows
        self.image = self.idle_images[0]

        self._idle_shift = shift
        self._walk_shift = GOLDSHIP_WALK_SHIFT
        self._death_shift = GOLDSHIP_DEATH_SHIFT

        self.apply_stats(GOLDSHIP_STATS)
        self.max_health = self.health
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False

        self._last_attack_time = -self.attack_cooldown_ms
        self._has_noticed_player = False

        self.attack_sound = pg.mixer.Sound(self.ASSET_DIR + 'attack.wav')
        self.death_sound = pg.mixer.Sound(self.ASSET_DIR + 'death.wav')
        self.spawn_sound = pg.mixer.Sound(self.ASSET_DIR + 'spwan.wav')
        self.attack_sound.set_volume(0.5)
        self.spawn_sound.set_volume(0.6)
        self.spawn_sound.play()

    def run_logic(self):

        if self.alive and self.ray_cast_value and not self._has_noticed_player:
            self._has_noticed_player = True
            if random() < GOLDSHIP_ENCOUNTER_SOUND_CHANCE:
                choice((self.attack_sound, self.spawn_sound)).play()
        super().run_logic()

    def update(self):

        if self.image is self.walk_images[0]:
            self.SPRITE_HEIGHT_SHIFT = self._walk_shift
        elif self.image is self.death_images[0]:
            self.SPRITE_HEIGHT_SHIFT = self._death_shift
        else:
            self.SPRITE_HEIGHT_SHIFT = self._idle_shift
        super().update()

    def attack(self):
        if not self.animation_trigger:
            return
        now = pg.time.get_ticks()
        if now - self._last_attack_time < self.attack_cooldown_ms:
            return
        self._last_attack_time = now
        self.attack_sound.play()
        if random() < self.accuracy:
            self.game.player.get_damage(self.attack_damage)

    def check_health(self):
        if self.health < 1:
            self.alive = False
            self.death_sound.play()
            self.game.object_handler.boss_defeated()


class MeishoDotoNPC(BossNPC):

    ASSET_DIR = 'resources/MEISH_DOTO/'

    def __init__(self, game, pos, scale=3.2, shift=-01.25, animation_time=250):
        SpriteObject.__init__(self, game, path=self.ASSET_DIR + MEISHO_DOTO_STAGES[0]['skin'],
                               pos=pos, scale=scale, shift=shift)
        self.animation_time = animation_time
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

        self.defeat_image = load_cached_image(self.ASSET_DIR + 'defeat.png')

        self._stage_images = {
            i: load_cached_image(self.ASSET_DIR + stage['skin'])
            for i, stage in enumerate(MEISHO_DOTO_STAGES)
        }

        self.apply_stats(MEISHO_DOTO_STATS)
        self._base_speed = self.speed
        self._base_scale = scale
        self.max_health = MEISHO_DOTO_TOTAL_HEALTH
        self.health = self.max_health
        self._displayed_health = self.health 
        self.stage_index = -1  # forces _enter_stage(0) to run its setup on the first check_health()
        self.is_omni_stage = False

        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False

        # --- transformation state ------------------------------------
        self.transforming = False
        self.transform_until = 0

        # --- independent attack-move cooldown trackers ----------------
        self._last_move_a = 0
        self._last_move_b = 0
        self._last_move_c = 0
        self._combo_pending_until = None
        self._cross_rotation = 0.0
        self._omni_ring_rotation = 0.0

        self._enter_stage(0)

    # --- stage management ---------------------------------------------
    @property
    def stage_config(self):
        return MEISHO_DOTO_STAGES[self.stage_index]

    @property
    def stage_number(self):
  
        return self.stage_index + 1

    def get_current_form_name(self):
        return self.stage_config['name']

    @property
    def boss_label(self):
        return self.get_current_form_name()

    def _stage_boundaries(self):
 
        remaining = self.max_health
        boundaries = []
        for i, stage in enumerate(MEISHO_DOTO_STAGES):
            boundaries.append((i, remaining))
            remaining -= stage['health']
        return boundaries

    def _stage_for_health(self, health):
        for i, threshold in self._stage_boundaries():
            floor = threshold - MEISHO_DOTO_STAGES[i]['health']
            if health > floor:
                return i
        return len(MEISHO_DOTO_STAGES) - 1

    def _enter_stage(self, index):
 
        self.stage_index = index
        stage = self.stage_config

        image = self._stage_images[index]
        self.idle_images = deque([image])
        self.walk_images = deque([image])
        self.attack_images = deque([image])
        self.pain_images = deque([image])
        self.death_images = deque([self.defeat_image, self.defeat_image])
        self.image = image

        self.SPRITE_SCALE = self._base_scale * (stage['scale'] / MEISHO_DOTO_STAGES[0]['scale'])
        # each form's art has different amounts of transparent padding
        # below the character, so grounding needs a per-stage shift
        # value rather than one fixed fraction reused everywhere
        self.SPRITE_HEIGHT_SHIFT = stage['shift']
        self.speed = self._base_speed * stage['speed_multiplier']
        self.is_omni_stage = stage['omni_mode']

    def start_transformation(self, index):

        self._enter_stage(index)
        stage = self.stage_config

        now = pg.time.get_ticks()
        self.transforming = True
        self.transform_until = now + MEISHO_DOTO_TRANSFORM_DURATION_MS

        if stage['spawns_minions'] and stage['minion_wave_count'] > 0:
            self.game.object_handler.final_battle.spawn_minion_wave(
                count=stage['minion_wave_count'], tier_multiplier=stage['minion_tier'])

        self.game.hud.show_transformation_banner(stage['transform_arrow'], stage['transform_banner'])

    def _update_transformation(self):
        if self.transforming and pg.time.get_ticks() >= self.transform_until:
            self.finish_transformation()

    def finish_transformation(self):
 
        self.transforming = False
        now = pg.time.get_ticks()
        self._last_move_a = now
        self._last_move_b = now
        self._last_move_c = now
        self._combo_pending_until = None
        if self.is_omni_stage:
            self._last_move_a = now - (OMNI_RING_COOLDOWN_MS - OMNI_RING_FIRST_CAST_DELAY_MS)

    def check_health(self):
        if self.health <= 0:
            if self.alive:
                self.alive = False
                self.game.object_handler.final_battle.on_boss_death()
            return

        target_stage = self._stage_for_health(self.health)
        if target_stage != self.stage_index:
            self.start_transformation(target_stage)

    # --- per-frame behavior ---------------------------------------------
    def run_logic(self):
        if not self.alive:
            self.animate_death()
            return

        self._update_transformation()
        self.ray_cast_value = self.ray_cast_player_npc()
        self.check_hit_in_npc()

        if self.transforming:
            # cinematic freeze: no movement, no attacking, while the
            # transformation banner plays out
            self.animate(self.idle_images)
            return

        if self.ray_cast_value:
            self.player_search_trigger = True
            self.try_attacks()
            if self.dist > 6:
                self.animate(self.walk_images)
                self.movement()
            else:
                self.animate(self.idle_images)
        elif self.player_search_trigger:
            self.animate(self.walk_images)
            self.movement()
        else:
            self.animate(self.idle_images)

    def try_attacks(self):
        if self.is_omni_stage:
            self.fire_omni_attack()
        elif self.stage_index == 0:
            self.fire_stage_attack()
        elif self.stage_index == 1:
            self.fire_stage2_attack()
        elif self.stage_index == 2:
            self.fire_stage3_attack()

    # --- shared projectile-spawning helpers ------------------------------
    def _fire_fan(self, asset, count, spread_deg, damage, speed, scale, hit_radius,
                  lifetime_ms, angle_offset=0.0):

        base_angle = math.atan2(self.player.y - self.y, self.player.x - self.x) + angle_offset
        if count <= 1:
            self.game.object_handler.spawn_projectile(
                path=self.ASSET_DIR + asset, pos=(self.x, self.y), angle=base_angle,
                speed=speed, damage=damage, scale=scale,
                lifetime_ms=lifetime_ms, hit_radius=hit_radius)
            return
        spread = math.radians(spread_deg)
        for i in range(count):
            offset = -spread / 2 + spread * i / (count - 1)
            self.game.object_handler.spawn_projectile(
                path=self.ASSET_DIR + asset, pos=(self.x, self.y), angle=base_angle + offset,
                speed=speed, damage=damage, scale=scale,
                lifetime_ms=lifetime_ms, hit_radius=hit_radius)

    def _fire_cross(self, asset, damage, speed, scale, hit_radius, lifetime_ms,
                     arms=4, rotation_offset=0.0):

        for i in range(arms):
            angle = rotation_offset + math.tau * i / arms
            self.game.object_handler.spawn_projectile(
                path=self.ASSET_DIR + asset, pos=(self.x, self.y), angle=angle,
                speed=speed, damage=damage, scale=scale,
                lifetime_ms=lifetime_ms, hit_radius=hit_radius)

    def _fire_ring(self, asset, count, damage, speed, scale, spawn_radius, hit_radius,
                   lifetime_ms, rotation_offset=0.0):
  
        for i in range(count):
            angle = rotation_offset + math.tau * i / count
            spawn_x = self.x + math.cos(angle) * spawn_radius
            spawn_y = self.y + math.sin(angle) * spawn_radius
            self.game.object_handler.spawn_projectile(
                path=self.ASSET_DIR + asset, pos=(spawn_x, spawn_y), angle=angle,
                speed=speed, damage=damage, scale=scale,
                lifetime_ms=lifetime_ms, hit_radius=hit_radius)

    # --- Stage 1: MESHO DOTO  baseline, readable kit ---------------------
    def fire_stage_attack(self):
        now = pg.time.get_ticks()
        if now - self._last_move_a >= STAGE1_HUGE_COOLDOWN_MS:
            self._last_move_a = now
            self._fire_fan(STAGE1_HUGE_ASSET, STAGE1_HUGE_COUNT, STAGE1_HUGE_SPREAD_DEG,
                            STAGE1_HUGE_DAMAGE, STAGE1_HUGE_SPEED, STAGE1_HUGE_SCALE,
                            STAGE1_HUGE_HIT_RADIUS, STAGE1_HUGE_LIFETIME_MS)
        elif now - self._last_move_b >= STAGE1_SPREAD_COOLDOWN_MS:
            self._last_move_b = now
            self._fire_fan(STAGE1_SPREAD_ASSET, STAGE1_SPREAD_COUNT, STAGE1_SPREAD_DEG,
                            STAGE1_SPREAD_DAMAGE, STAGE1_SPREAD_SPEED, STAGE1_SPREAD_SCALE,
                            STAGE1_SPREAD_HIT_RADIUS, STAGE1_SPREAD_LIFETIME_MS)

    # --- Stage 2: MESHO DOTO BLACK  bigger fan, faster, occasional cross -
    def fire_stage2_attack(self):
        now = pg.time.get_ticks()
        if now - self._last_move_a >= STAGE2_HUGE_COOLDOWN_MS:
            self._last_move_a = now
            self._fire_fan(STAGE2_HUGE_ASSET, STAGE2_HUGE_COUNT, STAGE2_HUGE_SPREAD_DEG,
                            STAGE2_HUGE_DAMAGE, STAGE2_HUGE_SPEED, STAGE2_HUGE_SCALE,
                            STAGE2_HUGE_HIT_RADIUS, STAGE2_HUGE_LIFETIME_MS)
        if now - self._last_move_b >= STAGE2_SPREAD_COOLDOWN_MS:
            self._last_move_b = now
            self._fire_fan(STAGE2_SPREAD_ASSET, STAGE2_SPREAD_COUNT, STAGE2_SPREAD_DEG,
                            STAGE2_SPREAD_DAMAGE, STAGE2_SPREAD_SPEED, STAGE2_SPREAD_SCALE,
                            STAGE2_SPREAD_HIT_RADIUS, STAGE2_SPREAD_LIFETIME_MS)
        if now - self._last_move_c >= STAGE2_CROSS_COOLDOWN_MS:
            self._last_move_c = now
            self._fire_cross(STAGE2_SPREAD_ASSET, STAGE2_CROSS_DAMAGE, STAGE2_CROSS_SPEED,
                              STAGE2_CROSS_SCALE, STAGE2_CROSS_HIT_RADIUS, STAGE2_CROSS_LIFETIME_MS,
                              arms=STAGE2_CROSS_ARMS)

    # --- Stage 3: MESHO DOTO BLACK PURPLE  major spike, real combos ------
    def fire_stage3_attack(self):
        now = pg.time.get_ticks()
        if now - self._last_move_a >= STAGE3_HUGE_COOLDOWN_MS:
            self._last_move_a = now
            self._fire_fan(STAGE3_HUGE_ASSET, STAGE3_HUGE_COUNT, STAGE3_HUGE_SPREAD_DEG,
                            STAGE3_HUGE_DAMAGE, STAGE3_HUGE_SPEED, STAGE3_HUGE_SCALE,
                            STAGE3_HUGE_HIT_RADIUS, STAGE3_HUGE_LIFETIME_MS)
            self._combo_pending_until = now + STAGE3_COMBO_DELAY_MS
        if now - self._last_move_b >= STAGE3_SPREAD_COOLDOWN_MS:
            self._last_move_b = now
            self._fire_fan(STAGE3_SPREAD_ASSET, STAGE3_SPREAD_COUNT, STAGE3_SPREAD_DEG,
                            STAGE3_SPREAD_DAMAGE, STAGE3_SPREAD_SPEED, STAGE3_SPREAD_SCALE,
                            STAGE3_SPREAD_HIT_RADIUS, STAGE3_SPREAD_LIFETIME_MS)
        if now - self._last_move_c >= STAGE3_CROSS_COOLDOWN_MS:
            self._last_move_c = now
            self._cross_rotation = (self._cross_rotation + 0.4) % math.tau
            self._fire_cross(STAGE3_SPREAD_ASSET, STAGE3_CROSS_DAMAGE, STAGE3_CROSS_SPEED,
                              STAGE3_CROSS_SCALE, STAGE3_CROSS_HIT_RADIUS, STAGE3_CROSS_LIFETIME_MS,
                              arms=STAGE3_CROSS_ARMS, rotation_offset=self._cross_rotation)
        if self._combo_pending_until is not None and now >= self._combo_pending_until:
            self._combo_pending_until = None
            self._fire_fan(STAGE3_SPREAD_ASSET, STAGE3_COMBO_SPREAD_COUNT, STAGE3_COMBO_SPREAD_DEG,
                            STAGE3_SPREAD_DAMAGE, STAGE3_SPREAD_SPEED, STAGE3_SPREAD_SCALE,
                            STAGE3_SPREAD_HIT_RADIUS, STAGE3_SPREAD_LIFETIME_MS)

    # --- Stage 4: MESHO DOTO OMNI GOD  the signature attack --------------
    def fire_omni_attack(self):
        now = pg.time.get_ticks()
        if now - self._last_move_a >= OMNI_RING_COOLDOWN_MS:
            self._last_move_a = now
            self._omni_ring_rotation = (self._omni_ring_rotation
                                         + math.radians(OMNI_RING_ROTATION_STEP_DEGREES)) % math.tau
            self._fire_ring(OMNI_ASSET, OMNI_RING_COUNT, OMNI_RING_DAMAGE, OMNI_RING_SPEED,
                             OMNI_RING_SCALE, OMNI_RING_SPAWN_RADIUS, OMNI_RING_HIT_RADIUS,
                             OMNI_RING_LIFETIME_MS, rotation_offset=self._omni_ring_rotation)
        if now - self._last_move_b >= OMNI_BURST_COOLDOWN_MS:
            self._last_move_b = now
            self._fire_fan(OMNI_ASSET, OMNI_BURST_COUNT, OMNI_BURST_SPREAD_DEG, OMNI_BURST_DAMAGE,
                            OMNI_BURST_SPEED, OMNI_BURST_SCALE, OMNI_BURST_HIT_RADIUS,
                            OMNI_BURST_LIFETIME_MS)

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            hit_half_width = max(self.sprite_half_width, 34)
            if HALF_WIDTH - hit_half_width < self.screen_x < HALF_WIDTH + hit_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.health -= self.game.weapon.damage
                self.check_health()

    def draw_health_bar(self, slot=0):

        if not self.alive:
            return

        self._displayed_health += (self.health - self._displayed_health) * 0.12
        if abs(self._displayed_health - self.health) < 1:
            self._displayed_health = self.health
        ratio = max(0.0, min(1.0, self._displayed_health / self.max_health))

        stage = self.stage_config
        accent = stage['bar_color']

        bar_w, bar_h = 480, 34
        x = HALF_WIDTH - bar_w // 2
        y = 44 + slot * 88  # tucked right under the top edge, centered

        name_font = get_cached_font('Arial', 25, bold=True)
        hp_font = get_cached_font('Arial', 18, bold=True)

        # name, centered directly above the bar
        name_text = stage['name']
        name_surf = name_font.render(name_text, True, (255, 255, 255))
        outline_surf = name_font.render(name_text, True, (0, 0, 0))
        name_x = HALF_WIDTH - name_surf.get_width() // 2
        name_y = y - name_surf.get_height() - 4
        for ox, oy in ((-2, -2), (-2, 2), (2, -2), (2, 2)):
            self.game.screen.blit(outline_surf, (name_x + ox, name_y + oy))
        self.game.screen.blit(name_surf, (name_x, name_y))

        # soft glow behind the frame
        glow = pg.Surface((bar_w + 40, bar_h + 40), pg.SRCALPHA)
        for i, alpha in enumerate((26, 18, 10)):
            pad = 4 + i * 6
            pg.draw.rect(glow, (*accent, alpha),
                         (20 - pad, 20 - pad, bar_w + pad * 2, bar_h + pad * 2),
                         border_radius=14)
        self.game.screen.blit(glow, (x - 20, y - 20))

        # outer frame + track
        pg.draw.rect(self.game.screen, (18, 14, 16), (x, y, bar_w, bar_h), border_radius=10)

        # smooth fill 
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            fill_rect = pg.Rect(x, y, fill_w, bar_h)
            pg.draw.rect(self.game.screen, accent, fill_rect, border_radius=10)
            # a thin brighter highlight along the top of the fill for depth
            highlight = tuple(min(255, c + 60) for c in accent)
            pg.draw.rect(self.game.screen, highlight, (x, y, fill_w, max(2, bar_h // 5)),
                         border_radius=10)

        pg.draw.rect(self.game.screen, (235, 235, 235), (x, y, bar_w, bar_h), 2, border_radius=10)

        # just the percentage, centered inside the bar
        hp_text = f'{round(ratio * 100)}%'
        hp_surf = hp_font.render(hp_text, True, (255, 255, 255))
        hp_outline = hp_font.render(hp_text, True, (0, 0, 0))
        hp_x = HALF_WIDTH - hp_surf.get_width() // 2
        hp_y = y + bar_h // 2 - hp_surf.get_height() // 2
        for ox, oy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            self.game.screen.blit(hp_outline, (hp_x + ox, hp_y + oy))
        self.game.screen.blit(hp_surf, (hp_x, hp_y))
