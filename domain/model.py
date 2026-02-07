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
            if value[1] == EXIT:
                self.passed = True
            elif value[1] is None:
                self.matrix[pos][1] = PLAYER
                self.matrix[self.player.pos][1] = None
                self.player.pos = pos
        self.handle_enemies()

    def room_number(self, pos):
        value = self.matrix.get(pos)
        if value is not None:
            return value[0] 
        return None

    def walkable(self, pos):
        value = self.matrix.get(pos)
        return value is not None and value[1] is None
    
    def valid(self, pos):
        return pos in self.matrix

    def place_entity(self, pos, e:Entity):
        if self.walkable(pos):
            self.matrix[(e.pos)][1] = None
            e.pos = pos
            self.matrix[pos][1] = e

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
            monster = m(pos, r)
            self.matrix[pos][1] = monster
            self._entities.add(monster)

    def entities(self):
        result = {(e.pos, e.id) for e in self._entities}
        result.add((self.player.pos, self.player.id))
        return result
    
    def handle_enemies(self):
        for e in self._entities:
            e.move(self, self.player)
            # if self._player_visible(e):
            #     path = self._get_path_to_player(e)
            #     # sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(path)}, p-{self.player.pos}')
            #     # self._count += 1
            #     self._attack(e)
            # else:
            #     # sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos},p-{self.player.pos} - NOT visible')
            #     # self._count += 1
            #     # if e.current_room != e.initial.room:
            #     #     self._go_home(e)
            #     e.patrol(self)





    # def _patrol(self, e:Entity):
    #     moves = ((1, 0), (0, 1), (-1, 0), (0, -1))
    #     idx = randint(0, 3)
    #     pos = (e.pos[0] + moves[idx][0], e.pos[1] + moves[idx][1])
    #     value = self.matrix.get(pos)
    #     if value and value[1] is None:
    #         self.matrix[pos][1] = e
    #         self.matrix[e.pos][1] = None
    #         e.pos = pos


    # def _player_visible(self, e:Entity): 
    #     y0, x0 = e.pos
    #     y1, x1 = self.player.pos
    #     dx = abs(x1 - x0)
    #     dy = abs(y1 - y0)
    #     sx = 1 if x0 < x1 else -1
    #     sy = 1 if y0 < y1 else -1
    #     x, y = x0, y0
    #     if dx > dy:
    #         d = 2*dy - dx
    #         while True: 
    #             x += sx
    #             if y == y1 and x == x1:
    #                 return True
    #             if not self.walkable(y, x):
    #                 return False          
    #             if d >= 0:
    #                 y += sy      
    #                 if y == y1 and x == x1:
    #                     return True
    #                 d -= 2*dx
    #                 if not self.walkable(y, x):
    #                     return False
    #             d += 2*dy        
    #     else:        
    #         d = 2*dx - dy
    #         while True:
    #             y += sy       
    #             if y == y1 and x == x1:
    #                 return True   
    #             if not self.walkable(y, x):
    #                 return False
    #             if d >= 0:
    #                 x += sx  
    #                 if y == y1 and x == x1:
    #                     return True   
    #                 d -= 2*dy  
    #                 if not self.walkable(y, x):
    #                     return False
    #             d += 2*dx        
    
    # def _get_path_to_player(self, e:Entity): 
    #     y0, x0 = e.pos
    #     y1, x1 = self.player.pos
    #     dx = abs(x1 - x0)
    #     dy = abs(y1 - y0)
    #     sx = 1 if x0 < x1 else -1
    #     sy = 1 if y0 < y1 else -1
    #     x, y = x0, y0
    #     visible = []
    #     if dx > dy:
    #         d = 2*dy - dx
    #         while True: 
    #             x += sx
    #             if y == y1 and x == x1:
    #                 return visible         
    #             visible.append((y, x))
    #             if d >= 0:
    #                 y += sy      
    #                 if y == y1 and x == x1:
    #                     return visible
    #                 d -= 2*dx
    #                 visible.append((y, x))
    #             d += 2*dy                        
    #     else:        
    #         d = 2*dx - dy
    #         while True:
    #             y += sy       
    #             if y == y1 and x == x1:
    #                 return visible   
    #             visible.append((y, x))
    #             if d >= 0:
    #                 x += sx  
    #                 if y == y1 and x == x1:
    #                     return visible   
    #                 d -= 2*dy  
    #                 visible.append((y, x))
    #             d += 2*dx        


