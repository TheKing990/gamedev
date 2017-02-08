#!/usr/bin/python2

import pygame
import sys
from utils import vector2, sprite, player
from enemy import Enemy, Minion

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
WIZARD_FILE = 'art/apprentice_moves/move1.png' # 'art/Wizard_Male.png'
MINION_FILE = 'art/Retrowizard_evil.png'
BACKGROUND_F = 'art/forest.png'
BACKGROUND_C = 'art/castle.png'

def loadbackground(b_image):
    bg = pygame.image.load(b_image).convert()
    bg = pygame.transform.scale(bg, SCREEN_SIZE)
    return bg

# setup goes here
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("The Apprentice")

accel = vector2(0.025, 0)

background = loadbackground(BACKGROUND_F)

sprites = [player(WIZARD_FILE, vector2(100, 600), vector2(0, 0), name="Player"),
           Minion(MINION_FILE, vector2(700, 600), vector2(-0.5, 0))
           ]
player_s = sprites[0]

old_tick = pygame.time.get_ticks()

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
        
    if keys[pygame.K_a]: # a is currently pressed
        player_s.velocity.x -= 0.002
    elif keys[pygame.K_d]: # d is currently pressed
        player_s.velocity.x += 0.002
    else:
        if player_s.velocity.x > 0:
            player_s.velocity.x -= accel.scale(delta).x
            if player_s.velocity.x < 0:
                player_s.velocity.x = 0
        elif player_s.velocity.x < 0:
            player_s.velocity.x += accel.scale(delta).x
            if player_s.velocity.x > 0:
                player_s.velocity.x = 0
    
    #accel = accel.scale(delta)
    for s in sprites:
        s.update(delta, player_s)
    
    for i in range(0, len(sprites)):
        for other in sprites[i + 1:]:
            sprites[i].collision(other)

    # draw to screen and flip
    # screen.fill(COLORS['yellow'])
    screen.blit(background, (0, 0))
    for s in sprites:
        s.draw(screen)
    
    pygame.display.flip()
    old_tick = current_tick # pygame.time.get_ticks()
    
