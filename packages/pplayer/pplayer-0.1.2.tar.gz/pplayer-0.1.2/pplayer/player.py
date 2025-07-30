import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, images=None, shape="sprite", size=32, color=(255, 0, 0)):
        super().__init__()
        self.shape = shape
        self.color = color
        self.size = size
        self.speed = speed
        self.vel_y = 0
        self.gravity = 0.5
        self.on_ground = False
        self.animation_timer = 0
        self.image_index = 0

        if images:
            self.images = images
            self.image = self.images[0]
            self.rect = self.image.get_rect(topleft=(x, y))
        else:
            self.images = None
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            self.image.fill(color)
            self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, keys, tiles):
        dx, dy = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = -10
            self.on_ground = False
        self.vel_y += self.gravity
        dy += self.vel_y

        self.rect.x += dx
        for tile in tiles:
            if self.rect.colliderect(tile):
                if dx > 0:
                    self.rect.right = tile.left
                if dx < 0:
                    self.rect.left = tile.right

        self.rect.y += dy
        for tile in tiles:
            if self.rect.colliderect(tile):
                if dy > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0

        if self.images:
            self.animate()

    def animate(self):
        self.animation_timer += 1
        if self.animation_timer >= 5:
            self.animation_timer = 0
            self.image_index = (self.image_index + 1) % len(self.images)
            self.image = self.images[self.image_index]

    def draw(self, surface):
        if self.shape == "square":
            pygame.draw.rect(surface, self.color, self.rect)
        elif self.shape == "circle":
            center = self.rect.center
            pygame.draw.circle(surface, self.color, center, self.size // 2)
        else:
            surface.blit(self.image, self.rect)
