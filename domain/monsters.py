from common.characters import *
from .entity import Character
from .navigator import Navigator
from random import randint
from globals.globals import global_counter
import sys


class Monster(Character):
    def __init__(self, id, pos, r):
        super().__init__(id, pos)
        self.room = r
        self._patrol_moves = ((1, 0), (0, 1), (-1, 0), (0, -1))
        self._go_home_moves = self._patrol_moves


    def set_features(self, data, nav):
        for k, v in data.items():
            setattr(self, k, v)
        self._nav = nav

    def set_init_values(self, k):
        with open ('adapter.txt', 'a') as f:
            f.write(f'monster: {self.id} ')
            for value in ('health', 'hostility', 'dexterity', 'strength'):
                val = randint(getattr(self, 'MIN_' + value), getattr(self, 'MAX_' + value))
                val = round(val * k)
                setattr(self, value, val)
                f.write(f'{value} - {val} ')
            f.write('\n')

    def drop_treasure(self):
        return randint(1, self.hostility + self.strength + self.dexterity+ self.MAX_health)

    def __repr__(self):
        return f'({self.id}, {self.hostility}, {self.pos})'

    def _patrol(self):
        idx = randint(0, len(self._patrol_moves) - 1)
        pos = (self.pos[0] + self._patrol_moves[idx][0], self.pos[1] + self._patrol_moves[idx][1])
        self._nav.place_entity(pos, self)

    def move(self, player):
        if self._player_visible(player):
            path = self._get_path_to_player(player)
            if path:
                self._nav.place_entity(path[0], self)
            else:
                # sys.stdout.write(f'\033[{1 + global_counter()};{104}H{self.id} must attack player')
                self.attack(player)
        else:
            if self.room != self._nav.room_number(self.pos):
                self._go_home()
            else:
                self._patrol()

    def _go_home(self):
        stack = [self.pos]
        path = {self.pos: None}
        while stack:
            new_stack = []
            for pos in stack:
                for move in self._go_home_moves:
                    new_pos = (pos[0] + move[0], pos[1]+ move[1])
                    if new_pos not in path:
                        room = self._nav.room_number(new_pos)
                        if room is not None:
                            if self.room == room:
                                while pos != self.pos:
                                    new_pos = pos
                                    pos = path[pos]
                                self._nav.place_entity(new_pos, self)
                                return
                            new_stack.append(new_pos)
                            path[new_pos] = pos
            stack = new_stack

    def _player_visible(self, player): 
        y0, x0 = self.pos
        y1, x1 = player.pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        if max(dx, dy) > self.hostility:
            return False
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        x, y = x0, y0
        if dx > dy:
            d = 2*dy - dx
            while True: 
                x += sx
                if y == y1 and x == x1:
                    return True
                if not self._nav.valid((y, x)):
                    return False          
                if d >= 0:
                    y += sy      
                    if y == y1 and x == x1:
                        return True
                    d -= 2*dx
                    if not self._nav.valid((y, x)):
                        return False
                d += 2*dy        
        else:        
            d = 2*dx - dy
            while True:
                y += sy       
                if y == y1 and x == x1:
                    return True   
                if not self._nav.valid((y, x)):
                    return False
                if d >= 0:
                    x += sx  
                    if y == y1 and x == x1:
                        return True   
                    d -= 2*dy  
                    if not self._nav.valid((y, x)):
                        return False
                d += 2*dx   

    def _get_path_to_player(self, player): 
        y0, x0 = self.pos
        y1, x1 = player.pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        x, y = x0, y0
        path = []
        if dx > dy:
            d = 2*dy - dx
            while True: 
                x += sx
                if y == y1 and x == x1:
                    return path         
                path.append((y, x))
                if d >= 0:
                    y += sy      
                    if y == y1 and x == x1:
                        return path
                    d -= 2*dx
                    path.append((y, x))
                d += 2*dy                        
        else:        
            d = 2*dx - dy
            while True:
                y += sy       
                if y == y1 and x == x1:
                    return path   
                path.append((y, x))
                if d >= 0:
                    x += sx  
                    if y == y1 and x == x1:
                        return path   
                    d -= 2*dy  
                    path.append((y, x))
                d += 2*dx 

    def __repr__(self):
        return repr({k: v for k, v in self.__dict__.items() if not k.startswith('__')})

    def to_dict(self):
        return {
        'id': self.id,
        'pos': self.pos, 
        'room': self.room,
        'hostility': self.hostility,
        'dexterity': self.dexterity, 
        'strength': self.strength, 
        'health': self.health
        }
    
'', 'hostility', 'dexterity', ''
class Snake(Monster):
    MIN_health = 4
    MAX_health = 6
    MIN_strength = 2
    MAX_strength = 3
    MIN_dexterity = 6
    MAX_dexterity = 8
    MIN_hostility = 5
    MAX_hostility = 6

    def __init__(self, pos=None, r=None):
        super().__init__(SNAKE, pos, r)
        # self.health = self.max_health = 20 + level * 5
        # self.dexterity= 25 + level
        # self.strength = 8 + level
        # self.hostility = 10
        self._patrol_moves = ((1, 1), (-1, 1), (1, -1), (-1, -1))
        # self._go_home_moves = ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))
        
class Ogre(Monster):

    MIN_health = 15
    MAX_health = 18
    MIN_strength = 5
    MAX_strength = 6
    MIN_dexterity = 1
    MAX_dexterity = 2
    MIN_hostility = 4
    MAX_hostility = 5

    def __init__(self, pos=None, r=None):
        super().__init__(OGRE, pos, r)
        # self.health = 0
        # self.dexterity= 5 + level
        # self.strength = 24 + level
        # self.hostility = 6

class Vampire(Monster):

    MIN_health = 10
    MAX_health = 12
    MIN_strength = 4
    MAX_strength = 5
    MIN_dexterity = 5
    MAX_dexterity = 6
    MIN_hostility = 5
    MAX_hostility = 6

    def __init__(self, pos=None, r=None):
        super().__init__(VAMPIRE, pos, r)
        # self.health = self.max_health = 25 + level * 5
        # self.dexterity= 16 + level
        # self.strength = 10 + level
        # self.hostility = 8

class Ghost(Monster):

    MIN_health = 5
    MAX_health = 7
    MIN_strength = 2
    MAX_strength = 3
    MIN_dexterity = 7
    MAX_dexterity = 8
    MIN_hostility = 3
    MAX_hostility = 4

    def __init__(self, pos=None, r=None):
        super().__init__(GHOST, pos, r)
        # self.health = self.max_health = 15 + level * 5
        # self.dexterity= 18 + level
        # self.strength = 4 + level
        # self.hostility = 4

class Zombie(Monster):

    MIN_health = 8
    MAX_health = 12
    MIN_strength = 3
    MAX_strength = 5
    MIN_dexterity = 1
    MAX_dexterity = 2
    MIN_hostility = 3
    MAX_hostility = 4

    def __init__(self, pos=None, r=None):
        super().__init__(ZOMBIE, pos, r)
        # self.health = self.max_health = 30 + level * 5
        # self.dexterity= 3 + level
        # self.strength = 8 + level
        # self.hostility = 5











