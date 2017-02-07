

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
