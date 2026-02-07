from common.constants import *
from .entity import Zombie, Snake, Ogre, Vampire, Ghost, Player, Entity
from random import randint, choice
import sys


class Model:

    def __init__(self, level, matrix, rooms, start_room):
        self._count = 0
        self.level = level
        self.matrix = matrix
        self.rooms = rooms
        self._entities = set()
        self.passed = False
        self._place_entities(start_room)
        # for e in self._entities:
        #     r = e.room
        #     if r < 8:
        #         e.room = r + 1
        #     else:
        #         e.room = 0
        #     sys.stdout.write(f'\033[{1 + self._count};{103}H{e.id}, {r}, motherroom={e.room}')
        #     self._count += 1
           

    def handle_move(self, char):
        new_y, new_x = self.player.pos
        if char == 'w':
            new_y -= 1
        elif char == 'a':
            new_x -= 1
        elif char == 's':
            new_y += 1
        elif char == 'd':
            new_x += 1
        pos = (new_y, new_x)
        value = self.matrix.get(pos)
        if value is not None:
            value = value[1]
            if value == EXIT:
                self.passed = True
            elif value is None:
                self.matrix[pos][1] = self.player
                self.matrix[self.player.pos][1] = None
                self.player.pos = pos
            elif isinstance(value, Entity):
                self.matrix[pos][1] = self.player
                self.matrix[self.player.pos][1] = None
                self.player.pos = pos
                self._entities.discard(value)

        self.handle_enemies()

    def room_number(self, pos):
        value = self.matrix.get(pos)
        if value is not None:
            return value[0] 
        return None

    def walkable(self, pos):
        value = self.matrix.get(pos)
        return value is not None and value[1] is None
    
    # def valid(self, pos):
    #     return pos in self.matrix

    def place_entity(self, pos, e:Entity):
        if self.walkable(pos):
            self.matrix[(e.pos)][1] = None
            e.pos = pos
            self.matrix[pos][1] = e


    def monster_attacks_player(self, entity):
        pass

    def _get_pos(self, r):
        pos = choice(list(self.rooms[r].floor))
        while self.matrix[pos][1] is not None:
            pos = choice(list(self.rooms[r].floor))
        return pos
        
    def _place_entities(self, start):
        pos = self._get_pos(start)
        self.player = Player(pos)
        self.matrix[pos][1] = self.player
        rooms = {start,}
        monsters = [Zombie, Snake, Ogre, Vampire, Ghost]
        # monsters = [Zombie]
        for i in range(self.level):
            monsters.append(choice(monsters))
        for m in monsters:
            r = randint(0, ROOMS - 1)
            while r in rooms:
                r = randint(0, ROOMS - 1)
            rooms.add(r)
            if len(rooms) == ROOMS:
                rooms = {start,}
            pos = self._get_pos(r)
            monster = m(pos, r, self.level)
            self.matrix[pos][1] = monster
            self._entities.add(monster)

    def entities(self):
        result = {(e.pos, e.id) for e in self._entities}
        result.add((self.player.pos, self.player.id))
        return result
    
    def handle_enemies(self):
        for e in self._entities:
            e.move(self, self.player)


