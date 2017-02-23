#!/usr/bin/python2

import math
import pygame
import os

SS = (1024, 700)

# puts images in a folder in an array.
def load_Image(path, size=(75, 75)):
    images = []
    for files in os.listdir(path):
        image = pygame.image.load(path + files).convert_alpha()
        image = pygame.transform.scale(image, size)
        images.append(image)
    return images

# flips images in an array
def flip_array_images(arr):
    images1 = []
    for i in arr:
        i = pygame.transform.flip(i, True, False)
        images1.append(i)
    return images1
    #return [pygame.transform.flip(i, True, False) for i in arr]

class vector2:
    # constructor
    def __init__(self, x, y):
        # unlike C++?/Java, no implicit "this" pointer
        # instead, reference is passed in as first argument (self in this case)
        self.x = x
        self.y = y

    # method definitions
    def add(self, other):
        v = vector2(self.x + other.x, self.y + other.y)
        return v

    def subtract(self, other):
        v = vector2(self.x - other.x, self.y - other.y)
        return v

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return vector2(0, 0)
        v = vector2(self.x / float(mag), self.y / float(mag))
        return v

    def scale(self, scalar):
        v = vector2(self.x * scalar, self.y * scalar)
        return v

    def dot_prod(self, other):
        return self.x * other.x + self.y * other.y

    def tangent(self):
        return vector2(self.y, -self.x)

    # overload return-this-as-string for printing
    def __str__(self):
        # format allows you to replace "{}" with variable values
        return '({x}, {y})'.format(x=self.x, y=self.y)

# basic sprite class
class sprite(object):
    def __init__(self, img_fn, pos, vel):
        if img_fn:
            self.image = pygame.image.load(img_fn).convert()
            self.image = pygame.transform.scale(self.image, (75, 75))
            self.size = self.image.get_size()
            self.radius = math.sqrt((self.size[0] ** 2) + (self.size[1] ** 2))
            self.radius = int(self.radius / 4) - 1 # make radius smaller

        self.position = vector2(pos.x, pos.y)
        self.velocity = vector2(vel.x, vel.y)

    def load_image(self, filename, size=None):
        if not size:
            size = (75, 75)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.size = self.image.get_size()
        self.radius = math.sqrt((self.size[0] ** 2) + (self.size[1] ** 2))
        self.radius = int(self.radius / 2) - 1 # make radius smaller

    def flip_image(self):
        return pygame.transform.flip(self.image, True, False)

    def pic_center(self):
        size = self.image.get_size()
        center = (int(self.position.x + (size[0] / 2)),
                  int(self.position.y + (size[1] / 2))
                  )
        return center

    def update(self, delta, player=None):
        self.position = self.position.add(self.velocity.scale(delta))
        max_x = self.position.x + self.size[0]
        min_x = self.position.x
        max_y = self.position.y
        min_y = self.position.y - self.size[1]

        if max_x > SS[0]: # right wall
            self.position.x -= max_x - SS[0]
            self.velocity.x = -self.velocity.x
        if min_x < 0: # left wall
            self.position.x = 0
            self.velocity.x = -self.velocity.x
        if max_y > SS[1]: # bottom wall
            self.position.y -= self.position.y - SS[1]
        if min_y < 0: # top wall
            self.position.y = 0

    def collision(self, other):
        cn = self.position.subtract(other.position)
        center = self.pic_center()
        other_center = other.pic_center()
        cn_c = vector2(center[0], center[1]).subtract(vector2(other_center[0], center[1]))
        dist = cn_c.magnitude()
        if hasattr(other, "shield"):
            if other.shield:
                o_radius = other.radius * 3.5
            else:
                o_radius = other.radius
        else:
            o_radius = other.radius
        if dist < (self.radius + o_radius): # collision?
            scale_factor = 0.5 * ((self.radius + o_radius) - dist)
            diff = cn.normalize().scale(scale_factor)

            # move balls away from each other
            self.position = self.position.add(diff)
            other.position = other.position.subtract(diff)

            # new velocity calculation
            cn = cn.normalize()
            ct = cn.tangent()

            dp_ns = self.velocity.dot_prod(cn)
            dp_no = other.velocity.dot_prod(cn)
            dp_ts = self.velocity.dot_prod(ct)
            dp_to = other.velocity.dot_prod(ct)

            vn_s = cn.scale(dp_ns)
            vn_o = cn.scale(dp_no)
            vt_s = ct.scale(dp_ts)
            vt_o = ct.scale(dp_to)

            self.velocity = vt_s.add(vn_o)
            other.velocity = vt_o.add(vn_s)

    def draw(self, screen):
        #pygame.draw.circle(screen, (255, 0, 0),
        #                   self.pic_center(),
        #                   int(self.radius), 2)
        screen.blit(self.image, (self.position.x, self.position.y))

class player(sprite):
    NEXT_WIN = False
    def __init__(self, img_fn, pos, vel, sdx=None, name=None):
        if name:
            self.name = name
        else:
            self.name = "Minion"
        self.image = pygame.image.load(img_fn).convert_alpha()
        size = self.image.get_size()
        self.image_r = pygame.transform.scale(self.image,
                                              (int(size[0] * 0.2),
                                               int(size[1] * 0.2)))
        self.image_l = pygame.transform.flip(self.image_r, True, False)
        self.image_show = self.image_r
        self.size = self.image_l.get_size()
        self.radius = math.sqrt((self.size[0] ** 2) + (self.size[1] ** 2))
        self.radius = int((self.radius / 3) * 0.30)
        self.position = vector2(pos.x, pos.y)
        self.velocity = vector2(vel.x, vel.y)
        self.hero_mode = False # for testing purposes, don't let player die


        ''' things you need for the shield '''
        self.shield = False
        self.shiled_hold = False
        self.facing_right = True
        self.facing_left = False

        self.shield_right_sprites = load_Image('art/apprentice_moves/shield/', self.size)
        self.shield_sprites = self.shield_right_sprites
        self.shield_left_sprites  = flip_array_images(self.shield_right_sprites)
        self.index = 0
        self.shield_current_Image = self.shield_sprites[self.index]
        '''end of shield'''

        '''moving normal without shield'''
        self.walk_images = load_Image('art/apprentice_moves/normal_move/', self.size)
        self.walk_right = self.walk_images
        self.walk_left = flip_array_images(self.walk_images)
        self.walking_index = 0
        self.walking_current = self.walk_images[self.walking_index]

        self.current_time = 0
        self.animation_frames = 125
        self.current_frame = 0

        self.hits = 0
        self.sdx = sdx

        self.shield_available = True
        self.shield_timer = 0
        self.shield_maxtime = 1500
        self.shield_cooldown_timer = 0
        self.shield_cooldown = 800

    def pic_center(self):
        size = self.image_show.get_size()
        center = (int(self.position.x + (size[0] / 2)),
                  int(self.position.y + (size[1] / 2))
                  )
        return center

    def update(self, delta, player_s=None):
        self.position = self.position.add(self.velocity.scale(delta))

        center = self.pic_center() # 0 = x, 1 = y
        #print("the current velocity is " + str(self.velocity.x))
        if self.velocity.x > 0:
            self.facing_left = False
            self.facing_right = True
            #choosing the images facing right
            self.shield_sprites = self.shield_right_sprites
            self.walk_images = self.walk_right
        elif self.velocity.x < 0:
            self.facing_left = True
            self.facing_right = False
            # choosing the flip side of images
            self.shield_sprites = self.shield_left_sprites
            self.walk_images = self.walk_left

        if self.shield: # animate shield
            self.current_time += delta
            if self.current_time >= self.animation_frames:
                self.current_time = self.animation_frames - self.current_time
                self.index += 1
                if self.index < len(self.shield_sprites):
                    self.shield_current_Image = self.shield_sprites[self.index]
                else:
                    self.index = len(self.shield_sprites) - 1
        else:
            self.current_time = 0
            self.index = 0
                
        """
        #creating animation for shield
        self.current_frame +=1
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0

            if self.shiled_hold != True:
                self.index = (self.index + 1) % len(self.shield_sprites)
                if self.index == 2:

                    self.shield_current_Image = self.shield_sprites[2]
                    self.shiled_hold = True
                else:
                    self.shield_current_Image = self.shield_sprites[self.index]
        """
        
        if self.shield:
            s_top = center[1] - self.radius
            s_right = center[0] + self.radius
            s_bottom = center[1] + self.radius
            s_left = center[0] - self.radius
        else:
            s_top = self.position.y
            s_right = self.position.x + self.size[0]
            s_bottom = self.position.y + self.size[1]
            s_left = self.position.x

        if s_right > SS[0]: # right wall
            player.NEXT_WIN = True
            self.position.x -= s_right - SS[0]
        #    #self.velocity.x = -(self.velocity.x)
        if s_left < 0: # left wall
            self.position.x += abs(s_left)
            #self.velocity.x = -(self.velocity.x)
        if s_bottom > SS[1]: # bottom wall
            self.position.y -= s_bottom - SS[1]
            #self.velocity.y = -(self.velocity.y)
        if s_top < 0: # top wall
            self.position.y += abs(s_top)
            #self.velocity.y = -(self.velocity.y)

        if self.velocity.x > 0:
            self.image_show = self.image_r
        elif self.velocity.x < 0:
            self.image_show = self.image_l

        # shield usage limit code
        if self.shield:
            self.shield_timer += delta
            if self.shield_timer >= self.shield_maxtime:
                self.shield = False
                self.shield_available = False
                self.shield_cooldown_timer = self.shield_maxtime - self.shield_timer
        else:
            self.shield_cooldown_timer += delta
            if self.shield_cooldown_timer >= self.shield_cooldown:
                self.shield_available = True
                self.shield_cooldown_timer = 0
            self.shield_timer = 0
        
        if self.hero_mode:
            self.hits = 0


    def collision(self, other):
        center = self.pic_center()
        if self.shield:
            radius = self.radius * 3.5
        else:
            radius = self.radius
        if hasattr(other, "hits"): # if final boss, make y pos the same
            # boss is on higher ground so we have to lower it for correct
            # collision
            cn = self.position.subtract(vector2(other.position.x, self.position.y))
            cn_c = vector2(center[0], center[1]).subtract(vector2(other.pic_center()[0], center[1]))
        else:
            other_center = other.pic_center()
            cn_c = vector2(center[0], center[1]).subtract(vector2(other_center[0], other_center[1]))
            cn = self.position.subtract(other.position)
        dist = cn_c.magnitude()
        if dist < (radius + other.radius): # collision?
            scale_factor = 0.5 * ((radius + other.radius) - dist)
            diff = cn.normalize().scale(scale_factor)

            # move balls away from each other
            self.position = self.position.add(diff)
            other.position = other.position.subtract(diff)

            # new velocity calculation
            cn = cn.normalize()
            ct = cn.tangent()

            dp_ns = self.velocity.dot_prod(cn)
            dp_no = other.velocity.dot_prod(cn)
            dp_ts = self.velocity.dot_prod(ct)
            dp_to = other.velocity.dot_prod(ct)

            vn_s = cn.scale(dp_ns)
            vn_o = cn.scale(dp_no)
            vt_s = ct.scale(dp_ts)
            vt_o = ct.scale(dp_to)

            self.velocity = vt_s.add(vn_o)
            other.velocity = vt_o.add(vn_s)
            if not self.shield:
                self.sdx.play()
                self.hits = 15
        if self.hero_mode:
            self.hits = 0

    def draw(self, screen):
        if self.shield:
            radius = int(self.radius * 3.5)
        else:
            radius = self.radius
        #pygame.draw.circle(screen, (255, 0, 0),
        #                   self.pic_center(),
        #                   radius, 2)
        if self.shield:
            screen.blit(self.shield_current_Image, (self.position.x, self.position.y))
        else:
            screen.blit(self.image_show, (self.position.x, self.position.y))
