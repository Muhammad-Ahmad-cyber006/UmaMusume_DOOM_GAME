from sprite_object import *


class Weapon(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/weapon/shotgun/0.png', scale=0.4, animation_time=90):
        super().__init__(game=game, path=path, scale=scale, animation_time=animation_time)
        self.images = deque(
            [pg.transform.smoothscale(img, (self.image.get_width() * scale, self.image.get_height() * scale))
             for img in self.images])
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        self.damage = 1000

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0

    def draw(self):
        self.game.screen.blit(self.images[0], self.weapon_pos)
        self.draw_crosshair()

    def draw_crosshair(self):
        cx, cy = HALF_WIDTH, HALF_HEIGHT
        size, gap, thickness = 14, 6, 3
        color = (255, 60, 60) if self.reloading else (255, 255, 255)

        # four crosshair ticks with a small open gap in the middle
        pg.draw.line(self.game.screen, color, (cx - size - gap, cy), (cx - gap, cy), thickness)
        pg.draw.line(self.game.screen, color, (cx + gap, cy), (cx + size + gap, cy), thickness)
        pg.draw.line(self.game.screen, color, (cx, cy - size - gap), (cx, cy - gap), thickness)
        pg.draw.line(self.game.screen, color, (cx, cy + gap), (cx, cy + size + gap), thickness)
        pg.draw.circle(self.game.screen, color, (cx, cy), 2)

    def update(self):
        self.check_animation_time()
        self.animate_shot()