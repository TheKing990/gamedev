

from utils import *
class Enemy:

    def __init__(self, filename, pos, vel,health, attack):
        self.filename = filename
        self.health = health
        self.attack = attack
        self.pos = vector2(pos.x,pos.y)
        self.vel = vector2(vel.x,vel.y)

