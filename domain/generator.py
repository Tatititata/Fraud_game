from random import randint, choice
import traceback
from common.constants import *
# from common.playground import *
from .dungeon import Room, Corridor
import sys





class Generator:
    def __init__(self) -> None:
        self._matrix = None
        self._corridors = None
        self._rooms = None
        self.layout = None
        success = False
        while not success:
            try:
                # border is not valid for rooms:
                self._matrix = set((0, j) for j in range(WIDTH)) 
                self._matrix.update(set((i, 0) for i in range(HEIGHT)))

                # self._rooms = [Room(*r) for r in self._generate_rooms()]
                self._rooms = [Room((i, *r)) for i, r in enumerate(self._generate_rooms_full_random())]

                # no corridors yet:
                edges, self._start, self._end = self._connect_rooms()
                success = self._create_corridors(edges)
                self._update_corridors()

            except Exception as e:
                traceback.print_exc()
                success = False
        # with open('generator.txt', 'w') as f:
        #     f.write(f'generator\n{self}\n')


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

    def _generate_rooms_full_random(self) -> list:
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
        # rooms = [(30, 3, 9, 8), (15, 56, 14, 8), (31, 33, 6, 8), (11, 1, 7, 10), (32, 13, 14, 8), 
        #          (32, 81, 10, 13), (17, 81, 6, 10), (35, 67, 14, 10), (9, 29, 13, 11)]

        # rooms = [(5, 71, 13, 18), (31, 62, 7, 13), (10, 4, 15, 19), (18, 81, 12, 10), (37, 41, 11, 13), 
        #          (36, 2, 12, 10), (28, 18, 12, 18), (36, 87, 6, 11), (16, 50, 14, 16)]

        # rooms = [(1, 1, 6, 8), (1, 11, 8, 10)]
        # print(f'rooms = {rooms}')
        return rooms       
    
    def _generate_rooms(self) -> list:
        rooms = []
        self._matrix = [[0] * WIDTH for _ in range(HEIGHT)]
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
                                if self._matrix[y + i][x + j]:
                                    created = False
                                    j = w
                                    i = h
                                j += 1
                            i += 1
                        if created:
                            for i in range(h):
                                for j in range(w):
                                    self._matrix[y + i][x + j] = count
                            rooms.append((y + OFFSET // 2, x + OFFSET // 2, h - OFFSET, w - OFFSET))
                            count += 1
        # print(f'rooms = {rooms}')
        return rooms

    def _connect_rooms(self):
        graph = []
        for i in range(ROOMS):
            y1, x1 = self._rooms[i].center
            for j in range(i + 1, ROOMS):
                y2, x2 = self._rooms[j].center
                graph.append((abs(y1 - y2) + abs(x1 - x2), i, j))
        
        graph.sort()
        start, end = graph[-1][1], graph[-1][-1] # 2 rooms with longest edge, tmp value
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
        return edges, start, end
    
    def __repr__(self):
        endl = '\r\n'

        level = [f"{i:02d}" + ''.join(l) for i, l in enumerate(self.layout)]
        s1 = '  ' + ''.join(str(i) + ' ' * 9 for i in range(10)) + endl
        s2 = '  ' + '0123456789' * 10 + endl
        return s1 + s2 + endl.join(level)

    def _bottom_left_corner_connection_(self, r1:Room, r2:Room): # └ connection
        x = y = -1
        top_y = max(r2.y + 1, r1.y + r1.h)
        right_x = min(r1.x + r1.w - 2, r2.x - 1)
        # print(f'top_y = {top_y}, right_x = {right_x} L', end = ' ')
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
        # print(f'y = {y}, x = {x} L', end = ' ')
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
        # self._corridors.update(Corridor(r1.y + r1.h - 1, x, y, x).path | Corridor(y, x, y, r2.x).path)
        self._corridors.append(c)
        # print(f'y = {y}, x = {x} L')

    def _top_right_corner_connection_(self, r1:Room, r2:Room): # ┐ connection
        x = y = -1
        left_x = max(r1.x + r1.w, r2.x + 1)
        bottom_y = min(r1.y + r1.h - 2, r2.y - 1)
        # print(f'bottom_y = {bottom_y}, left_x = {left_x}', end = ' ')
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
        # print(f'y = {y}, x = {x} ┐', end = ' ')
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
        # self._corridors.update(Corridor(y, r1.x + r1.w - 1, y, x).path | Corridor(y, x, r2.y, x).path)
        # print(f'y = {y}, x = {x} ┐')

    def _bottom_right_corner_connection_(self, r1:Room, r2:Room): # ┘-connection
        x = y = -1
        left_x = max(r1.x + 1, r2.x + r2.w)
        top_y = max(r1.y + r1.h, r2.y + 1)
        # print(f'top_y = {top_y}, left_x = {left_x} ┘', end = ' ')
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
        # print(f'y = {y}, x = {x} ┘', end = ' ')
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
        # self._corridors.update(Corridor(y, r2.x + r2.w - 1, y, x).path | Corridor(r1.y + r1.h - 1, x, y, x).path)

        # print(f'y = {y}, x = {x} ┘') 

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
        # print(f'y = {y}, bottom_y = {bottom_y}, r2.y = {r2.y}, x = {x}, r1.x = {r1.x}, right_x = {right_x}', end = ' ')
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
        # print(f'y = {y}, x = {x}, ')
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
        # self._corridors.update(Corridor(y, x, y, r1.x).path | Corridor(y, x, r2.y, x).path)
         # print(f'y = {y}, x = {x} ┌')      

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
        # print(*edges, sep='\n')
        # return True
        for e in edges:
            v1, v2, hor, ver, _ = e
            r1 = self._rooms[v1]
            r2 = self._rooms[v2]
            # print(v1, v2, end = ' ')
            # print(hor, ver, end = ' ')
            if hor[0][1] + hor[1][1]:
                # top-bottom connection
                # print('top-bottom', end = ' ')
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
                # print(f'x = {x}')
                r1.make_gate(r1.y + r1.h - 1, x)
                r2.make_gate(r2.y, x)
                c = Corridor((r1.y + r1.h - 1, x, r2.y, x, r1.id, r2.id))
                self._corridors.append(c)

            elif ver[0][1] + ver[1][1]:
                    # left-right connection
                    # print('left and right', end = ' ')
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
                    # print(f'y = {y}')
                    r1.make_gate(y, r1.x + r1.w - 1)
                    r2.make_gate(y, r2.x)
                    c = Corridor((y, r1.x + r1.w - 1, y, r2.x, r1.id, r2.id))
                    self._corridors.append(c)
                    # for i in range(r1.x + r1.w - 1, r2.x + 1):
                    #     self._matrix[y][i] = CORR_HOR
                    # self._matrix[y][r1.x + r1.w - 1] = DOOR_V
                    # self._matrix[y][r2.x] = DOOR_V
            else:
                # return True
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

    @property
    def data(self):
        return self._rooms, self._corridors, self._start, self._end

    def __repr__(self):
        s = '\r\n'.join(str(r) for r in self._rooms)
        return f'{s}, \r\n{self._corridors}\r\n{self._start}\r\n{self._end}'



if __name__ == '__main__':
    l = Generator()
    print(l)
    print(*l.rooms, sep='\n')
