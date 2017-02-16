#!/usr/bin/python2

import pygame
import sys
import random
from utils import vector2, sprite, player
from enemy import Enemy, Minion, Fireball

# constants
SCREEN_SIZE = (1024, 700) # W x H
COLORS = {
    'red' : (255, 0, 0),
    'blue' : (0, 0, 255),
    'green' : (0, 255, 0),
    'yellow' : (255, 255, 0),
    'orange' : (255, 165, 0),
    'pink' : (255, 192, 203),
    'white' : (255, 255, 255),
    'black' : (0, 0, 0)
}
PLACES = {
    'topleft' : (0, 0),
    'topright' : (SCREEN_SIZE[0], 0),
    'bottomleft' : (0, SCREEN_SIZE[1]),
    'bottomright' : (SCREEN_SIZE[0], SCREEN_SIZE[1]),
    'center' : (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
}

# camera movement variables
LEFT_EDGE = 0
RIGHT_EDGE = SCREEN_SIZE[0]
MIDDLE = SCREEN_SIZE[0] / 2

GROUND = 600
WIZARD_FILE = 'art/apprentice_moves/move1.png' # 'art/Wizard_Male.png'
MINION_FILE = 'art/Retrowizard_evil.png'
BACKGROUND_F = 'art/forest.png'
BACKGROUND_C = 'art/castle.png'
HP_SHIELD = 'art/HP_Shield33.png'
HP_SHIELD2 = 'art/HP_Shield23.png'
HP_SHIELD3 = 'art/HP_Shield13.png'
GAME_OVER_STR = "Game Over! Press [ESC] to quit."

def loadbackground(b_image):
    bg = pygame.image.load(b_image).convert()
    bg = pygame.transform.scale(bg, SCREEN_SIZE)
    return bg

# create a new minion somewhere on the screen
def createMinion(player):
    # player is on the right part of the screen
    if player.position.x > SCREEN_SIZE[0] / 2:
        x_p = random.randint(0, int(SCREEN_SIZE[0] / 2))
    else:
        x_p = random.randint(int(SCREEN_SIZE[0] / 2) + 1, SCREEN_SIZE[0])
    if random.randint(0, 1) == 0:
        x_v = -0.35
    else:
        x_v = 0.35

    pos = vector2(x_p, GROUND)
    vel = vector2(x_v, 0)

    new_minion = Minion(MINION_FILE, pos, vel)
    return new_minion

def displayHP(screen, hp_left, hp_img):
    if hp_left == 0:
        return
    img_s = hp_img[0].get_size()
    w = img_s[0]
    h = img_s[1]
    col = 1
    while hp_left > 2:
        x = SCREEN_SIZE[0] - ((w + 4) * col) - 10
        y = 20 + (h + 4)
        screen.blit(hp_img[0], (x, y))
        col += 1
        hp_left = hp_left - 3
    x = SCREEN_SIZE[0] - ((w + 4) * col + 1) - 10
    y = 20 + (h + 4)
    if hp_left == 2:
        screen.blit(hp_img[1], (x, y))
    elif hp_left == 1:
        screen.blit(hp_img[2], (x, y))


def next_win(old_bg, new_bg, screen, sprites):
    bg_size = old_bg.get_size()
    i = 0
    old_tick_t = pygame.time.get_ticks()
    # move everything back for new stage
    while i < bg_size[0]:
        current_tick_t = pygame.time.get_ticks()
        delta = current_tick_t - old_tick_t
        screen.blit(old_bg, (-i, 0))
        screen.blit(new_bg, (bg_size[0] - i, 0))
        for s in sprites: # move every sprite back
            new_pos = s.position.add(vector2(-1.0, 0).scale(delta))
            s.position = new_pos
            s.draw(screen)
        old_tick_t = pygame.time.get_ticks()
        i += delta
        pygame.display.flip()
    # now move player into view
    i = -sprites[0].size[0]
    p = sprites[0].position.add(vector2(0, 0))
    p.x = i
    sprites[0].position = p
    old_tick_t = pygame.time.get_ticks()
    while sprites[0].position.x < 0:
        current_tick_t = pygame.time.get_ticks()
        delta = current_tick_t - old_tick_t
        if delta == 0:
            delta = 1
        screen.blit(new_bg, (0, 0))
        new_pos = sprites[0].position.add(vector2(0.5, 0).scale(delta))
        sprites[0].position = new_pos
        sprites[0].draw(screen)
        old_tick_t = pygame.time.get_ticks()
    return new_bg

# setup goes here
pygame.init()
# font code from:
# http://stackoverflow.com/questions/10077644/python-display-text-w-font-color
myfont = pygame.font.SysFont("monospace", 24)
screen = pygame.display.set_mode(SCREEN_SIZE) #, pygame.FULLSCREEN)
pygame.display.set_caption("The Apprentice")

pygame.mixer.music.load("music/title_screen.mp3")
pygame.mixer.music.play(-1)

clock = pygame.time.Clock()

accel = vector2(0.025, 0)

forest = loadbackground(BACKGROUND_F)
castle = loadbackground(BACKGROUND_C)

stage_parts = [forest, forest, forest, forest, forest, forest]
stage_index = 0
win_background = stage_parts[stage_index]
hp_image = pygame.image.load(HP_SHIELD).convert_alpha()
hp_image_s = hp_image.get_size()
hp_image = pygame.transform.scale(hp_image,
                                  (int(hp_image_s[0] * 0.07),
                                   int(hp_image_s[1] * 0.07)))
hp_image2 = pygame.image.load(HP_SHIELD2).convert_alpha()
hp_image2 = pygame.transform.scale(hp_image2,
                                  (int(hp_image_s[0] * 0.07),
                                   int(hp_image_s[1] * 0.07)))
hp_image3 = pygame.image.load(HP_SHIELD3).convert_alpha()
hp_image3 = pygame.transform.scale(hp_image3,
                                   (int(hp_image_s[0] * 0.07),
                                    int(hp_image_s[1] * 0.07)))
hp_imgs = [hp_image, hp_image2, hp_image3]

sprites = [player(WIZARD_FILE, vector2(50, GROUND),
                  vector2(0, 0), name="Player")
]
player_s = sprites[0]
sprites.append(createMinion(player_s))
sprites.append(createMinion(player_s))
minions_killed = []

old_tick = pygame.time.get_ticks()

title_screen = True
while True:
    # get user events
    pygame.event.pump()
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evt.type == pygame.KEYDOWN and evt.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif evt.type == pygame.KEYDOWN and evt.key == pygame.K_c:
            title_screen = False
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.load("music/forest.mp3")
            pygame.mixer.music.play(-1)
            #pygame.mixer.stop()

    if title_screen:
        # show title screen
        continue

    if player_s.hits >= 15:
        # game over
        screen.fill(COLORS['black'])
        label = myfont.render(GAME_OVER_STR, 1, COLORS['white'])
        screen.blit(label, (200, 200))
        pygame.display.flip()
        continue

    # simulation stuff goes here (nothing to update yet)
    current_tick = pygame.time.get_ticks()
    delta = current_tick - old_tick
    if delta > 100: # prevent huge spikes in acceletation?
        old_tick = pygame.time.get_ticks()
        continue

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        player_s.shield = True
    else:
        player_s.shield = False
        player_s.shiled_hold = False

    if keys[pygame.K_a]: # a is currently pressed
        player_s.velocity.x -= 0.002
        player_s.facing_left = True
        player_s.facing_right = False
    elif keys[pygame.K_d]: # d is currently pressed
        player_s.velocity.x += 0.002
        player_s.facing_right = True
        player_s.facing_left = False
    else:
        if player_s.velocity.x > 0:
            player_s.velocity.x -= accel.scale(delta).x
            if player_s.velocity.x < 0:
                player_s.velocity.x = 0
        elif player_s.velocity.x < 0:
            player_s.velocity.x += accel.scale(delta).x
            if player_s.velocity.x > 0:
                player_s.velocity.x = 0

    if len(sprites) == 1: # only player left
        # add new minion into game
        sprites.append(createMinion(player_s))

    #accel = accel.scale(delta)
    for s in sprites:
        s.update(delta, player_s)

    for i in range(1, len(sprites)):
        for f in sprites[i].attack_count:
            f.collision(player_s)

    for i in range(1, len(sprites)):
        for f in sprites[i].attack_count:
            if f.collision_minion(sprites[i]):
                minions_killed.append(sprites[i])
                continue

    for m in minions_killed:
        sprites.remove(m)
    minions_killed = [] # reset list

    for i in range(0, len(sprites)):
        for other in sprites[i + 1:]:
            sprites[i].collision(other)

    # draw to screen and flip
    screen.blit(win_background, (0, 0))
    for s in sprites:
        s.draw(screen)

    hp_left = 15 - player_s.hits
    if hp_left <= 0:
        hp_left = 0
        pygame.mixer.music.fadeout(500)
        pygame.mixer.music.load("music/game_over.mp3")
        pygame.mixer.music.play(-1)
    displayHP(screen, hp_left, hp_imgs)

    pygame.display.flip()

    if player.NEXT_WIN:
        if stage_index < len(stage_parts) - 1:
            for i in range(1, len(sprites)):
                minions_killed.append(sprites[i])
            win_background = next_win(stage_parts[stage_index],
                                      stage_parts[stage_index + 1],
                                      screen, sprites)
            player.NEXT_WIN = False
            for m in minions_killed:
                sprites.remove(m)
            minions_killed = []
            stage_index += 1
        else:
            player.NEXT_WIN = False
        
    old_tick = current_tick # pygame.time.get_ticks()
