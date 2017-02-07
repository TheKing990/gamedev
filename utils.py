#!/usr/bin/python2

import math
import pygame

SS = (1024, 700)

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
            self.size = self.image_l.get_size()
            self.radius = math.sqrt((self.size[0] ** 2) + (self.size[1] ** 2))
            self.radius = int(self.radius / 2) - 1 # make radius smaller
            
        self.position = vector2(pos.x, pos.y)
        self.velocity = vector2(vel.x, vel.y)

    def load_image(self, filename):
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 75))
        self.size = self.image.get_size()
        self.radius = math.sqrt((self.size[0] ** 2) + (self.size[1] ** 2))
        self.radius = int(self.radius / 2) - 1 # make radius smaller
            
    def update(self, delta):
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
        dist = cn.magnitude()
        if dist < (self.radius + other.radius): # collision?
            scale_factor = 0.5 * ((self.radius + other.radius) - dist)
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
        screen.blit(self.image, (self.position.x, self.position.y))

class player(sprite):
    def __init__(self, img_fn, pos, vel, name=None):
        if name:
            self.name = name
        else:
            self.name = "Minion"
        self.image = pygame.image.load(img_fn).convert_alpha()
        self.image_l = pygame.transform.scale(self.image, (75, 75))
        self.image_r = pygame.transform.flip(self.image_l, True, False)
        self.image_show = self.image_r
        self.size = self.image_l.get_size()
        self.radius = math.sqrt((self.size[0] ** 2) + (self.size[1] ** 2))
        self.radius = int(self.radius / 2)
        self.position = vector2(pos.x, pos.y)
        self.velocity = vector2(vel.x, vel.y)
        self.color = [0, 0, 0]
        self.shield = False

    def pic_center(self):
        size = self.image_show.get_size()
        center = (int(self.position.x + (size[0] / 2)),
                  int(self.position.y + (size[1] / 2))
                  )
        return center

    def update(self, delta):
        self.position = self.position.add(self.velocity.scale(delta))

        center = self.pic_center() # 0 = x, 1 = y
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
            self.position.x -= s_right - SS[0]
            #self.velocity.x = -(self.velocity.x)
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

    def collision(self, other):
        cn = self.position.subtract(other.position)
        dist = cn.magnitude()
        if dist < (self.radius + other.radius): # collision?
            scale_factor = 0.5 * ((self.radius + other.radius) - dist)
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
        if self.shield:
            pygame.draw.circle(screen,
                               (self.color[0], self.color[1], self.color[2]),
                               self.pic_center(),
                               self.radius, 2)
        screen.blit(self.image_show, (self.position.x, self.position.y))
