from common.constants import *
from common.characters import *
from common.playground import *
from .entity import Entity, Player, Item
# from random import randint, choice
from .navigator import Navigator
from .monsters import Zombie, Snake, Ogre, Vampire, Ghost, Mimic
from .dungeon import Room, Corridor
from .layout import Layout
# import sys


class Model:

    BACKPACK_SHOW_MENU = {'j': FOOD, 'h': WEAPON, 'u': SCROLL, 'k':POTION, 'm': KEY}
    MONSTERS_DICT = dict(zip(MONSTERS, (Zombie, Vampire, Ghost, Ogre , Snake)))

    def __init__(self, data, statistics=None):
        data = data.data
        if statistics: # continue to play
            self._statistics = {k: v for k, v in statistics.items()}
            self._statistics["monsters_killed"] = 0
            self._statistics['path_length'] = data['path_length']
        elif data.get('statistics') is not None: # saved game
            self._statistics = {k: v for k, v in data.get('statistics').items()}
        else: # new game
            self._statistics = {k: 0 for k in STATISTICS}
            self._statistics['level_reached'] = 1
            self._statistics['path_length'] = data['path_length']

        self.passed = False
        self._gamestate = NORMAL
        self._nav = Navigator(self)
        self._visible = set()
        self._matrix = None
        self._rooms = [Room(r) for r in data['rooms']]
        self._corridors = [Corridor(c) for c in data['corridors']]
        self._layout = Layout().create_layout(self._rooms, self._corridors)
        self._explored = {tuple(i) for i in data.get('explored', set())}
        self._player = Player(data.get('player'), self._nav)

        self._create_matrix()
        self._monsters_from_dict(data['monsters'])
        self._items_from_dict(data['items'])
        
        if data.get('visited'):
            self._visited = [i for i in data['visited']]
        else:
            self._visited = [0] * ROOMS
        self._danger = []
        
    def _monsters_from_dict(self, data:list):
        self._monsters = {}
        for m in data:
            monster = self.MONSTERS_DICT.get(m['id'], Mimic)()
            monster.set_features(m, self._nav)
            self._monsters[monster.pos] = monster

    def _items_from_dict(self, data:list):
        self._items = {}
        self._doors = {}
        for d in data:
            item = Item(d)
            self._items[item.pos] = item
            if item.id == KEY:
                self._doors[item.door.pos] = item.color
                del self._matrix[item.door.pos]
      
    def update(self, char):
        self._danger = []
        if self._gamestate == NORMAL:
            if char in 'wasd':
                self._move_player(char)
                self._handle_monsters()
            elif char in 'hjkum':
                self._gamestate = self.BACKPACK_SHOW_MENU[char]
            # else:
            #     self._handle_monsters()
        else:
            if self._player.use_backpack(self._gamestate, char):
                self._handle_monsters()
            self._gamestate = NORMAL
        if self._player.health <= 0:
            self._gamestate = GAMEOVER

    def _move_player(self, char):
        y, x = self._player.pos
        if char == 'w':
            pos = (y - 1, x)
        elif char == 'a':
            pos = (y, x - 1)
        elif char == 's':
            pos = (y + 1, x)
        else: # char == 'd':
            pos = (y, x + 1)
        if pos in self._monsters:
            monster = self._monsters[pos]
            if isinstance(monster, Mimic) and not monster.active:
                monster.activate()
                monster.attack(self._player)
            else:
                self._player.attack(monster)
            if monster.health <= 0:
                self._statistics["monsters_killed"] += 1
                self._statistics["treasure"] += monster.drop_treasure()
                del self._monsters[pos]
        elif pos in self._items:
            item = self._items[pos]
            if item.id == EXIT:
                self.passed = True
                self._statistics['level_reached'] += 1
            else:
                if self._player.get_item(item):
                    self._player.pos = pos
                    del self._items[pos]
                    self._statistics["steps"] += 1
        elif pos in self._doors:
            self.add_danger('You need to open the door')
        elif pos in self._matrix:
            self._player.pos = pos
            self._statistics["steps"] += 1

    def _create_matrix(self):
        self._matrix = {pos: ROOMS + i for i, c in enumerate(self._corridors) for pos in c.walls}
        for r in self._rooms:
            for floor in r.floor:
                self._matrix[floor] = r.id
            
    def _handle_monsters(self):
        for m in list(self._monsters.values()):
            old_pos = m.pos
            m.move(self._player)
            if m.pos != old_pos:
                self._monsters[m.pos] = m
                del self._monsters[old_pos]
        # self._monsters = {m.pos: m for m in self._monsters.values()}
        self._player.update()

    def open_door(self, key):
        if key.door.pos in self._doors:
            del self._doors[key.door.pos]
            self._matrix[key.door.pos] = key.door.id
        else:
            self.add_danger('You need key for the door!')

    def _update_visible(self, visible):
        y, x = self._player.pos
        for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            pos = (y + dy, x + dx)
            if pos in self._doors:
                visible.add(pos)
            value = self._matrix.get(pos)
            while value is not None:
                visible.add(pos)
                if value >= ROOMS:
                    self._explored.add(pos)
                pos = (pos[0] + dy, pos[1] + dx)
                if pos in self._doors:
                    visible.add(pos)
                value = self._matrix.get(pos)

    @property
    def first_screen(self):
        res = {pos: self._layout.get(pos, GROUND) for pos in self._explored}
        for i in range(ROOMS):
            if self._visited[i]:
                for pos in self._rooms[i].walls:
                    res[pos] = self._layout.get(pos, GROUND)
        res.update(self.data_for_rendering)
        return res

    @property
    def data_for_rendering(self):
        res = {}
        idx = self._matrix[self._player.pos] #the room player in
        visible = set()
        if idx >= ROOMS:
            pos = self._player.pos
            for i in self._corridors[idx - ROOMS].connecting:
                if pos in self._rooms[i].gate:
                    idx = i
        if idx < ROOMS:
            r = self._rooms[idx]
            if not self._visited[idx]:
                self._visited[idx] = 1
                for pos in r.walls:
                    res[pos] = self._layout[pos]
            visible.update(r.floor)
            visible.update(r.gate)
          
        self._update_visible(visible)

        for pos in visible:
            res[pos] = self._layout.get(pos, FLOOR)
        
        self._visible -= visible
        for pos in self._visible:
            res[pos] = self._layout.get(pos, GROUND)
        self._visible = visible

        for pos in self._items:
            if pos in visible:
                item = self._items[pos]
                if item.id == KEY:
                    res[pos] = item.color + item.id + '\033[0m'
                else:
                    res[pos] = item.id
        for pos in self._doors:
            if pos in visible:
                res[pos] = self._doors[pos] + 'x' + '\033[0m'

        for m in self._monsters.values():
            if m.pos in visible:
                res[m.pos] = m.id
                
        res[self._player.pos] = self._player.id

        return res

    def place_entity(self, pos, e:Entity):
        if self.walkable(pos):
            self._matrix[(e.pos)][1] = None
            e.pos = pos
            self._matrix[pos][1] = e

    def walkable(self, pos):
        return self.valid(pos) and pos not in self._items and not pos in self._monsters
    
    def valid(self, pos):
        return pos in self._matrix

    def valid_for_monsters(self, pos):
        return pos in self._matrix and pos not in self._monsters

    @property
    def backpack(self):
        if self.gamestate in (NORMAL, GAMEOVER):
            res = {(item, len(value)) for item, value in self._player.backpack.have.items()}
            res.update({
                (CURRENT_WEAPON, self._player.current_weapon.power), 
                (DEXTERITY, self._player.dexterity), 
                (STRENGTH, self._player.strength), 
                (HEALTH, self._player.health), 
                (MAX_HEALTH, self._player.max_health),
                (TREASURE, self._statistics['treasure']), 
                })
            return res
        
        if self._gamestate == KEY:
            return [d.color + d.id + '\033[0m' for d in self._player.backpack.have.get(KEY)]
        
        res = []
        for d in self._player.backpack.have.get(self.gamestate):
            d = sorted(d.to_dict().items(), key=lambda x: len(x[0]), reverse=True)
            d = ', '.join(f'{k}: {v}' for k, v in d if k != 'id' and k != 'pos')
            res.append(d)
        return res
    
    def room_number(self, pos):
        return self._matrix.get(pos)

    def place_weapon(self, pos, weapon):
        for y, x in ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            new_pos = (pos[0] + y, pos[1] + x)
            if self.walkable(new_pos):
                self._items[new_pos] = weapon
                return

    @property
    def player(self):
        return self._player

    @property
    def gamestate(self):
        return self._gamestate
    
    @property
    def level(self):
        return self._statistics['level_reached']

    @property
    def stats(self):
        return self._statistics
    
    def add_danger(self, s):
        return self._danger.append(s)

    @property
    def danger(self):
        return self._danger

    @property
    def full_statistics(self):
        d = self.stats
        d['max_health'] = self._player.max_health
        d['monsters_left'] = len(self._monsters)
        d['playground_size'] = len(self._matrix)
        d['dexterity'] = self._player.backpack.dexterity + self._player.dexterity
        d['strength'] = self._player.backpack.strength + self._player.strength
        d['health'] = self._player.backpack.health + self._player.health
        d['food'] = self._player.backpack.food
        d['weapon'] = self._player.weapon 

        return d

    def add_statistics(self, key:str, value:int=1):
        self._statistics[key] += value

    def rotate(self, direction):
        self._player.facing += direction

    def data_for_saving(self):
        data = {}
        data['player'] = self._player.to_dict()
        # data['keys'] = [k.to_dict() for k in self._keys.values()]
        data['monsters'] = [m.to_dict() for m in self._monsters.values()]
        data['items'] = [item.to_dict() for item in self._items.values()]
        data['rooms'] = [r.to_dict() for r in self._rooms ]
        data['corridors'] = [r.to_dict() for r in self._corridors ]
        data['visited'] = self._visited
        data['explored'] = [i for i in self._explored]
        data['statistics'] = self._statistics
        return data

        # with open('log.txt', 'w') as f:
        #     f.write(f'items\n{self._items}\n')
        #     f.write(f'monsters\n{self._monsters}')
        #     f.write(f'visible\n{self._visible}\n')
        #     f.write(f'visited\n{self._visited}\n')
        #     f.write(f'explored\n{self._explored}\n')
        #     f.write(f'backpack\n{self._player.backpack}\n')