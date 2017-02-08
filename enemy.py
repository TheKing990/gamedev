

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


class Minion(Enemy):

    def __init__(self, filename, pos, vel):
        #super(Minion, self).__init__(self, name="Minion", attack=20, health=100)
        self.load_image(filename)
        self.position = vector2(pos.x, pos.y)
        self.velocity = vector2(vel.x, vel.y)
        self.attack_count = []
        self.attack_max = 3

    def update(self, delta, player_s=None):
        super(Enemy, self).update(delta)
        self.attack(player_s)
        for fire in self.attack_count:
            fire.update(delta)

    def draw(self, screen):
        super(Enemy, self).draw(screen)
        for fire in self.attack_count:
            fire.draw(screen)

    def attack(self, player_sprite):
        # if enemy can attack, attack
        if len(self.attack_count) < self.attack_max:
            if player_sprite.position.x < self.position.x: # send fireball <-
                pos = vector2(self.position.x - 50, self.position.y + 25)
                vel = vector2(-0.5, 0)
            else: # send fireball ->
                pos = vector2(self.position.x + 50, self.position.y + 25)
                vel = vector2(0.5, 0)
                
            fireball = sprite('art/fireball.png', pos, vel)
            fireball.load_image('art/fireball.png', (25, 25))
            self.attack_count.append(fireball)
        else: # if enemy used all of their attack, remove attacks not visible by
            to_remove = [] # user
            for f in self.attack_count:
                if f.position.x > SS[0]:
                    to_remove.append(f)
                if f.position.x < 0:
                    to_remove.append(f)
            for r in to_remove:
                _ = self.attack_count.remove(r)
            
