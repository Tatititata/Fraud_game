from common.constants import *
from common.characters import *
from common.playground import *
from .entity import Entity, Player, Item
from random import randint, choice
from .navigator import Navigator
from .monsters import Zombie, Snake, Ogre, Vampire, Ghost, Monster
from .dungeon import Room, Corridor
import sys


class Model:

    BACKPACK_SHOW_MENU = {'j': FOOD, 'h': WEAPON, 'e': SCROLL, 'k':POTION}
    MONSTERS_DICT = dict(zip(MONSTERS, (Zombie, Vampire, Ghost, Ogre , Snake)))

    def __init__(self, data, statistics=None):
        with open('log.txt', 'w') as f:
           f.write(f'model init \n{data}\n')
        data = data.data
        if statistics or data.get('statistics'):
            statistics = statistics or data.get('statistics')
            self._statistics = {k: v for k, v in statistics.items()}
        else:
            self._statistics = {k: 0 for k in STATISTICS}
            self._statistics['level_reached'] = 1

        self.passed = False
        self._gamestate = NORMAL
        self._nav = Navigator(self)
        self._visible = set()
        self._matrix = None
        self._layout = {}
        self._monsters = set()
        self._items = set()
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
            monster = self.MONSTERS_DICT[m['id']]()
            monster.set_features(m, self._nav)
            self._monsters.add(monster)
            self._matrix[monster.pos][1] = monster

    def _items_from_dict(self, data:list):
        for d in data:
            y, x, item_dict = d
            pos = (y, x)
            item = Item(item_dict)
            self._items.add(((pos), item))
            self._matrix[pos][1] = item        

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
        value = self._matrix.get(pos)
        if value is not None:
            value = value[1]
            if value is None:
                self._matrix[pos][1] = self._player
                self._matrix[self._player.pos][1] = None
                self._player.pos = pos
                self._statistics["cells_moved"] += 1 
            elif value.id == EXIT:
                self.passed = True
                self._statistics['level_reached'] += 1
            elif isinstance(value, Monster):
                self._player.attack(value)
                if value.health <= 0:
                    self._monsters.discard(value)
                    self._matrix[value.pos][1] = None
                    self._statistics["monsters_killed"] += 1
                    self._statistics["treasure"] += value.drop_treasure()
            else:
                if self._player.get_item(value):
                    self._matrix[pos][1] = self._player
                    self._matrix[self._player.pos][1] = None
                    self._player.pos = pos
                    value = (pos, value)
                    self._items.discard(value)

    def _create_matrix(self):
        self._matrix = {pos: [ROOMS + i, None] for i, c in enumerate(self._corridors) for pos in c.walls}
        for i, r in enumerate(self._rooms):
            for floor in r.floor:
                self._matrix[floor] = [i, None]
        self._matrix[self._player.pos][1] = self._player
        
    def _create_layout(self):
        for r in self._rooms:
            # for y, x in r.floor:
            #     layout[(y, x)] = FLOOR
                # layout[(y, x)] = str(r.id)
            for y, x in r.left_wall:
                self._layout[(y, x)] = WALL_VER
            for y, x in r.right_wall:
                self._layout[(y, x)] = WALL_VER
            for y, x in r.top_wall:
                self._layout[(y, x)] = WALL_HOR
            for y, x in r.bottom_wall:
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

    def _handle_enemies(self):
        for e in self._monsters:
            e.move(self._player)
        self._player.update()

    def _update_visible(self, visible):
        y, x = self._player.pos
        for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            pos = (y + dy, x + dx)
            value = self._matrix.get(pos)
            while value:
                visible.add(pos)
                if value[0] >= ROOMS:
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
        idx = self._matrix[self._player.pos][0] #the room player in
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

        for m in self._monsters:
            if m.pos in visible:
                res[m.pos] = m.id

        for pos, i in self._items:
            if pos in visible:
                res[pos] = i.id

        res[self._player.pos] = self._player.id
        # with open('log.txt', 'w') as f:
        #         f.write(f'rooms\n{self._rooms}\n')
        #         f.write(f'corrs\n{self._corridors}\n')
        #         f.write(f'items\n{self._items}\n')
        #         f.write(f'monsters\n{self._monsters}\n')
        #         # f.write(f'visible\n{self._visible}\n')
        #         f.write(f'visited\n{self._visited}\n')
        #         f.write(f'explored\n{self._explored}\n')
        #         f.write(f'backpack\n{self._player.backpack}\n')
        return res

    def place_entity(self, pos, e:Entity):
        if self.walkable(pos):
            self._matrix[(e.pos)][1] = None
            e.pos = pos
            self._matrix[pos][1] = e

    def walkable(self, pos):
        value = self._matrix.get(pos)
        return value is not None and value[1] is None
    
    def valid(self, pos):
        return pos in self._matrix

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
            # with open('log.txt', 'a') as f:
            #     f.write(f'{d.__class__.__name__}\n')
            #     f.write(f'{d}\n')
            d = sorted(d.to_dict().items(), key=lambda x: len(x[0]), reverse=True)
            d = ', '.join(f'{k}: {v}' for k, v in d if k != 'id')
            res.append(d)
        return res
    
    def room_number(self, pos):
        value = self._matrix.get(pos)
        if value is not None:
            return value[0] 
        return None

    # - Оружие при смене должно падать на пол на соседнюю клетку. Если свободных нет = уничтожаем.
    def place_weapon(self, pos, weapon):
        for y, x in ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            new_pos = (pos[0] + y, pos[1] + x)
            if self.walkable(new_pos):
                self._matrix[new_pos][1] = weapon
                self._items.add((new_pos, weapon))
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
        d.update(self._player.backpack.to_dict())
        d['max_health'] = self._player.max_health
        return d

    def add_statistics(self, key:str, value:int=1):
        self._statistics[key] += value

    def update(self, char):
        self._danger = []
        if self._gamestate == NORMAL:
            if char in 'wasd':
                self._move_player(char)
                self._handle_enemies()
            elif char in 'hjke':
                self._gamestate = self.BACKPACK_SHOW_MENU[char]
        else:
            if self._player.use_backpack(self._gamestate, char):
                self._handle_enemies()
            self._gamestate = NORMAL
        if self._player.health <= 0:
            self._gamestate = GAMEOVER

        # with open('player.txt', 'w') as f:
        #     f.write(f'bp\n{self._player.__dict__}\n')
        #     f.write(f'pl\n{self._player.to_dict()}\n')


    def data_for_saving(self):
        data = {}
        data['player'] = self._player.to_dict()
        data['monsters'] = [r.to_dict() for r in self._monsters]
        data['items'] = [[*pos, r.to_dict() ] for pos, r in self._items]
        data['statistics'] = self._statistics
        data['visited'] = self._visited
        data['explored'] = [i for i in self._explored]
        data['rooms'] = [r.to_dict() for r in self._rooms ]
        data['corridors'] = [r.to_dict() for r in self._corridors ]
        return data



    # def _place_player(self, start):
    #     self._player.pos = self._get_pos(start)
    #     self._matrix[self._player.pos][1] = self._player
    #     self._player._nav = self._nav
    #     # with open('log.txt', 'w') as f:
    #     #     f.write(f"{self._player.pos}\n")
    #     #     for key, value in sorted(self._matrix.items()):
    #     #         f.write(f"{key}: {value}\n")

    # def _get_pos(self, r):
    #     pos = choice(list(self._rooms[r].floor))
    #     while self._matrix[pos][1] is not None:
    #         pos = choice(list(self._rooms[r].floor))
    #     return pos
    
    # def _place_items(self, end):
    #     items = dict(zip(ITEMS, 
    #       (
    #           max(5 - self.level, 1),           #food
    #           max(3 - self.level // 2, 1),      #potion
    #           max(2 - self.level // 3, 1),      #scroll
    #           1 + self.level // 5               #weapon
    #           )))
        
    #     positions = list(self._matrix)
    #     for item, quantity in items.items():
    #         for _ in range(quantity):
    #             pos = choice(positions)
    #             while self._matrix[pos][1] is not None:
    #                 pos = choice(positions)
    #             it = Item(item, self.level)
    #             self._matrix[pos][1] = it
    #             self._items.add((pos, it))
    #     positions = list(self._rooms[end].floor)
    #     pos = choice(positions)
    #     while self._matrix[pos][1] is not None:
    #         pos = choice(positions)
    #     it = Item(EXIT)
    #     self._matrix[pos][1] = it
    #     self._items.add((pos, it))
        
    # def _place_monsters(self, start):
    #     # return
    #     rooms = {start,}
    #     monsters = list(MONSTERS)[:2]
    #     for i in range(self.level - 1):
    #         monsters.append(choice(monsters))
    #     for m in monsters:
    #         r = randint(0, ROOMS - 1)
    #         while r in rooms:
    #             r = randint(0, ROOMS - 1)
    #         rooms.add(r)
    #         if len(rooms) == ROOMS:
    #             rooms = {start,}
    #         pos = self._get_pos(r)
    #         monster = self.MONSTERS_DICT[m](self._nav, pos, r, self.level)
    #         self._matrix[pos][1] = monster
    #         self._monsters.add(monster)


    # def _load_generated_game(self, data, player, statistics):

    #     self._rooms = data['rooms']
    #     self._corridors = data['corridors']
    #     self._visited = [0] * (ROOMS)
    #     self._matrix = data['matrix']
    #     # self._create_matrix()
    #     self._create_layout()
    #     self._player = player or Player()
    #     self._monsters = set()
    #     self._items = set()
    #     self._explored = set()
    #     self._place_monsters(data[2])
    #     self._place_items(data[3])
    #     self._place_player(data[2])
        

        # with open('log.txt', 'w') as f:
        #     f.write(f'items\n{self._items}\n')
        #     f.write(f'monsters\n{self._monsters}')
        #     f.write(f'visible\n{self._visible}\n')
        #     f.write(f'visited\n{self._visited}\n')
        #     f.write(f'explored\n{self._explored}\n')
        #     f.write(f'backpack\n{self._player.backpack}\n')