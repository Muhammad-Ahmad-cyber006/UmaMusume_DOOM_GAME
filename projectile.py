import math
import pygame as pg
from sprite_object import SpriteObject

#this class is for projectiles that are fired by enemies or 
# bosses in the game. The projectiles travel in a straight line, 
# expire after a certain lifetime or upon hitting a wall, and deal damage 
# to the player if they come within a certain radius. The projectiles are 
# rendered using the same sprite pipeline as other game objects.
class Projectile(SpriteObject):
    def __init__(self, game, path, pos, angle, speed=0.015, damage=10,
                 scale=0.3, shift=0.0, lifetime_ms=4000, hit_radius=0.5):
        super().__init__(game, path=path, pos=pos, scale=scale, shift=shift)
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.hit_radius = hit_radius
        self.spawn_time = pg.time.get_ticks()
        self.lifetime_ms = lifetime_ms
        self.alive = True

    def update(self):
        if not self.alive:
            return

        dt = self.game.delta_time
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt

        if pg.time.get_ticks() - self.spawn_time > self.lifetime_ms:
            self.alive = False
            return

        if (int(self.x), int(self.y)) in self.game.map.world_map:
            self.alive = False
            return

        player = self.game.player
        if math.hypot(self.x - player.x, self.y - player.y) < self.hit_radius:
            player.get_damage(self.damage)
            self.alive = False
            return

        self.get_sprite()
