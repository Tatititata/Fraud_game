from random import randint, choice
import traceback
import sys
from common.constants import *
from .entity import Player

class Room:
    def __init__(self, y, x, height, width):
        # y, x = up left corner
        self.y = y
        self.x = x
        self.h = height
        self.w = width
        self.center = (y + height // 2, x + width // 2)
        self.floor = set((i, j) for i in range(y + 1, y + height - 1) for j in range(x + 1, x + width - 1))
        self.walls = set((y, j) for j in range(x, x + width)) | \
            set((y + height - 1, j) for j in range(x, x + width)) | \
            set((i, x) for i in range(y, y + height)) | \
            set((i, x + width - 1) for i in range(y, y + height))
        self.gate = set()
        
    def __repr__(self):
        # return 'Walls' + repr(self.walls) + '\n' + 'Floor' + repr(self.floor)

        # matrix = [[GROUND] * WIDTH for _ in range(HEIGHT)]
        # for i, j in self.floor:
        #     matrix[i][j] = '.'
        # for i, j in self.walls:
        #     matrix[i][j] = '#'
        # return '\n'.join(''.join(m) for m in matrix)

        return f"[y={self.y}, x={self.x}, h={self.h}, w={self.w}, gate={repr(self.gate)}]"
    
    def make_gate(self, y, x):
        
        self.gate.add((y, x))
        self.walls.discard((y, x))
    
class Corridor:
    def __init__(self, y1, x1, y2, x2):
        # y1 <= y2, x1 <= x2
        self.path = set((i, x1) for i in range(y1, y2 + 1)) | set((y2, j) for j in range(x1, x2 + 1))



class Level:
    def __init__(self, level:int=0) -> None:
        self.id = level
        self.width = WIDTH
        self.height = HEIGHT
        self.matrix = []
        self.corridors = []
        self.rooms = []
        sucsess = False
        while not sucsess:
            try:
                # self.rooms = [Room(*r) for r in self._generate_rooms()]
                self.rooms = [Room(*r) for r in self._generate_rooms_full_random()]
                self._place_rooms()
                
                sucsess = self._create_corridors(self._connect_rooms())
            except Exception as e:

                traceback.print_exc()
                sucsess = False

        self._place_corridors()
        self.entities = []

    def start_game(self):
        self.start_room, self.end_room = self.set_start_end_rooms()
        self.player = self.set_player()
        self._fix_rooms_and_corridors()

    def set_player(self):
        y, x = choice(list(self.start_room.floor))
        player = Player(y, x, PLAYER)
        # player.room = self.start_room
        self.entities.append(player)
        # sys.stdout.write('\r\n' + str(player.__dict__) + '\r\n')
        # sys.stdout.write('\r\n' + str(self.entities) + '\r\n')
        return player

    def set_start_end_rooms(self):
        r = sorted(self.rooms, key=lambda r: r.h * r.w)
        return r[0], r[-1]

    def _generate_rooms_full_random(self) -> list:
        rooms = []
        self.matrix = [[0] * WIDTH for _ in range(HEIGHT)]
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
                            if self.matrix[y + i][x + j]:
                                created = False
                            j += 1
                        i += 1
                    if created:
                        for i in range(h):
                            for j in range(w):
                                self.matrix[y + i][x + j] = r
                        rooms.append((y + 1, x + 1, h - OFFSET, w - OFFSET))
        # rooms = [(30, 3, 9, 8), (15, 56, 14, 8), (31, 33, 6, 8), (11, 1, 7, 10), (32, 13, 14, 8), 
        #          (32, 81, 10, 13), (17, 81, 6, 10), (35, 67, 14, 10), (9, 29, 13, 11)]
        
        print(f'rooms = {rooms}')
        return rooms       
    
    def _generate_rooms(self) -> list:
        rooms = []
        self.matrix = [[0] * WIDTH for _ in range(HEIGHT)]
        count = 0
        for ii in ((1, 16), (17, 32), (33, 48)):
            for jj in ((1, 33), (34, 66), (67, 99)):
                created = False
                while not created:
                    h = randint(MIN_ROOM_HEIGHT, MAX_ROOM_HEIGHT)
                    w = randint(MIN_ROOM_WIDTH, MAX_ROOM_WIDTH)
                    y = randint(ii[0], ii[1] - h)
                    x = randint(jj[0], jj[1] - w)
                    
                    if y + h < ii[1] and x + w < jj[1]:
                        created = True
                        i = 0
                        while i < h and created:
                            j = 0
                            while j < w and created:
                                if self.matrix[y + i][x + j]:
                                    created = False
                                    j = w
                                    i = h
                                j += 1
                            i += 1
                        if created:
                            for i in range(h):
                                for j in range(w):
                                    self.matrix[y + i][x + j] = count
                            rooms.append((y + 1, x + 1, h - OFFSET, w - OFFSET))
                            count += 1
        print(f'rooms = {rooms}')
        return rooms

    def _connect_rooms(self):
        graph = []
        for i in range(ROOMS):
            y1, x1 = self.rooms[i].center
            for j in range(i + 1, ROOMS):
                y2, x2 = self.rooms[j].center
                # graph.append((2 * abs(y1 - y2) + abs(x1 - x2), i, j))
                graph.append((abs(y1 - y2) + abs(x1 - x2), i, j))
        
        graph.sort()
        # print(*graph, sep='\n')
        # print(graph[0])
        edges = []
        vertex = [{i,} for i in range(ROOMS)]
        graph = iter(graph)
        bst = False
        while not bst:
            _, i, j = next(graph)
            if j not in vertex[i]:
                vertex[i] = vertex[j] | vertex[i]
                if len(vertex[i]) == ROOMS:
                    bst = True
                else:
                    for v in vertex[i]:
                        vertex[v] = vertex[i]
                edges.append((i, j))
        # print(f"edges={edges}")
        return edges
    
    def __repr__(self):
        # level = [''.join(l) for i, l in enumerate(self.matrix)]
        # return '\n'.join(level)
        level = [f"{i:02d}" + ''.join(l) for i, l in enumerate(self.matrix)]
        s1 = '  ' + ''.join(str(i) + ' ' * 9 for i in range(10)) + '\n'
        s2 = '  ' + '0123456789' * 10 + '\n'
        return s1 + s2 + '\n'.join(level)

    def _place_rooms(self):
        level = self.matrix = [[GROUND] * WIDTH for _ in range(HEIGHT)]
        for i in range(HEIGHT):
            level[i][0] = WALL_VER
            level[i][WIDTH - 1] = WALL_VER

        for i in range(WIDTH):
            level[0][i] = WALL_HOR
            level[HEIGHT - 1][i] = WALL_HOR

        level[0][0] = ULCR
        level[0][WIDTH - 1] = URCR
        level[HEIGHT - 1][0] = BLCR
        level[HEIGHT - 1][WIDTH - 1] = BRCR
        for r in range(len(self.rooms)):
            y, x = self.rooms[r].y, self.rooms[r].x
            h = self.rooms[r].h
            w = self.rooms[r].w
            # print(y, x, y + h , x + w)
            for j in range(x, x + w):
                level[y][j] = WALL_HOR
                level[y + h - 1][j] = WALL_HOR
            for i in range(y, y + h):
                level[i][x] = WALL_VER
                level[i][x + w - 1] = WALL_VER
            level[y][x] = ULCR
            level[y][x + w - 1] = URCR
            level[y + h - 1][x] = BLCR
            level[y + h - 1][x + w - 1] = BRCR

            for i in range(y + 1, y + h - 1):
                for j in range(x + 1, x + w - 1):
                    # level[i][j] = str(r)
                    level[i][j] = FLOOR                 

    def _bottom_left_corner_connection_(self, r1:Room, r2:Room): # └ connection
        x = y = -1
        top_y = max(r2.y + 1, r1.y + r1.h)
        right_x = min(r1.x + r1.w - 2, r2.x - 1)
        print(f'top_y = {top_y}, right_x = {right_x} L', end = ' ')
        i = top_y
        while i < r2.y + r2.h - 1:
            if self.matrix[i][r2.x] == DOOR_V:
                y = i
                i = HEIGHT
            i += 1
        j = right_x
        while j > r1.x:
            if self.matrix[r1.y + r1.h - 1][j] == DOOR_H:
                x = j
                j = 0
            j -= 1
        print(f'y = {y}, x = {x} L', end = ' ')
        if y == -1:
            y = randint(top_y, r2.y + r2.h - 2)
        if x == -1:
            x = randint(r1.x + 1, right_x)
        i = top_y
        while i <= y:
            j = r2.x - 1
            while j > r2.x:
                if self.matrix[i][j] in ROOM_WALLS:
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
                if self.matrix[i][j] in ROOM_WALLS:
                    if j < r.x - 1:
                        x = j + 1
                    j = 0
                    i = HEIGHT
                i += 1
            j -= 1    
        for j in range(x, r2.x + 1):
            self.matrix[y][j] = CORR_HOR
        for i in range(r1.y + r1.h - 1, y + 1):
            self.matrix[i][x] = CORR_VER
        self.matrix[y][r2.x] = DOOR_V
        self.matrix[r1.y + r1.h - 1][x] = DOOR_H
        r1.make_gate(r1.y + r1.h - 1, x)
        r2.make_gate(y, r2.x)
        self.corridors.append(Corridor(r1.y + r1.h, x, y, x))
        self.corridors.append(Corridor(y, x, y, r2.x - 1))
        print(f'y = {y}, x = {x} L')

    def _top_right_corner_connection_(self, r1:Room, r2:Room): # ┐ connection
        x = y = -1
        left_x = max(r1.x + r1.w, r2.x + 1)
        bottom_y = min(r1.y + r1.h - 2, r2.y - 1)
        print(f'bottom_y = {bottom_y}, left_x = {left_x}', end = ' ')
        i = bottom_y
        while i > r1.y:
            if self.matrix[i][r1.x + r1.w - 1] == DOOR_V:
                y = i
                i = 0
            i -= 1
        j = left_x
        while j < r2.x + r2.w - 1:
            if self.matrix[r2.y][j] == DOOR_H:
                x = j
                j = 101
            j += 1
        print(f'y = {y}, x = {x} ┐', end = ' ')
        if y == -1:
            y = randint(r1.y + 1, bottom_y)
        if x == -1:
            x = randint(left_x, r2.x + r2.w - 2)

        i = bottom_y
        while i >= y:
            j = left_x
            while j <= x:
                if self.matrix[i][j] in ROOM_WALLS:
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
                if self.matrix[i][j] in ROOM_WALLS:
                    if j > left_x:
                        x = j - 1
                    i = 0
                    j = WIDTH
                i -= 1
            j += 1

        for j in range(r1.x + r1.w - 1, x + 1):
            self.matrix[y][j] = CORR_HOR
        for i in range(y, r2.y + 1):
            self.matrix[i][x] = CORR_VER
        r1.make_gate(y, r1.x + r1.w - 1)
        r2.make_gate(r2.y, x)
        self.corridors.append(Corridor(y, r1.x + r1.w, y, x))
        self.corridors.append(Corridor(y, x, r2.y - 1, x))
        print(f'y = {y}, x = {x} ┐')

    def _bottom_right_corner_connection_(self, r1:Room, r2:Room): # ┘-connection
        x = y = -1
        left_x = max(r1.x + 1, r2.x + r2.w)
        top_y = max(r1.y + r1.h, r2.y + 1)
        print(f'top_y = {top_y}, left_x = {left_x} ┘', end = ' ')
        i = top_y
        while i < r2.y + r2.h - 1:
            if self.matrix[i][r2.x + r2.w -1] == DOOR_V:
                y = i
                i = 101
            i += 1
        j = left_x
        while j < r1.x + r1.w - 1:
            if self.matrix[r1.y + r1.h - 1][j] == DOOR_H:
                x = j
                j = 101
            j += 1
        print(f'y = {y}, x = {x} ┘', end = ' ')
        if y == -1:
            y = randint(top_y, r2.y + r2.h - 2)
        if x == -1:
            x = randint(left_x, r1.x + r1.w - 2)
        i = top_y
        while i <= y:
            j = r2.x + r2.w
            while j <= x:
                if self.matrix[i][j] in ROOM_WALLS:
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
                if self.matrix[i][j] in ROOM_WALLS:
                    if j > left_x:
                        x = j - 1
                    j = WIDTH
                    i = HEIGHT
                i += 1
            j += 1

        for j in range(r2.x + r2.w - 1, x + 1):
            self.matrix[y][j] = CORR_HOR
        for i in range(r1.y + r1.h - 1, y + 1):
            self.matrix[i][x] = CORR_VER
        self.matrix[r1.y + r1.h - 1][x] = DOOR_H
        self.matrix[y][r2.x + r2.w - 1] = DOOR_V
        r1.make_gate(r1.y + r1.h - 1, x)
        r2.make_gate(y, r2.x + r2.w - 1)
        self.corridors.append(Corridor(y, r2.x + r2.w, y, x))
        self.corridors.append(Corridor(r1.y + r1.h, x, y, x))
        print(f'y = {y}, x = {x} ┘') 

    def _top_left_corner_connection_(self, r1:Room, r2:Room): # ┌-connection
        x = y = -1
        bottom_y = min(r1.y + r1.h - 2, r2.y - 1)
        right_x = min(r2.x + r2.w - 2, r1.x - 1)
        i = bottom_y
        while i > r1.y:
            if self.matrix[i][r1.x] == DOOR_V:
                y = i
                i = 0
            i -= 1
        j = right_x
        while j > r2.x:
            if self.matrix[r2.y][j] == DOOR_H:
                x = j
                j = 0
            j -= 1
        if x == -1:
            x = randint(r2.x + 1, right_x)
        if y == -1:
            y = randint(r1.y + 1, bottom_y)
        print(f'y = {y}, bottom_y = {bottom_y}, r2.y = {r2.y}, x = {x}, r1.x = {r1.x}, right_x = {right_x}', end = ' ')
        i = r2.y - 1
        while i >= y:
            j = x
            while j < r1.x:
                if self.matrix[i][j] in ROOM_WALLS:
                    if i < r2.y - 1:
                        y = i + 1
                    i = 0
                    j = WIDTH
                j += 1
            i -= 1
        print(f'y = {y}, x = {x}, ')
        j = r1.x - 1
        while j >= x:
            i = r2.y - 1
            while i >= y:
                if self.matrix[i][j] in ROOM_WALLS:
                    if j < r1.x - 1:
                        x = j + 1
                    j = WIDTH
                    i = 0
                i -= 1
            j -= 1

        for j in range(x, r1.x + 1):
            self.matrix[y][j] = CORR_HOR
        for i in range(y, r2.y + 1):
            self.matrix[i][x] = CORR_VER
        self.matrix[y][r1.x] = DOOR_V
        self.matrix[r2.y][x] = DOOR_H
        r1.make_gate(y, r1.x)
        r2.make_gate(r2.y, x)
        self.corridors.append(Corridor(y, x, y, r1.x - 1))
        self.corridors.append(Corridor(y, x, r2.y - 1, x))
        print(f'y = {y}, x = {x} ┌')      

    def _create_corridors(self, edges:list[Room]):
        for e in range(len(edges)):
            v1, v2 = edges[e]
            r1 = self.rooms[v1]
            r2 = self.rooms[v2]
            hor = [(r1.x + 1, 1), (r1.x + r1.w - 1, -1), (r2.x + 1, 1), (r2.x + r2.w - 1, -1)]
            ver = [(r1.y + 1, 1), (r1.y + r1.h - 1, -1), (r2.y + 1, 1), (r2.y + r2.h - 1, -1)]
            hor.sort()
            ver.sort()
            s = (hor[0][1] + hor[1][1] - hor[2][1] - hor[3][1], ver[0][1] + ver[1][1] - ver[2][1] - ver[3][1])
            edges[e] = (v1, v2, hor, ver, s)
        edges.sort(key = lambda x: x[4], reverse = True)
        # print(*edges, sep='\n')
        for e in edges:
            v1, v2, hor, ver, _ = e
            r1 = self.rooms[v1]
            r2 = self.rooms[v2]
            print(v1, v2, end = ' ')
            print(hor, ver, end = ' ')
            if hor[0][1] + hor[1][1]:
                # top-bottom connection
                print('up and down', end = ' ')
                if r1.y > r2.y:
                    r1, r2 = r2, r1
                x_min = hor[1][0]
                x_max = hor[2][0] - 1    
                for i in range(ver[1][0] + 2, ver[2][0] - 1):
                    l = x_min
                    r = x_max
                    while (l < r):
                        if self.matrix[i][l] == WALL_HOR or self.matrix[i][l] == WALL_VER:
                            x_min = l + 1
                        if self.matrix[i][r] == WALL_HOR or self.matrix[i][r] == WALL_VER:
                            x_max = r - 1
                        l += 1
                        r -= 1
                x = randint(x_min, x_max)
                print(f'x = {x}')
                r1.make_gate(r1.y + r1.h - 1, x)
                r2.make_gate(r2.y, x)
                self.corridors.append(Corridor(r1.y + r1.h, x, r2.y - 1, x))
                for i in range(r1.y + r1.h - 1, r2.y + 1):
                    self.matrix[i][x] = CORR_VER
                self.matrix[r1.y + r1.h - 1][x] = DOOR_H
                self.matrix[r2.y][x] = DOOR_H


            elif ver[0][1] + ver[1][1]:
                    # left-right connection
                    print('left and right', end = ' ')
                    if r1.x > r2.x:
                        r1, r2 = r2, r1
                    y_min = ver[1][0]
                    y_max = ver[2][0] - 1
                    for i in range(hor[1][0] + 1, hor[2][0] - 2):
                        t = y_min
                        b = y_max
                        while(t < b):
                            if self.matrix[t][i] == WALL_HOR or self.matrix[t][i] == WALL_VER:
                                y_min = t + 1
                            if self.matrix[b][i] == WALL_HOR or self.matrix[b][i] == WALL_VER:
                                y_max = b - 1
                            t += 1
                            b -= 1
                    y = randint(y_min, y_max)
                    print(f'y = {y}')
                    r1.make_gate(y, r1.x + r1.w - 1)
                    r2.make_gate(y, r2.x)
                    self.corridors.append(Corridor(y, r1.x + r1.w, y, r2.x + 1))
                    for i in range(r1.x + r1.w - 1, r2.x + 1):
                        self.matrix[y][i] = CORR_HOR
                    self.matrix[y][r1.x + r1.w - 1] = DOOR_V
                    self.matrix[y][r2.x] = DOOR_V
            else:
                if r1.y > r2.y:
                    r1, r2 = r2, r1
                if r1.x < r2.x:
                    if randint(0, 1): # └ connection
                        self._bottom_left_corner_connection_(r1, r2)
                        # print('└ connection')
                    else: # ┐-connection
                        self._top_right_corner_connection_(r1, r2)
                        # print('┐ connection')
                else: 
                    if randint(0, 1):# ┘-connection
                        self._bottom_right_corner_connection_(r1, r2)
                        # print('┘ connection')
                    else: # ┌-connection
                        self._top_left_corner_connection_(r1, r2)
                        # print('┌ connection')
        return True

    def _place_corridors(self):     
        corridors = '┣┫┳╋┻┏┓┗┛┃━'
        for i in range(1, HEIGHT - 1):
            for j in range(1, WIDTH - 1):
                if self.matrix[i][j] in corridors:
                    if self.matrix[i - 1][j] in corridors:
                        if self.matrix[i + 1][j] in corridors:
                            if self.matrix[i][j + 1] in corridors: 
                                if self.matrix[i][j - 1] in corridors: 
                                    self.matrix[i][j] = '╋'
                                else:
                                    self.matrix[i][j] = '┣'
                            elif self.matrix[i][j - 1] in corridors: 
                                self.matrix[i][j] = '┫'
                        else:
                            if self.matrix[i][j + 1] in corridors: 
                                if self.matrix[i][j - 1] in corridors: 
                                    self.matrix[i][j] = '┻'
                                else:
                                    self.matrix[i][j] = '┗'
                            elif self.matrix[i][j - 1] in corridors: 
                                self.matrix[i][j] = '┛'
                    elif self.matrix[i + 1][j] in corridors:
                            if self.matrix[i][j + 1] in corridors: 
                                if self.matrix[i][j - 1] in corridors: 
                                    self.matrix[i][j] = '┳'
                                else:
                                    self.matrix[i][j] = '┏'
                            elif self.matrix[i][j - 1] in corridors: 
                                self.matrix[i][j] = '┓'

    # def _fix_corridors(self):
    #     corridors = {}
    #     for cor in self.corridors:
    #         for c in cor.path:
    #             corridors.setdefault(c, set()).update(cor.room_connect)
    #     self.corridors = corridors
        
    def _fix_rooms_and_corridors(self):
        self.gates = dict((g, ['g', None, None]) for r in self.rooms for g in r.gate)
        self.rooms = dict((f, ['r', None]) for r in self.rooms for f in r.floor)
        self.corridors = dict((p, ['c', None]) for c in self.corridors for p in c.path)
        self.coord = {**self.corridors, **self.rooms, **self.gates}
        


    def handle_move(self, char):
        if char in 'awsd':
            self.handle_player_move(char)
            self.handle_enemies()



    def handle_player_move(self, char):
        new_y, new_x = self.player.y, self.player.x
        if char == 'w':
            new_y -= 1
        elif char == 'a':
            new_x -= 1
        elif char == 's':
            new_y += 1
        elif char == 'd':
            new_x += 1
        pos = (new_y, new_x)
        value = self.coord.get(pos)
        if value is not None and value[1] is None:
            self.coord[pos][1] = PLAYER
            self.coord[(self.player.y, self.player.x)][1] = None
            self.player.y = new_y
            self.player.x = new_x
        # elif (new_y, new_x) in self.gates:
        



    def handle_enemies(self):
        pass


# ┣  ┫  ┳   ┻   ╋   ┏   ┓   ┗  ┛  



if __name__ == '__main__':
    l = Level()
    print(l, flush=True)
    # print(*l.rooms, sep='\n')
