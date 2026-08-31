import math
import pygame as pg
from random import uniform
from map import Map, mini_map_final
from pathfinding import PathFinding
from sprite_object import AnimatedSprite
from enemy_config import MINION_COUNT_PER_WAVE, OMNI_STAGE_DOT_DAMAGE_PER_SECOND

# Local import of MeishoDotoNPC/MinionNPC happens inside methods (not at
# module level) to avoid a circular import, since npc.py itself reaches
# back into this module's manager via object_handler.final_battle.


class FinalBattleManager:
    def __init__(self, game, object_handler):
        self.game = game
        self.object_handler = object_handler

        self.active = False
        self.boss = None

        self.win_pending_since = None   # pause before the fight actually starts
        self.death_time = None          # pause before the victory screen shows
        self.victory_triggered = False

        self.audio_tracks = []
        self.audio_index = 0
        self.audio_channel = None
        self.audio_active = False

        self.dot_last_tick = None       # stage-4 continuous damage timer

    # --- starting the fight -------------------------------------------
    def start(self):
   
        from npc import MeishoDotoNPC
        oh = self.object_handler

        self.active = True

        self.game.map = Map(self.game, layout=mini_map_final)
        self.game.pathfinding = PathFinding(self.game)  # rebuild for the new arena
        self.game.player.x, self.game.player.y = 11.5, 17.5
        self.game.player.angle = -math.pi / 2  # face north, toward the boss

        oh.npc_list = []
        oh.sprite_list = []
        oh.projectiles = []
        oh.npc_positions = set()

        self.boss = MeishoDotoNPC(self.game, pos=(11.5, 5.5))
        oh.add_npc(self.boss)

        # arena atmosphere
        anim_path = oh.anim_sprite_path
        for pos in [(3.5, 3.5), (18.5, 3.5), (3.5, 18.5), (18.5, 18.5)]:
            oh.add_sprite(AnimatedSprite(self.game, path=anim_path + 'red_light/0.png', pos=pos))

        self._start_audio_sequence()
        self.game.hud.show_transformation_banner(
            'MESHO DOTO', 'MESHO DOTO \u2014 THE FINAL BOSS', duration_ms=3000)

    # --- minions ---------------------------------------------------------
    def spawn_minion_wave(self, count=None, tier_multiplier=1.0):

        from npc import MinionNPC
        oh = self.object_handler
        boss = self.boss
        if boss is None:
            return
        if count is None:
            count = MINION_COUNT_PER_WAVE

        spawned = 0
        attempts = 0
        while spawned < count and attempts < count * 25:
            attempts += 1
            angle = uniform(0, math.tau)
            radius = uniform(2.5, 7.5)
            x = boss.x + math.cos(angle) * radius
            y = boss.y + math.sin(angle) * radius
            tile = (int(x), int(y))
            if not (0 <= tile[0] < self.game.map.cols and 0 <= tile[1] < self.game.map.rows):
                continue
            if tile in self.game.map.world_map:
                continue
            oh.add_npc(MinionNPC(self.game, pos=(x, y), tier_multiplier=tier_multiplier))
            spawned += 1

    def kill_all_minions(self):
        from npc import MinionNPC
        now = pg.time.get_ticks()
        for npc in self.object_handler.npc_list:
            if isinstance(npc, MinionNPC) and npc.alive:
                npc.alive = False
                npc._death_time = now  # so they still show their defeat pose then disappear

    def _start_audio_sequence(self):
        from npc import MeishoDotoNPC
        pg.mixer.music.stop()
        self.audio_tracks = [
            pg.mixer.Sound(MeishoDotoNPC.ASSET_DIR + '1.wav'),
            pg.mixer.Sound(MeishoDotoNPC.ASSET_DIR + '2.wav'),
        ]
        self.audio_index = 0
        self.audio_channel = self.audio_tracks[0].play()
        self.audio_active = True

    def _update_audio_sequence(self):

        if not self.audio_active:
            return
        if self.audio_channel is None or not self.audio_channel.get_busy():
            self.audio_index = (self.audio_index + 1) % len(self.audio_tracks)
            self.audio_channel = self.audio_tracks[self.audio_index].play()

    def _stop_audio_sequence(self):
        self.audio_active = False
        if self.audio_channel is not None:
            self.audio_channel.stop()

    # --- stage-4 "omni" continuous damage ---------------------------------
    def _update_omni_dot(self):
        boss = self.boss
        if boss is None or not boss.alive or not getattr(boss, 'is_omni_stage', False):
            self.dot_last_tick = None
            return
        now = pg.time.get_ticks()
        if self.dot_last_tick is None:
            self.dot_last_tick = now
        elif now - self.dot_last_tick >= 1000:
            self.dot_last_tick = now
            self.game.player.get_damage(OMNI_STAGE_DOT_DAMAGE_PER_SECOND)

    # --- death / victory ---------------------------------------------------
    def on_boss_death(self):
        """Called once, the instant Meisho Doto's last stage hits 0.
        Stops the boss music, plays the defeat cue, and kills every one
        of her minions immediately — the actual victory screen is held
        off for a couple seconds (see _check_victory)."""
        if self.death_time is not None:
            return
        self.death_time = pg.time.get_ticks()

        self._stop_audio_sequence()

        if self.audio_tracks:
            self.audio_tracks[0].play()
        self.kill_all_minions()

    def _check_victory(self):
        if self.death_time is None or self.victory_triggered:
            return
 
        if pg.time.get_ticks() - self.death_time >= 2000:
            self.victory_triggered = True
            self.game.hud.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()


    def check_start_trigger(self, npc_positions_empty):
        """Called every frame while the final battle hasn't started yet.
        Waits 1.5s after the last regular enemy/Gold Ship dies before
        actually starting the fight."""
        if npc_positions_empty:
            now = pg.time.get_ticks()
            if self.win_pending_since is None:
                self.win_pending_since = now
            elif now - self.win_pending_since >= 1500:
                self.start()
        else:
            self.win_pending_since = None

    def update(self):
        if not self.active:
            return
        self._update_audio_sequence()
        self._update_omni_dot()
        self._check_victory()
