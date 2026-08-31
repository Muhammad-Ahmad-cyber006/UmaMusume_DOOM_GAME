from sprite_object import *
from npc import *
from projectile import Projectile
from final_battle import FinalBattleManager
from enemy_config import LEVEL1_MINION_WAVES
from random import choices, randrange


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.projectiles = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}

        self.final_battle = FinalBattleManager(game, self)

        # spawn npc 
        self.enemies = 16  # npc count (regular grunts)
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.weights = [60, 27, 13]
        # keep the starter room (top-left) and the entrance corridor clear
        self.restricted_area = {(i, j) for i in range(9) for j in range(9)}
        self.spawn_npc()
        self.spawn_level1_minions()

        # two Gold Ship elite bosses guarding the final arena
        add_npc(GoldShipNPC(game, pos=(9.5, 19.5)))
        add_npc(GoldShipNPC(game, pos=(21.5, 19.5)))

        add_sprite(AnimatedSprite(game, pos=(3.5, 3.5)))
        add_sprite(AnimatedSprite(game, pos=(6.5, 6.5)))

        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 3.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'green_light/0.png', pos=(11.5, 5.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'green_light/0.png', pos=(18.5, 5.5)))

        # wing A: pillared hall (top right, a side branch)
        add_sprite(AnimatedSprite(game, pos=(22.5, 4.5)))
        add_sprite(AnimatedSprite(game, pos=(25.5, 7.5)))

        # route waypoint
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 11.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(15.5, 13.5)))

        # wing B: winding corridor (left side, a side branch)
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'green_light/0.png', pos=(4.5, 11.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'green_light/0.png', pos=(7.5, 14.5)))

        # wing C: twin mirrored rooms (right side, a side branch)
        add_sprite(AnimatedSprite(game, pos=(21.5, 11.5)))
        add_sprite(AnimatedSprite(game, pos=(25.5, 11.5)))

        # the narrow main gate at row 16, flanked by red lights just
        # past it so the choke point reads as the intended route right
        # before the arena opens up
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(13.5, 17.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(16.5, 17.5)))

        # lower arena torches, on the approach to the Gold Ships
        add_sprite(AnimatedSprite(game, pos=(5.5, 17.5)))
        add_sprite(AnimatedSprite(game, pos=(24.5, 17.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(15.5, 18.5)))

        # boss-gate arena, an ominous ring of red lights around the Gold Ships
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 19.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(21.5, 19.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(15.5, 21.5)))

    def spawn_npc(self):
        for i in range(self.enemies):
            npc = choices(self.npc_types, self.weights)[0]
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

    def spawn_level1_minions(self):

        for wave in LEVEL1_MINION_WAVES:
            for pos in wave['positions']:
                self.add_npc(MinionNPC(self.game, pos=pos, tier_multiplier=wave['tier_multiplier']))

    def boss_defeated(self):
        pass  

    def spawn_projectile(self, path, pos, angle, speed, damage, scale, lifetime_ms, hit_radius):
        self.projectiles.append(Projectile(
            self.game, path=path, pos=pos, angle=angle, speed=speed, damage=damage,
            scale=scale, lifetime_ms=lifetime_ms, hit_radius=hit_radius))

    def check_win(self):
        if self.final_battle.active:
            return  # the final battle drives its own victory check in update
        self.final_battle.check_start_trigger(npc_positions_empty=not len(self.npc_positions))

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        [projectile.update() for projectile in self.projectiles]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.npc_list = [npc for npc in self.npc_list
                          if not (hasattr(npc, 'should_be_removed') and npc.should_be_removed())]
        self.final_battle.update()
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
