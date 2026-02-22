from common.constants import *
from common.characters import *
from common.playground import *
from .entity import Entity, Player, Item
from random import randint, choice
from .navigator import Navigator
from .monsters import Zombie, Snake, Ogre, Vampire, Ghost, Mimic
from .dungeon import Room, Corridor
import sys


class Model:

    BACKPACK_SHOW_MENU = {'j': FOOD, 'h': WEAPON, 'e': SCROLL, 'k':POTION}
    MONSTERS_DICT = dict(zip(MONSTERS, (Zombie, Vampire, Ghost, Ogre , Snake)))

    def __init__(self, data, statistics=None):
        data = data.data
        if statistics or data.get('statistics'):
            statistics = statistics or data.get('statistics')
            self._statistics = {k: v for k, v in statistics.items()}
            self._statistics["monsters_killed"] = 0
        else:
            self._statistics = {k: 0 for k in STATISTICS}
            self._statistics['level_reached'] = 1

        self.passed = False
        self._gamestate = NORMAL
        self._nav = Navigator(self)
        self._visible = set()
        self._matrix = None
        self._layout = {}
        self._monsters = {}
        self._items = {}
        self._rooms = [Room(r) for r in data['rooms']]
        self._corridors = [Corridor(c) for c in data['corridors']]
        self._player = Player(data.get('player'), self._nav)
        self._create_matrix()
        self._create_layout()

        self._explored = {tuple(i) for i in data.get('explored', set())}
        self._monsters_from_dict(data['monsters'])
        self._items_from_dict(data['items'])
        
        if data.get('visited'):
            self._visited = [i for i in data['visited']]
        else:
            self._visited = [0] * ROOMS
        
    def _monsters_from_dict(self, data:list):
        for m in data:
            monster = self.MONSTERS_DICT.get(m['id'], Mimic)()
            monster.set_features(m, self._nav)
            self._monsters[monster.pos] = monster

    def _items_from_dict(self, data:list):
        for d in data:
            item = Item(d)
            self._items[item.pos] = item
      
    def _move_player(self, char):
        new_y, new_x = self._player.pos
        if char == 'w':
            new_y -= 1
        elif char == 'a':
            new_x -= 1
        elif char == 's':
            new_y += 1
        elif char == 'd':
            new_x += 1
        pos = (new_y, new_x)
        if pos in self._monsters:
            monster = self._monsters[pos]
            if isinstance(monster, Mimic):
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
                    self._statistics["cells_moved"] += 1
        elif pos in self._matrix:
            self._player.pos = pos
            self._statistics["cells_moved"] += 1

    def _create_matrix(self):
        self._matrix = {pos: ROOMS + i for i, c in enumerate(self._corridors) for pos in c.walls}
        for i, r in enumerate(self._rooms):
            for floor in r.floor:
                self._matrix[floor] = i
        
    def _create_layout(self):
        for r in self._rooms:
            for y, x in r.vertical_walls:
                self._layout[(y, x)] = WALL_VER
            for y, x in r.horizontal_walls:
                self._layout[(y, x)] = WALL_HOR

            y, x = r.blc
            self._layout[(y, x)] = BLCR
            y, x = r.tlc
            self._layout[(y, x)] = TLCR
            y, x = r.brc
            self._layout[(y, x)] = BRCR
            y, x = r.trc
            self._layout[(y, x)] = TRCR
        self._place_corridors()

    def _place_corridors(self):
        for corridor in self._corridors:
            for (y, x) in corridor.walls:
                if (y - 1, x) in corridor.walls:
                    if (y + 1, x) in corridor.walls:
                        if (y, x + 1) in corridor.walls: 
                            if (y, x - 1) in corridor.walls: 
                                self._layout[(y, x)] = '╋' #1
                            else:
                                self._layout[(y, x)] = '┣'#2
                        elif (y, x - 1)  in corridor.walls: 
                            self._layout[(y, x)] = '┫'
                        else:
                            self._layout[(y, x)] = '┃'
                    else:
                        if (y, x + 1) in corridor.walls: 
                            if (y, x - 1) in corridor.walls: 
                                self._layout[(y, x)] = '┻'
                            else:
                                self._layout[(y, x)] = '┗'
                        elif (y, x - 1) in corridor.walls: 
                            self._layout[(y, x)] = '┛'
                        else:
                            self._layout[(y, x)] = '┃'
                elif (y + 1, x) in corridor.walls:
                        if (y, x + 1) in corridor.walls: 
                            if (y, x - 1) in corridor.walls: 
                                self._layout[(y, x)] = '┳'
                            else:
                                self._layout[(y, x)] = '┏'
                        elif (y, x - 1) in corridor.walls: 
                            self._layout[(y, x)] = '┓'
                        else:
                            self._layout[(y, x)] = '┃'
                else:
                    self._layout[(y, x)] = '━'

    def _handle_monsters(self):
        for m in list(self._monsters.values()):
            old_pos = m.pos
            m.move(self._player)
            if m.pos != old_pos:
                self._monsters[m.pos] = m
                del self._monsters[old_pos]
        # self._monsters = {m.pos: m for m in self._monsters.values()}
        self._player.update()

    def _update_visible(self, visible):
        y, x = self._player.pos
        for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            pos = (y + dy, x + dx)
            value = self._matrix.get(pos)
            while value is not None:
                visible.add(pos)
                if value >= ROOMS:
                    self._explored.add(pos)
                pos = (pos[0] + dy, pos[1] + dx)
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
                res[pos] = self._items[pos].id

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
        res = []
        for d in self._player.backpack.have.get(self.gamestate):
            d = sorted(d.to_dict().items(), key=lambda x: len(x[0]), reverse=True)
            d = ', '.join(f'{k}: {v}' for k, v in d if k != 'id' and k != 'pos')
            res.append(d)
        return res
    
    def room_number(self, pos):
        return self._matrix.get(pos)

    # - Оружие при смене должно падать на пол на соседнюю клетку. Если свободных нет = уничтожаем.
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

    def update(self, char):
        self._danger = []
        if self._gamestate == NORMAL:
            if char in 'wasd':
                self._move_player(char)
                self._handle_monsters()
            elif char in 'hjke':
                self._gamestate = self.BACKPACK_SHOW_MENU[char]
        else:
            if self._player.use_backpack(self._gamestate, char):
                self._handle_monsters()
            self._gamestate = NORMAL
        if self._player.health <= 0:
            self._gamestate = GAMEOVER

        # with open('player.txt', 'w') as f:
        #     f.write(f'bp\n{self._player.__dict__}\n')
        #     f.write(f'pl\n{self._player.to_dict()}\n')


    def data_for_saving(self):
        data = {}
        data['player'] = self._player.to_dict()
        data['monsters'] = [m.to_dict() for m in self._monsters.values()]
        data['items'] = [item.to_dict() for item in self._items.values()]
        data['statistics'] = self._statistics
        data['visited'] = self._visited
        data['explored'] = [i for i in self._explored]
        data['rooms'] = [r.to_dict() for r in self._rooms ]
        data['corridors'] = [r.to_dict() for r in self._corridors ]
        return data

        # with open('log.txt', 'w') as f:
        #     f.write(f'items\n{self._items}\n')
        #     f.write(f'monsters\n{self._monsters}')
        #     f.write(f'visible\n{self._visible}\n')
        #     f.write(f'visited\n{self._visited}\n')
        #     f.write(f'explored\n{self._explored}\n')
        #     f.write(f'backpack\n{self._player.backpack}\n')