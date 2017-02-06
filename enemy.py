

from utils import *

class Enemy:

    def __init__(self, name, attack, health):

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

    def __init__(self,filename, pos, vel):
        self.filename = filename
        self.pos = vector2(pos.x, pos.y)
        self.vel = vector2(vel.x,vel.y)

        super().__init__(name = "Minion", attack=20, health=100)




