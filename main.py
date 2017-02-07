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
WIZARD_FILE = 'art/Wizard_Male.png'
MINION_FILE = 'art/Retrowizard_evil.png'

# setup goes here
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("hi there")

accel = vector2(0.025, 0)

sprites = [player(WIZARD_FILE, vector2(100, 100), vector2(0, 0), name="Player"),
           Minion(MINION_FILE, vector2(700, 100), vector2(-0.5, 0))
           ]
player = sprites[0]

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
        player.shield = True
    else:
        player.shield = False
        
    if keys[pygame.K_a]: # a is currently pressed
        player.velocity.x -= 0.002
    elif keys[pygame.K_d]: # d is currently pressed
        player.velocity.x += 0.002
    else:
        if player.velocity.x > 0:
            player.velocity.x -= accel.scale(delta).x
            if player.velocity.x < 0:
                player.velocity.x = 0
        elif player.velocity.x < 0:
            player.velocity.x += accel.scale(delta).x
            if player.velocity.x > 0:
                player.velocity.x = 0
    
    #accel = accel.scale(delta)
    for s in sprites:
        s.update(delta)
    
    for i in range(0, len(sprites)):
        for other in sprites[i + 1:]:
            sprites[i].collision(other)

    # draw to screen and flip
    screen.fill(COLORS['yellow'])
    for s in sprites:
        s.draw(screen)
    pygame.display.flip()
    old_tick = current_tick # pygame.time.get_ticks()
    
