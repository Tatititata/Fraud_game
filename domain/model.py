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
        # monsters = [Zombie, Snake, Ogre, Vampire, Ghost]
        monsters = [Zombie]
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
            monster = m(pos)
            # monster.initial_room = r
            # monster.current_room = r
            self.matrix[pos][1] = monster
            self._entities.add(monster)

    def entities(self):
        result = {(e.pos, e.id) for e in self._entities}
        result.add((self.player.pos, self.player.id))
        return result
    
    def handle_enemies(self):
        for e in self._entities:
            if self._player_visible(e):
                self._attack(e)
            else:
                # if e.current_room != e.initial.room:
                #     self._go_home(e)
                self._patrol(e)


    def _attack(self, e:Entity):
        pass

    def _go_home(self, e:Entity):
        pass

    def _patrol(self, e:Entity):
        moves = ((1, 0), (0, 1), (-1, 0), (0, -1))
        idx = randint(0, 3)
        pos = (e.pos[0] + moves[idx][0], e.pos[1] + moves[idx][1])
        value = self.matrix.get(pos)
        if value and value[1] is None:
            self.matrix[pos][1] = e
            self.matrix[e.pos][1] = None
            e.pos = pos


    def _player_visible(self, e:Entity): 
        y0, x0 = e.pos
        y1, x1 = self.player.pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        x, y = x0, y0
        if dx > dy:
            d = 2*dy - dx
            # i = 0
            # while i < dx - 1: 
            while True: 
                x += sx
                if (y, x) == self.player.pos:
                    # sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(visible)}, p-{self.player.pos}')
                    # self._count += 1
                    return True
                if self.matrix.get((y, x)) is None or self.matrix[(y, x)][1] is not None:
                    # sys.stdout.write(f' {y}, {x} Nv')
                    return False          
                if d >= 0:
                    y += sy      
                    if(y, x) == self.player.pos:
                        return True
                    d -= 2*dx
                    if self.matrix.get((y, x)) is None or self.matrix[(y, x)][1] is not None:
                        # sys.stdout.write(f' {y}, {x} Nv')
                        return False
                d += 2*dy        
                # i += 1  
                
        else:        
            d = 2*dx - dy
            # i = 0
            # while i < dy - 1:
            while True:
                y += sy       
                if(y, x) == self.player.pos:
                    # sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(visible)}, p-{self.player.pos}')
                    # self._count += 1
                    return True   
                if self.matrix.get((y, x)) is None or self.matrix[(y, x)][1] is not None:
                    return False
                if d >= 0:
                    x += sx  
                    if(y, x) == self.player.pos:
                        return True   
                    d -= 2*dy  
                    if self.matrix.get((y, x)) is None or self.matrix[(y, x)][1] is not None:
                        return False
                d += 2*dx        
                # i += 1
                

        # sys.stdout.write(f'{e.pos}, {str(visible)}, {self.player.pos}')
        return visible
    
    def _get_path_to_player(self, e:Entity): 
        # self._count = 0
        y0, x0 = e.pos
        y1, x1 = self.player.pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        x, y = x0, y0
        visible = []
        if dx > dy:
            d = 2*dy - dx
            # i = 0
            # while i < dx - 1: 
            while True: 
                x += sx
                if(y, x) == self.player.pos:
                    # sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(visible)}, p-{self.player.pos}')
                    # self._count += 1
                    return visible
                if self.matrix.get((y, x)) is None or self.matrix[(y, x)][1] is not None:
                    sys.stdout.write(f' {y}, {x} Nv')
                    return False          
                visible.append((y, x))
                sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(visible)}, p-{self.player.pos}')
                self._count += 1
                if d >= 0:
                    y += sy      
                    if(y, x) == self.player.pos:
                        return visible
                    d -= 2*dx
                    if self.matrix.get((y, x)) is None or self.matrix[(y, x)][1] is not None:
                        sys.stdout.write(f' {y}, {x} Nv')
                        return False
                    visible.append((y, x))
                    sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(visible)}, p-{self.player.pos}')
                    self._count += 1
                d += 2*dy        
                # i += 1  
                
        else:        
            d = 2*dx - dy
            # i = 0
            # while i < dy - 1:
            while True:
                y += sy       
                if(y, x) == self.player.pos:
                    # sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(visible)}, p-{self.player.pos}')
                    # self._count += 1
                    return visible   
                if self.matrix.get((y, x)) is None or self.matrix[(y, x)][1] is not None:
                    return False
                visible.append((y, x))
                sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(visible)}, p-{self.player.pos}')
                self._count += 1
                if d >= 0:
                    x += sx  
                    if(y, x) == self.player.pos:
                        return visible   
                    d -= 2*dy  
                    if self.matrix.get((y, x)) is None or self.matrix[(y, x)][1] is not None:
                        return False
                    visible.append((y, x))
                    sys.stdout.write(f'\033[{1 + self._count};{103}He-{e.pos}, {str(visible)}, p-{self.player.pos}')
                    self._count += 1
                d += 2*dx        
                # i += 1
                

        # sys.stdout.write(f'{e.pos}, {str(visible)}, {self.player.pos}')
        return visible


