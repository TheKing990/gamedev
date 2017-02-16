

from utils import *

class Enemy(sprite):

    def __init__(self, name=None, attack=0, health=0):
        super(Enemy, self).__init__(self, None, vector2(0, 0), vector2(0, 0))
        self.health = health
        self.attack = attack
        self.name = name

    def is_Alive(self):
        if self.health > 0:
            return True
        else:
            return False

    def returnHealth(self):
        if self.is_Alive() == True:
            return self.health

class Fireball(sprite):
    def __init__(self, filename, pos, vel):
        super(Fireball, self).__init__(filename, pos, vel)
        self.load_image(filename, (25, 25))
        self.image_r = self.flip_image()
        self.image_l = self.image
        self.image = self.image_r
        self.bounced = False
        self.fixed = False

    def update(self, delta):
        self.position = self.position.add(self.velocity.scale(delta))

        if self.velocity.x > 0: # moving to the right
            self.image = self.image_r
        else:
            self.image = self.image_l

    def collision(self, other):
        level_pos = self.position.add(vector2(0, 0)) # copy pos vector
        level_pos.y = other.position.y # don't change y, only x
        cn = level_pos.subtract(other.position)
        dist = cn.magnitude()
        if dist < (self.radius + other.radius): # collision
            if other.shield:
                scale_factor = (self.radius + other.radius) - dist
                diff = cn.normalize().scale(scale_factor)
                self.position = self.position.add(diff)
                self.velocity.x = -self.velocity.x
                self.bounced = True
            else: # player hit by fireball, destroy fireball
                # move fireball offscreen and wait to be removed from list
                self.position.x = -self.size[0] - 10
                other.hits += 1
                other.sdx.play()
        if other.hero_mode:
            other.hits = 0

    def collision_minion(self, other):
        level_pos = self.position.add(vector2(0, 0)) # copy pos vector
        level_pos.y = other.position.y # don't change y, only x
        cn = level_pos.subtract(other.position)
        dist = cn.magnitude()
        if dist < (self.radius + other.radius): # collision
            if self.bounced: # player bounced fireball back
                # move fireball offscreen and wait to be removed from list
                self.position.x = -self.size[0] - 10
                return True
        
class Minion(Enemy):

    def __init__(self, filename, pos, vel):
        #super(Minion, self).__init__(name="Minion", attack=20, health=100)
        self.load_image(filename)
        self.position = vector2(pos.x, pos.y)
        self.velocity = vector2(vel.x, vel.y)
        self.image_l = self.flip_image()
        self.image_r = self.image
        if vel.x > 0:
            self.image = self.image_r
        else:
            self.image = self.image_l
        self.attack_count = []
        self.attack_max = 1

    def update(self, delta, player_s=None):
        super(Enemy, self).update(delta)
        self.attack(player_s)
        if self.velocity.x > 0:
            self.image = self.image_r
        else:
            self.image = self.image_l
        for fire in self.attack_count:
            fire.update(delta)

    def draw(self, screen):
        super(Enemy, self).draw(screen)
        if not player.NEXT_WIN:
            for fire in self.attack_count:
                fire.draw(screen)

    def attack(self, player_sprite):
        # if enemy can attack, attack
        if len(self.attack_count) < self.attack_max:
            player_is_in_front = False
            if player_sprite.position.x < self.position.x and \
               self.image == self.image_l: # send fireball <-
                pos = vector2(self.position.x - 50, self.position.y + 25)
                vel = vector2(-0.5, 0)
                player_is_in_front = True
            elif player_sprite.position.x > self.position.x + self.size[0] and \
                 self.image == self.image_r: # send fireball ->
                pos = vector2(self.position.x + 50, self.position.y + 25)
                vel = vector2(0.5, 0)
                player_is_in_front = True
            if player_is_in_front:
                fire = Fireball('art/fireball.png', pos, vel)
                self.attack_count.append(fire)
        else: # if enemy used all of their attack, remove attacks not visible by
            to_remove = [] # user
            for f in self.attack_count:
                if f.position.x > SS[0]:
                    to_remove.append(f)
                if f.position.x < 0:
                    to_remove.append(f)
            for r in to_remove:
                self.attack_count.remove(r)
            
class Boss(Minion):
    def __init__(self, filename, pos, vel):
        super(Boss, self).__init__(filename, pos, vel)
        self.load_image(filename, (160, 110))
        self.image_l = self.flip_image()
        self.image_r = self.image
        if vel.x > 0:
            self.image = self.image_r
        else:
            self.image = self.image_l
        self.hits = 20

    def attack(self, player_sprite):
        super(Boss, self).attack(player_sprite)
        for i in range(len(self.attack_count)):
            if not self.attack_count[i].fixed:
                self.attack_count[i].position.y += 20
                self.attack_count[i].fixed = True

    def collision(self, other):
        original_pos = self.position.add(vector2(0, 0))
        super(Boss, self).collision(other)
        self.position.y = original_pos.y
