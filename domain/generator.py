from random import randint, choice
import traceback
from common.constants import *
from common.playground import *
from common.characters import MONSTERS, ITEMS, WEAPON, KEY
from .dungeon import Room, Corridor
from .monsters import Zombie, Snake, Ogre, Vampire, Ghost, Mimic
from .entity import Item
from .player import Player


class Generator:
    MONSTERS_DICT = dict(zip(MONSTERS, (Zombie, Vampire, Ghost, Ogre , Snake)))

    def __init__(self, ad=None, player=None):
        data = ad.data if ad else {}
        self._k_monsters_quantity = data.get('K_monster_quantity') or 1
        self._k_monster_strength = data.get('K_monster_strength') or 1
        self._k_items_quantity = data.get('K_items_quantity') or 1
        self._k_items_power = data.get('K_items_power') or 1
        self._level = data.get('level_reached') or 1
        self._matrix = None
        self._corridors = None
        self._rooms = None
        self._player = player
        success = False
        exceptions = []
        while not success:
            try:
                # border is not valid for rooms:
                self._matrix = set((0, j) for j in range(WIDTH)) 
                self._matrix.update(set((i, 0) for i in range(HEIGHT)))

                self._rooms = [Room((i, *r)) for i, r in enumerate(self._generate_rooms())]

                # no corridors yet:
                edges = self._connect_rooms()
                success = self._create_corridors(edges)
                self._update_corridors()
                self._create_matrix()

                self._start, _ = self._most_distant_points()
                self._end, self._path = self._most_distant_points(self._start)
                start = self._matrix[self._start]

                adj = self._create_adj()
                d = {0:self._choose_rooms_for_keys_dfs, 
                     1:self._choose_rooms_for_keys_bfs}
                keys = self._closed_rooms(d[randint(0, 1)](adj))
                with open('layout.txt', 'w') as f:
                    f.write(f'{adj}\n')
                    f.write(f'{keys}\n')
                
                self._player = player  
                self._items = set()
                self._place_player_and_exit()
                self._place_keys(keys)
                self._place_monsters(start)
                self._place_items(start)

            except Exception as e:
                with open('error_log.txt', 'a') as f:
                    traceback.print_exc(file=f)
                exceptions.append(e)
                success = False
            if len(exceptions) > 2:
                raise AttributeError(exceptions)
        # with open('layout.txt', 'a') as f:
        #     f.write(f'{self.__repr__()}\n')
        #     f.write('rooms\n')
        #     for r in self._rooms:
        #         f.write(f'{r}\n')
        #     f.write(f'corridors\n')
        #     for c in self._corridors:
        #         f.write(f'{c}\n')
        

    def _most_distant_points(self, pos=None):
        visited = set()
        if not pos:
            pos = next(iter(self._matrix))
        visited.add(pos)
        max_dist = 0
        max_pos = 0
        s = [(pos, 0)]
        while s:
            new_s = []
            for pos, distance in s:
                if distance > max_dist:
                    max_dist = distance
                    max_pos = pos
                for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    new_pos = (pos[0] + dy, pos[1] + dx)
                    if new_pos in self._matrix and new_pos not in visited:
                        new_s.append((new_pos, distance + 1))
                        visited.add(new_pos)
            s = new_s
        return max_pos, max_dist

    def _choose_rooms_for_keys_dfs(self, adj):
        start = self._matrix[self._start]
        keys = {start: None}
        opened_rooms = {start,}
        s = [start]
        randmax = 1
        while s:
            room = s.pop()
            available_rooms = adj[room]
            for r in available_rooms:
                if r not in opened_rooms:
                    if randint(0, randmax):
                        k = choice(list(opened_rooms))
                        keys[r] = k
                        randmax = 2
                    else:
                        keys[r] = None
                    opened_rooms.add(r)
                    s.append(r)
        return keys

    def _choose_rooms_for_keys_bfs(self, adj):
        start = self._matrix[self._start]
        keys = {start: None}
        opened_rooms = {start,}
        s = [start]
        while s:
            for room in s:
                new_s = []
                available_rooms = adj[room]
                for r in available_rooms:
                    if r not in opened_rooms:
                        if randint(0, 2) < 2:
                            k = choice(list(opened_rooms))
                            keys[r] = k
                        else:
                            keys[r] = None
                        opened_rooms.add(r)
                        new_s.append(r)
            s = new_s
        return keys

    def _closed_rooms(self, rooms_with_keys):
        keys = {}
        for r, r_to_place in rooms_with_keys.items():
            if r_to_place is not None:
                keys.setdefault(r_to_place, []).append(r)
        return keys

    def _create_adj(self):
        adj = {}
        for c in self._corridors:
            c = c.connecting
            for r in c:
                adj.setdefault(r, set()).update(c)
        for k, v in adj.items():
            v.remove(k)
        return adj


    def _update_corridors(self):
        indexes = set()
        for i in range(len(self._corridors)):
            if i not in indexes:
                ci = self._corridors[i]
                for j in range(i + 1, len(self._corridors)):
                    if j not in indexes:
                        cj = self._corridors[j]
                        if ci.walls & cj.walls:
                            ci.add_connection(cj.connecting)
                            ci.add_walls(cj.walls)
                            indexes.add(j)
        self._corridors = [c for i, c in enumerate(self._corridors) if i not in indexes]


    def _generate_rooms(self) -> list:
        rooms = []
        for r in range(1, ROOMS + 1):
            created = False
            while not created:
                y, x = randint(0, HEIGHT), randint(0, WIDTH)
                h = randint(MIN_ROOM_HEIGHT, MAX_ROOM_HEIGHT)
                w = randint(MIN_ROOM_WIDTH, MAX_ROOM_WIDTH)
                if y + h < HEIGHT and x + w < WIDTH:
                    created = True
                    i = 0
                    while i < h and created:
                        j = 0
                        while j < w and created:
                            if (y + i, x + j) in self._matrix:
                                created = False
                            j += 1
                        i += 1
                    if created:
                        for i in range(h):
                            for j in range(w):
                                self._matrix.add((y + i, x + j))
                        rooms.append((y + OFFSET // 2, x + OFFSET // 2, h - OFFSET, w - OFFSET))

        return rooms       
    

    def _connect_rooms(self):
        graph = []
        for i in range(ROOMS):
            y1, x1 = self._rooms[i].center
            for j in range(i + 1, ROOMS):
                y2, x2 = self._rooms[j].center
                graph.append((abs(y1 - y2) + abs(x1 - x2), i, j))
        
        graph.sort()

        edges = []
        vertex = [{i,} for i in range(ROOMS)]
        graph = iter(graph)
        bst = False
        while not bst:
            _, i, j = next(graph)
            if j not in vertex[i]:
                vertex[i].update(vertex[j])
                if len(vertex[i]) == ROOMS:
                    bst = True
                else:
                    for v in vertex[i]:
                        vertex[v] = vertex[i]
                edges.append((i, j))

        return edges
    
    def _bottom_left_corner_connection_(self, r1:Room, r2:Room): # └ connection
        x = y = -1
        top_y = max(r2.y + 1, r1.y + r1.h)
        right_x = min(r1.x + r1.w - 2, r2.x - 1)
        i = top_y
        while i < r2.y + r2.h - 1:
            if (i, r2.x) in r2.gate:
                y = i
                i = HEIGHT
            i += 1
        j = right_x
        while j > r1.x:
            if (r1.y + r1.h - 1, j) in r1.gate:
                x = j
                j = 0
            j -= 1
        if y == -1:
            y = randint(top_y, r2.y + r2.h - 2)
        if x == -1:
            x = randint(r1.x + 1, right_x)
        i = top_y
        while i <= y:
            j = r2.x - 1
            while j > r2.x:
                if (i, j) in self._matrix:
                    if i > top_y:
                        y = i - 1
                    i = HEIGHT
                    j = 0
                j -= 1 
            i += 1
        j = r2.x - 1
        while j >= x:
            i = r1.y + r1.h
            while i <= y:
                if (i, j) in self._matrix:
                    if j < r2.x - 1:
                        x = j + 1
                    j = 0
                    i = HEIGHT
                i += 1
            j -= 1    
        r1.make_gate(r1.y + r1.h - 1, x)
        r2.make_gate(y, r2.x)
        c = Corridor((r1.y + r1.h - 1, x, y, x, r1.id, r2.id))
        c.add_path(y, x, y, r2.x)
        self._corridors.append(c)


    def _top_right_corner_connection_(self, r1:Room, r2:Room): # ┐ connection
        x = y = -1
        left_x = max(r1.x + r1.w, r2.x + 1)
        bottom_y = min(r1.y + r1.h - 2, r2.y - 1)
        i = bottom_y
        while i > r1.y:
            if (i, r1.x + r1.w - 1) in r1.gate:
                y = i
                i = 0
            i -= 1
        j = left_x
        while j < r2.x + r2.w - 1:
            if (r2.y, j) in r2.gate:
                x = j
                j = 101
            j += 1
        if y == -1:
            y = randint(r1.y + 1, bottom_y)
        if x == -1:
            x = randint(left_x, r2.x + r2.w - 2)

        i = bottom_y
        while i >= y:
            j = left_x
            while j <= x:
                if (i, j) in self._matrix:
                    if i < bottom_y:
                        y = i + 1
                    i = 0
                    j = WIDTH
                j += 1
            i -= 1
        j = left_x
        while j <= x:
            i = bottom_y
            while i >= y:
                if (i, j) in self._matrix:
                    if j > left_x:
                        x = j - 1
                    i = 0
                    j = WIDTH
                i -= 1
            j += 1
        r1.make_gate(y, r1.x + r1.w - 1)
        r2.make_gate(r2.y, x)
        c = Corridor((y, r1.x + r1.w - 1, y, x, r1.id, r2.id))
        c.add_path(y, x, r2.y, x)
        self._corridors.append(c)
      

    def _bottom_right_corner_connection_(self, r1:Room, r2:Room): # ┘-connection
        x = y = -1
        left_x = max(r1.x + 1, r2.x + r2.w)
        top_y = max(r1.y + r1.h, r2.y + 1)
    
        i = top_y
        while i < r2.y + r2.h - 1:
            if (i, r2.x + r2.w -1) in r2.gate:
                y = i
                i = 101
            i += 1
        j = left_x
        while j < r1.x + r1.w - 1:
            if (r1.y + r1.h - 1, j) in r1.gate:
                x = j
                j = 101
            j += 1
        if y == -1:
            y = randint(top_y, r2.y + r2.h - 2)
        if x == -1:
            x = randint(left_x, r1.x + r1.w - 2)
        i = top_y
        while i <= y:
            j = r2.x + r2.w
            while j <= x:
                if (i, j) in self._matrix:
                    if i > top_y:
                        y = i - 1
                    i = HEIGHT
                    j = WIDTH
                j += 1
            i += 1
        j = left_x
        while j <= x:
            i = top_y
            while i <= y:
                if (i, j) in self._matrix:
                    if j > left_x:
                        x = j - 1
                    j = WIDTH
                    i = HEIGHT
                i += 1
            j += 1
        r1.make_gate(r1.y + r1.h - 1, x)
        r2.make_gate(y, r2.x + r2.w - 1)
        c = Corridor((y, r2.x + r2.w - 1, y, x, r1.id, r2.id))
        c.add_path(r1.y + r1.h - 1, x, y, x)
        self._corridors.append(c)
 
    def _top_left_corner_connection_(self, r1:Room, r2:Room): # ┌-connection
        x = y = -1
        bottom_y = min(r1.y + r1.h - 2, r2.y - 1)
        right_x = min(r2.x + r2.w - 2, r1.x - 1)
        i = bottom_y
        while i > r1.y:
            if (i, r1.x) in r1.gate:
                y = i
                i = 0
            i -= 1
        j = right_x
        while j > r2.x:
            if (r2.y, j) in r2.gate:
                x = j
                j = 0
            j -= 1
        if x == -1:
            x = randint(r2.x + 1, right_x)
        if y == -1:
            y = randint(r1.y + 1, bottom_y)
        i = r2.y - 1
        while i >= y:
            j = x
            while j < r1.x:
                if (i, j) in self._matrix:
                    if i < bottom_y - 1:
                        y = i + 1
                    i = 0
                    j = WIDTH
                j += 1
            i -= 1
        j = r1.x - 1
        while j >= x:
            i = r2.y - 1
            while i >= y:
                if (i, j) in self._matrix:
                    if j < r1.x - 1:
                        x = j + 1
                    j = 0
                    i = 0
                i -= 1
            j -= 1
        r1.make_gate(y, r1.x)
        r2.make_gate(r2.y, x)
        c = Corridor((y, x, y, r1.x, r1.id, r2.id))
        c.add_path(y, x, r2.y, x)
        self._corridors.append(c) 

    def _create_corridors(self, edges:list[Room]):
        self._corridors = []
        for e in range(len(edges)):
            v1, v2 = edges[e]
            r1 = self._rooms[v1]
            r2 = self._rooms[v2]
            hor = [(r1.x + 1, 1), (r1.x + r1.w - 1, -1), (r2.x + 1, 1), (r2.x + r2.w - 1, -1)]
            ver = [(r1.y + 1, 1), (r1.y + r1.h - 1, -1), (r2.y + 1, 1), (r2.y + r2.h - 1, -1)]
            hor.sort()
            ver.sort()
            s = (hor[0][1] + hor[1][1] - hor[2][1] - hor[3][1], ver[0][1] + ver[1][1] - ver[2][1] - ver[3][1])
            edges[e] = (v1, v2, hor, ver, s)
        edges.sort(key = lambda x: x[4], reverse = True)
        for e in edges:
            v1, v2, hor, ver, _ = e
            r1 = self._rooms[v1]
            r2 = self._rooms[v2]
            if hor[0][1] + hor[1][1]:
                if r1.y > r2.y:
                    r1, r2 = r2, r1
                x_min = hor[1][0]
                x_max = hor[2][0]  - 1
                for i in range(ver[1][0] + 2, ver[2][0] - 1):
                    l = x_min
                    r = x_max
                    while (l < r):
                        if (i, l) in self._matrix:
                            x_min = l + 1
                        if (i, r) in self._matrix:
                            x_max = r - 1
                        l += 1
                        r -= 1
                x = randint(x_min, x_max)
                r1.make_gate(r1.y + r1.h - 1, x)
                r2.make_gate(r2.y, x)
                c = Corridor((r1.y + r1.h - 1, x, r2.y, x, r1.id, r2.id))
                self._corridors.append(c)
                

            elif ver[0][1] + ver[1][1]:
                    if r1.x > r2.x:
                        r1, r2 = r2, r1
                    y_min = ver[1][0]
                    y_max = ver[2][0] - 1
                    for i in range(hor[1][0] + 1, hor[2][0] - 2):
                        t = y_min
                        b = y_max
                        while(t < b):
                            if (t, i) in self._matrix:
                                y_min = t + 1
                            if (b, i) in self._matrix:
                                y_max = b - 1
                            t += 1
                            b -= 1
                    y = randint(y_min, y_max)
                    r1.make_gate(y, r1.x + r1.w - 1)
                    r2.make_gate(y, r2.x)
                    c = Corridor((y, r1.x + r1.w - 1, y, r2.x, r1.id, r2.id))
                    self._corridors.append(c)

            else:
                if r1.y > r2.y:
                    r1, r2 = r2, r1
                if r1.x < r2.x:
                    if randint(0, 1): # └ connection
                        self._bottom_left_corner_connection_(r1, r2)
                    else: # ┐-connection
                        self._top_right_corner_connection_(r1, r2)
                else: 
                    if randint(0, 1):# ┘-connection
                        self._bottom_right_corner_connection_(r1, r2)
                    else: # ┌-connection
                        self._top_left_corner_connection_(r1, r2)
        return True

    def __repr__(self):
        from .layout import Layout
        l = Layout().create_layout(self._rooms, self._corridors, with_rooms=False)
        l[self._player.pos] = '@'
        l[self._end] = '█'
        for i in self._items:
            if i.id == KEY:
                l[i.pos] = i.color + i.id + '\033[0m'
                l[i.door.pos] = i.color + 'x' + '\033[0m'
                # l[i.pos] = i.id
                # l[i.door.pos] = 'x'
            else:
                l[i.pos] = i.id
        for m in self._monsters:
            l[m.pos] = str(m)
        layout = '\n'.join(f"{i:02}{''.join(l.get((i, j), ' ') for j in range(WIDTH))}"  for i in range(HEIGHT))
        s1 = '  ' + ''.join(str(i) + ' ' * 9 for i in range(10)) + '\n'
        s2 = '  ' + ''.join(str(i) for i in range(10)) * 10 + '\n'

        return s1 + s2 + layout

    def _create_matrix(self):
        self._matrix = {pos: r.id for r in self._rooms for pos in r.floor}
        for i, c in enumerate(self._corridors, ROOMS):
            for pos in c.walls:
                self._matrix[pos] = i


    def _place_keys(self, keys):
        # return
        key_positions = set()
        for room_with_keys, closed_rooms in keys.items():
            for room in closed_rooms:
                pos = self._get_pos(room_with_keys)
                self._matrix[pos] = room
                while pos in key_positions:
                    pos = self._get_pos(room_with_keys)
                    self._matrix[pos] = room
                key_positions.add(pos)
                lock_pos = self._find_door_to_close(pos, room)
                lock_id = self._matrix[lock_pos]
                self._items.add(Item((KEY, pos, (lock_id, lock_pos))))
        for key_pos in key_positions:
            del self._matrix[key_pos]


    def _find_door_to_close(self, pos, room):
        gates = self._rooms[room].gate
        s = [pos]
        visited = set()
        while s:
            new_s = []
            for pos in s:
                for dy, dx in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    new_pos = (pos[0] + dy, pos[1] + dx)
                    if new_pos in gates:
                        return new_pos
                    if new_pos in self._matrix and not new_pos in visited:
                        new_s.append(new_pos)
                        visited.add(new_pos)
            s = new_s

    def _place_player_and_exit(self):
        if self._player is None:
            self._player = Player()
        self._player.pos = self._start
        self._player.backpack.have[KEY] = []
        
        it = Item((EXIT, self._end, 1))
        self._items.add(it)
        del self._matrix[self._start]
        del self._matrix[self._end]

    def _place_items(self, start):
        # return
        rooms_idx = [i for i in range(ROOMS) if i != start]
        items = dict(zip(ITEMS, 
            (
                max(round(5 * (self._k_items_quantity)), 1),      # food
                max(round(3 * (self._k_items_quantity)), 1),      # potion
                max(round(2 * (self._k_items_quantity)), 1)      # scroll
            )))

        for item, quantity in items.items():
                for _ in range(quantity):
                    pos = self._get_pos(choice(rooms_idx))
                    it = Item((item, pos, self._k_items_power))
                    self._items.add(it)
                
        for _ in range(max(1, round(1 + self._level // 3))):      # weapon
            pos = self._get_pos(choice(rooms_idx))
            it = Item((WEAPON, pos, self._k_monster_strength))
            self._items.add(it)

    def _get_pos(self, r):
        valid_pos = list(self._rooms[r].floor)
        pos = choice(valid_pos)
        while pos not in self._matrix:
            pos = choice(valid_pos)
        del self._matrix[pos]
        return pos
        
    def _place_monsters(self, start):
        self._monsters = set()
        # return
        rooms = {start,}
        quantity = round(randint(3, 5) * self._k_monsters_quantity)
        monsters = list(MONSTERS)[:quantity]
        if quantity > len(monsters):
            for i in range(quantity - len(monsters)):
                monsters.append(choice(monsters))

        for m in monsters:
            r = randint(0, ROOMS - 1)
            while r in rooms:
                r = randint(0, ROOMS - 1)
            rooms.add(r)
            if len(rooms) == ROOMS:
                rooms = {start,}
            pos = self._get_pos(r)
            monster = self.MONSTERS_DICT[m](pos, r)
            monster.set_init_values(self._k_monster_strength)
            self._monsters.add(monster)

        if randint(0, 1):
            rooms = {start,}
            r = randint(0, ROOMS - 1)
            while r in rooms:
                r = randint(0, ROOMS - 1)
            pos = self._get_pos(r)
            monster = Mimic(pos, r)
            monster.set_init_values(self._k_monster_strength)
            self._monsters.add(monster)


    @property
    def data(self):
        data = {}
        data['player'] = self._player.to_dict()
        data['monsters'] = [m.to_dict() for m in self._monsters]
        data['items'] = [item.to_dict() for item in self._items]
        data['rooms'] = [r.to_dict() for r in self._rooms ]
        data['corridors'] = [r.to_dict() for r in self._corridors ]
        data['path_length'] = self._path 
        return data


if __name__ == '__main__':

    print(Generator())




