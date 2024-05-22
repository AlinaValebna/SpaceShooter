import pygame
import random
import os
import sys


pygame.init()
pygame.font.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('SPACE SHOOTER')

BG = pygame.image.load(
    os.path.join("assets", "background.png"))
PLAYER_SHIP = pygame.image.load(os.path.join("assets",'ship1.png')).convert_alpha()
RED_ENEMY = pygame.image.load(os.path.join("assets",'enemyred.png')).convert_alpha()
YELLOW_ENEMY = pygame.image.load(os.path.join("assets",'enemyyellow.png')).convert_alpha()
GREEN_ENEMY = pygame.image.load(os.path.join("assets",'enemygreen.png')).convert_alpha()
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_yellow.png"))
background_music = pygame.mixer.Sound('assets/soundtrack.wav')
background_music.play(-1)
boom_sound = pygame.mixer.Sound('assets/explosion.wav')


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        self.laser_sound = pygame.mixer.Sound('assets/laser.ogg')

    def draw(self, WIN):
        WIN.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(WIN)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WINDOW_HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            self.laser_sound.play()

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.rect = self.ship_img.get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.laser_img = BLUE_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def input_position(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WINDOW_HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, WIN):
        super().draw(WIN)
        self.healthbar(WIN)

    def healthbar(self, WIN):
        pygame.draw.rect(WIN, (255, 0, 0), (100, 30,
                         self.ship_img.get_width(), 20))
        pygame.draw.rect(WIN, (0, 255, 0), (100, 30, self.ship_img.get_width(
        ) * (self.health/self.max_health), 20))

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 80, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            self.laser_sound.play()


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_ENEMY, RED_LASER),
        "green": (GREEN_ENEMY, GREEN_LASER),
        "yellow": (YELLOW_ENEMY, YELLOW_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 75, self.y + 75, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, WIN):
        WIN.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 35)
    lost_font = pygame.font.SysFont("comicsans", 60)
    player_vel = 5
    laser_vel = 4
    player = Player(300, 630)
    enemies = []
    wave_length = 3
    enemy_vel = 1
    lost = False
    lost_count = 0

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render("HP: ", 1, (255, 255, 255))
        level_label = main_font.render(f"Wave: {level}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WINDOW_WIDTH - level_label.get_width() - 10, 10))
        player.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)

        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (255, 0, 0))
            WIN.blit(lost_label, (WINDOW_WIDTH/2 -
                     lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 5:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 3
            for i in range(wave_length):
                enemy = Enemy(random.randrange(
                    50, WINDOW_WIDTH-100), random.randrange(-1000, -100), random.choice(["red", "yellow", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WINDOW_WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 25 < WINDOW_HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                boom_sound.play()
            elif enemy.y + enemy.get_height() > WINDOW_HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render(
            "A long time ago in a galaxy far, far away...", 1, (255, 255, 255))
        WIN.blit(title_label, (WINDOW_WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
    sys.exit()


main_menu()
