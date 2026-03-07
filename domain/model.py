from common.constants import *
from common.characters import *
from common.playground import *
from common.keymap import Command
from .entity import Entity, Player, Item
from .navigator import Navigator
from .monsters import Zombie, Snake, Ogre, Vampire, Ghost, Mimic
from .dungeon import Room, Corridor
from .layout import Layout
from common.keymap import Command
from math import sin, cos, pi
from .bresenham import Bresenham


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
        
        self._matrix = None
        self._rooms = [Room(r) for r in data['rooms']]
        self._corridors = [Corridor(c) for c in data['corridors']]
        self._layout = Layout().create_layout(self._rooms, self._corridors)
        
        self._player = Player(data.get('player'), self._nav)

        self._create_matrix()
        self._monsters_from_dict(data['monsters'])
        self._items_from_dict(data['items'])
        
        self._visited = [0] * (ROOMS + len(self._corridors))
        self._explored = {tuple(i) for i in data.get('explored', set())}
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
                self._doors[item.door.pos] = item.door
                del self._matrix[item.door.pos]
      
    def update(self, command):
        self._danger = []
        if self._gamestate == NORMAL:
            if isinstance(command, Command):
                if command == Command.CHANGE_RENDER:
                    self._player.angle = 1/2
                    return
                self._move_player(command)
                if command not in (Command.ROTATE_LEFT, Command.ROTATE_RIGHT):
                    self._handle_monsters()          
            elif command in 'hjkum':
                self._gamestate = self.BACKPACK_SHOW_MENU[command]
            else:
                return      
        else:
            if self._player.use_backpack(self._gamestate, command):
                self._handle_monsters()
            self._gamestate = NORMAL
        if self._player.health <= 0:
            self._gamestate = GAMEOVER
            return
        
    def _get_pos(self, command):


        angle_delta = 1/16
        
        if command == Command.ROTATE_LEFT:
            self._player.angle -= angle_delta
            return self._player.pos
        elif command == Command.ROTATE_RIGHT:
            self._player.angle += angle_delta
            return self._player.pos
        
        y, x = self._player.pos
        if command == Command.MOVE_LEFT:
            return y, x - 1
        if command == Command.MOVE_RIGHT:
            return y, x + 1

        angle = (self._player.angle + 0.0001) * pi
        s = round(sin(angle))
        c = round(cos(angle))
        if abs(s) > abs(c):
            c = 0
        else:
            s = 0

        if command == Command.MOVE_FORWARD:
            y += s
            x += c
        elif command == Command.MOVE_BACK:
            y -= s
            x -= c
        
        return y, x

    def _move_player(self, command):
        pos = self._get_pos(command)
        if pos == self._player.pos:
            return
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
            self.add_danger(f'Open the door with the {self._doors[pos].color + '&\033[0m'}!')
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
        self._player.update()

    def open_door(self, key):
        if key.door.pos in self._doors:
            y0, x0 = key.door.pos
            y1, x1 = self._player.pos
            if abs(x1 - x0) + abs(y1 - y0) != 1:
                self.add_danger(f'Find the {key.color + "door" + "\033[0m"} to open with the key!')
                return False
            else:
                del self._doors[key.door.pos]
                self._matrix[key.door.pos] = key.door.id
                return True
        # else:
        #     self.add_danger('You need key for the door!')

    def _update_visible(self, visible):
        y, x = self._player.pos
        indexes = set()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            pos = (y + dy, x + dx)
            idx = self._matrix.get(pos)
            while idx is not None:
                if idx not in indexes:
                    indexes.add(idx)
                    if idx < ROOMS:
                        r = self._rooms[idx]
                    else:
                        r = self._corridors[idx - ROOMS]
                    for position in r.floor:
                        self._check_visibility(position, visible)
                    for position in r.walls:
                        self._check_visibility(position, visible)
                pos = (pos[0] + dy, pos[1] + dx)
                idx = self._matrix.get(pos)
            if pos in self._doors:
                visible.add(pos)

    def _check_visibility(self, pos, visible):
            if Bresenham().find_path(self._player.pos, pos, self):
                visible.add(pos)


    @property
    def first_screen(self):
        visible = {pos for pos in self._explored}
        # for i in range(ROOMS):
        #     if self._visited[i]:
        #         visible.update(self._rooms[i].walls)
        return visible

    @property
    def data_for_rendering(self):
        pos = self._player.pos
        idx = self._matrix[pos] #the room player in
        visible = set()
        if idx < ROOMS:
            r = self._rooms[idx]
            visible.update(r.walls)
            if not self._visited[idx]:
                self._visited[idx] = 1
                self._explored.update(r.walls)
        else:
            self._explored.add(pos)
        self._update_visible(visible)
        visible.add(pos)
        return visible
    
    def visible(self, pos):
        if pos == self._player.pos:
            return self._player
        if pos in self._monsters:
            return self._monsters[pos]
        if pos in self._items:
            return self._items[pos]
        if pos in self._doors:
            return self._doors[pos]
        else:
            return self._layout.get(pos, FLOOR)

    def layout(self, pos):
        if pos in self._explored:
            return self._layout[pos]
        return GROUND

    def place_entity(self, pos, e:Entity):
        if self.walkable(pos):
            self._matrix[(e.pos)][1] = None
            e.pos = pos
            self._matrix[pos][1] = e
    
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


    def data_for_saving(self):
        data = {}
        data['explored'] = [i for i in self._explored]
        data['player'] = self._player.to_dict()
        data['monsters'] = [m.to_dict() for m in self._monsters.values()]
        data['items'] = [item.to_dict() for item in self._items.values()]
        data['rooms'] = [r.to_dict() for r in self._rooms ]
        data['corridors'] = [r.to_dict() for r in self._corridors ]
        # data['visited'] = self._visited  
        data['statistics'] = self._statistics

        return data