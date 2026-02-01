from random import randint

# ┏  # U+250F BOX DRAWINGS HEAVY DOWN AND RIGHT
# ┓  # U+2513 BOX DRAWINGS HEAVY DOWN AND LEFT
# ┗  # U+2517 BOX DRAWINGS HEAVY UP AND RIGHT  
# ┛  # U+251B BOX DRAWINGS HEAVY UP AND LEFT
# ┃  # U+2503 BOX DRAWINGS HEAVY VERTICAL
# ━  # U+2501 BOX DRAWINGS HEAVY HORIZONTAL
# ┣  # U+2523 BOX DRAWINGS HEAVY VERTICAL AND RIGHT
# ┫  # U+252B BOX DRAWINGS HEAVY VERTICAL AND LEFT
# ┳  # U+2533 BOX DRAWINGS HEAVY DOWN AND HORIZONTAL
# ┻  # U+253B BOX DRAWINGS HEAVY UP AND HORIZONTAL
# ╋  # U+254B BOX DRAWINGS HEAVY VERTICAL AND HORIZONTAL
ROOMS = 9
OFFSET = 1
MIN_ROOM_WIDTH = 8 + OFFSET
MAX_ROOM_WIDTH = 20 + OFFSET
MIN_ROOM_HEIGHT = 6 + OFFSET
MAX_ROOM_HEIGHT = 15 + OFFSET

MIN_ROOM_AREA = MIN_ROOM_WIDTH * MIN_ROOM_HEIGHT
MAX_ROOM_AREA = MAX_ROOM_WIDTH * MAX_ROOM_HEIGHT
CORRIDOR = 1
CORR_VER = '┃' #'║' # '·'
CORR_HOR = '━' #'═' # '·'

WALL_HOR = '─' # '─'
WALL_VER = '│' # '│'
# CORNER = '-'
ULCR = '┌' # '┌'
BLCR = '└' # '└'
URCR = '┐' # '┐' ┓
BRCR = '┘' # '┘'
ROOM_CORNERS = (ULCR, URCR, BRCR, BLCR)
ROOM_WALLS = (ULCR, URCR, BRCR, BLCR, WALL_HOR, WALL_VER)
ULC = '┏' #'╔'  '┌'
BLC = '┗' #'╚'  '└'
URC = '┓'  #'╗' # '┐'
BRC = '┛' # '╝' # '┘'
FLOOR = '·'
GROUND = ' '
DOOR_H = '┃' # '╫' # '╬' '┼' door on horizontal wall
DOOR_V =  '━' #'╪' # '╬' '┼' door on vertical wall
WIDTH = 100
HEIGHT = 50

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
    def __init__(self, y1, x1, y2, x2, r1, r2):
        # y1 <= y2, x1 <= x2
        self.path = set((i, x1) for i in range(y1, y2 + 1)) | set((y2, j) for j in range(x1, x2 + 1))
        self.room_connect = (r1, r2)



class Level:

    def __init__(self, level:int=0) -> None:
        self.id = level
        self.width = WIDTH
        self.height = HEIGHT
        self.matrix = []
        # self.rooms = [Room(*r) for r in self._generate_rooms()]
        
        self.rooms = [Room(*r) for r in self._generate_rooms_full_random()]
        
        self._place_rooms()
        # print(self.__repr__(), flush=True)
        self.corridors = []
        self._create_corridors(self._connect_rooms())
        self._fix_corridors()
        print(*self.rooms, sep='\n')


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
        # rooms = [
        # (5, 45, 17, 10), 
        # (4, 7, 17, 10), 
        # (26, 80, 7, 14), 
        # (19, 33, 17, 10), 
        # (40, 24, 8, 19), 
        # (32, 7, 9, 8), 
        # (24, 61, 14, 12), 
        # (9, 76, 6, 17), 
        # (36, 47, 11, 10)]
        # rooms = [(1, 39, 7, 11), (7, 67, 6, 14), (32, 82, 6, 9), (18, 31, 14, 14), 
        #          (35, 10, 7, 8), (34, 35, 6, 9), (10, 14, 7, 12), (21, 72, 11, 8), (38, 59, 8, 11)]

        # rooms = [(13, 75, 13, 9), (3, 7, 9, 8), (28, 4, 12, 10), (24, 31, 8, 17), (21, 16, 9, 10), 
        #          (29, 79, 8, 8), (3, 54, 8, 9), (34, 46, 9, 15), (37, 30, 6, 8)]

        # rooms = [(32, 63, 13, 16), (27, 30, 7, 17), (7, 12, 6, 8), (27, 9, 12, 9), (18, 54, 12, 12), 
        #         (15, 82, 13, 11), (11, 2, 9, 8), (7, 41, 13, 9), (5, 77, 7, 15)]

        # rooms = [(25, 23, 11, 14), (37, 43, 11, 8), (6, 13, 15, 13), (36, 64, 7, 15), (19, 62, 10, 19), 
        #          (16, 39, 13, 13), (2, 58, 10, 14), (10, 87, 9, 9), (39, 3, 8, 14)]

        # rooms = [(5, 27, 13, 10), (11, 52, 8, 12), (30, 17, 13, 16), (21, 56, 13, 11), (13, 3, 15, 16), 
        #          (37, 76, 11, 12), (1, 61, 8, 11), (7, 84, 6, 8), (23, 78, 12, 10)]

        # rooms = [(32, 71, 14, 8), (2, 57, 14, 17), (13, 2, 8, 12), (29, 29, 12, 9), 
        #          (1, 88, 8, 10), (2, 4, 9, 8), (12, 88, 14, 8), (21, 53, 7, 17), (35, 17, 12, 9)]

        # rooms = [(20, 6, 8, 13), (30, 69, 7, 10), (36, 18, 9, 8), (25, 34, 6, 18), (9, 21, 6, 18), 
        #          (18, 69, 7, 9), (4, 67, 10, 14), (3, 46, 7, 11), (39, 31, 6, 18)]

        # rooms = [(26, 21, 10, 10), (6, 6, 11, 14), (27, 61, 7, 10), (5, 49, 10, 11), (32, 80, 13, 9), 
        #          (35, 35, 7, 19), (12, 75, 13, 8), (5, 30, 6, 15), (16, 36, 10, 9)]

        # rooms = [(32, 59, 13, 12), (12, 33, 15, 9), (32, 79, 11, 9), (7, 1, 7, 19), (5, 81, 6, 12), 
        #          (35, 18, 6, 10), (6, 56, 8, 12), (20, 2, 11, 11), (1, 31, 7, 19)]

        # rooms = [(7, 36, 13, 12), (34, 2, 10, 13), (31, 34, 14, 8), (24, 5, 6, 15), 
        #          (32, 46, 9, 11), (14, 76, 12, 10), (26, 63, 10, 9), (1, 19, 12, 11), (3, 52, 14, 16)]

        # rooms = [(25, 67, 15, 9), (15, 63, 7, 12), (17, 33, 14, 9), (36, 2, 10, 11), 
        #          (5, 5, 7, 20), (8, 89, 14, 9), (36, 42, 8, 14), (35, 25, 8, 10), (37, 79, 7, 8)]

        # rooms = [(37, 32, 8, 11), (5, 1, 9, 15), (27, 49, 7, 14), (10, 53, 13, 17), 
        #          (25, 9, 7, 9), (8, 81, 11, 11), (31, 68, 11, 15), (7, 20, 9, 19), (20, 28, 6, 10)]

        # rooms = [(20, 31, 13, 14), (37, 12, 9, 20), (10, 55, 13, 9), (24, 71, 9, 14), (8, 9, 7, 8), 
        #          (3, 69, 7, 16), (9, 39, 7, 10), (23, 6, 10, 20), (1, 25, 10, 10)]

        # rooms = [(24, 85, 11, 10), (10, 82, 9, 11), (2, 49, 10, 12), (19, 16, 9, 9), (40, 22, 7, 20), 
        #          (3, 65, 15, 8), (37, 52, 6, 17), (25, 2, 10, 10), (16, 33, 8, 18)]

        # rooms = [(30, 77, 10, 18), (17, 35, 6, 16), (8, 4, 7, 10), (18, 65, 6, 9), (31, 23, 14, 15), 
        #          (7, 76, 11, 13), (17, 12, 14, 8), (5, 17, 9, 11), (10, 53, 6, 9)]

        # rooms = [(20, 2, 9, 9), (38, 75, 6, 20), (27, 28, 6, 12), (19, 48, 13, 17), (36, 37, 12, 19), 
        #          (35, 1, 7, 9), (1, 10, 8, 13), (26, 15, 13, 11), (1, 77, 10, 9)]

        # rooms = [(22, 70, 7, 19), (22, 30, 15, 13), (9, 6, 6, 10), (9, 63, 11, 9), (13, 49, 7, 11), 
        #          (2, 22, 7, 16), (36, 55, 9, 15), (18, 8, 12, 9), (2, 77, 7, 11)]


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
        # rooms = [
        # (5, 45, 17, 10), 
        # (4, 7, 17, 10), 
        # (26, 80, 7, 14), 
        # (19, 33, 17, 10), 
        # (40, 24, 8, 19), 
        # (32, 7, 9, 8), 
        # (24, 61, 14, 12), 
        # (9, 76, 6, 17), 
        # (36, 47, 11, 10)]
        # rooms = [(1, 39, 7, 11), (7, 67, 6, 14), (32, 82, 6, 9), (18, 31, 14, 14), 
        #          (35, 10, 7, 8), (34, 35, 6, 9), (10, 14, 7, 12), (21, 72, 11, 8), (38, 59, 8, 11)]
        # rooms = [(13, 75, 13, 9), (3, 7, 9, 8), (28, 4, 12, 10), (24, 31, 8, 17), (21, 16, 9, 10), 
        #          (29, 79, 8, 8), (3, 54, 8, 9), (34, 46, 9, 15), (37, 30, 6, 8)]
        # rooms = [(32, 63, 13, 16), (27, 30, 7, 17), (7, 12, 6, 8), (27, 9, 12, 9), (18, 54, 12, 12), 
        #         (15, 82, 13, 11), (11, 2, 9, 8), (7, 41, 13, 9), (5, 77, 7, 15)]
        # rooms = [(25, 23, 11, 14), (37, 43, 11, 8), (6, 13, 15, 13), (36, 64, 7, 15), (19, 62, 10, 19), 
        #          (16, 39, 13, 13), (2, 58, 10, 14), (10, 87, 9, 9), (39, 3, 8, 14)]
        # rooms = [(5, 27, 13, 10), (11, 52, 8, 12), (30, 17, 13, 16), (21, 56, 13, 11), (13, 3, 15, 16), 
        #          (37, 76, 11, 12), (1, 61, 8, 11), (7, 84, 6, 8), (23, 78, 12, 10)]

        # rooms = [(32, 71, 14, 8), (2, 57, 14, 17), (13, 2, 8, 12), (29, 29, 12, 9), 
        #          (1, 88, 8, 10), (2, 4, 9, 8), (12, 88, 14, 8), (21, 53, 7, 17), (35, 17, 12, 9)]
        # rooms = [(20, 6, 8, 13), (30, 69, 7, 10), (36, 18, 9, 8), (25, 34, 6, 18), (9, 21, 6, 18), 
        #          (18, 69, 7, 9), (4, 67, 10, 14), (3, 46, 7, 11), (39, 31, 6, 18)]
        # rooms = [(26, 21, 10, 10), (6, 6, 11, 14), (27, 61, 7, 10), (5, 49, 10, 11), (32, 80, 13, 9), 
        #          (35, 35, 7, 19), (12, 75, 13, 8), (5, 30, 6, 15), (16, 36, 10, 9)]
        # rooms = [(32, 59, 13, 12), (12, 33, 15, 9), (32, 79, 11, 9), (7, 1, 7, 19), (5, 81, 6, 12), 
        #          (35, 18, 6, 10), (6, 56, 8, 12), (20, 2, 11, 11), (1, 31, 7, 19)]

        # rooms = [(7, 36, 13, 12), (34, 2, 10, 13), (31, 34, 14, 8), (24, 5, 6, 15), 
        #          (32, 46, 9, 11), (14, 76, 12, 10), (26, 63, 10, 9), (1, 19, 12, 11), (3, 52, 14, 16)]

        # rooms = [(25, 67, 15, 9), (15, 63, 7, 12), (17, 33, 14, 9), (36, 2, 10, 11), 
        #          (5, 5, 7, 20), (8, 89, 14, 9), (36, 42, 8, 14), (35, 25, 8, 10), (37, 79, 7, 8)]


        print(f'rooms = {rooms}')
        return rooms

    def _connect_rooms(self):
        graph = []
        for i in range(ROOMS):
            y1, x1 = self.rooms[i].center
            for j in range(i + 1, ROOMS):
                y2, x2 = self.rooms[j].center
                graph.append((2 * abs(y1 - y2) + abs(x1 - x2), i, j))
        
        graph.sort()
        print(*graph, sep='\n')
        print(graph[0])
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
        print(edges)
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

    def _create_corridors_old_version(self, edges:list[Room]):
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
        print(*edges, sep='\n')
        for e in edges:
            r1, r2, hor, ver, _ = e
            print(r1, r2, end = ' ')
            print(hor, ver, end = ' ')
            r1 = self.rooms[r1]
            r2 = self.rooms[r2]
            if hor[0][1] + hor[1][1]:
                print('up and down', end = ' ')
                if r1.y > r2.y:
                    r1, r2 = r2, r1
                x = randint(hor[1][0], hor[2][0] - 1)
                print(f'x = {x}')
                for i in range(r1.y + r1.h - 1, r2.y + 1):
                    self.matrix[i][x] = CORR_VER

            elif ver[0][1] + ver[1][1]:
                    print('left and right', end = ' ')
                    if r1.x > r2.x:
                        r1, r2 = r2, r1
                    y = randint(ver[1][0], ver[2][0] - 1)
                    print(f'y = {y}')
                    for i in range(r1.x + r1.w - 1, r2.x + 1):
                        self.matrix[y][i] = CORR_HOR
            else:
                x = -1
                y = -1
                if r1.y > r2.y:
                    r1, r2 = r2, r1
                if r1.x < r2.x:
                    if randint(0, 1): # |_ connection
                        for j in range(r1.x, r1.x + r1.w):
                            if self.matrix[r1.y + r1.h - 1][j] == CORR_VER:
                                x = j
                        if x == -1:
                            x = randint(hor[0][0], min(hor[1][0] - 1, hor[2][0] - 2))
                        for i in range(r2.y + 1, r2.y + r2.h):
                            if self.matrix[i][r2.x] == CORR_HOR:
                                y = i
                        if y == -1:
                            y = randint(max(ver[1][0] + 2, ver[2][0] + 1), ver[3][0])

                        for i in range(max(ver[1][0] + 2, ver[2][0] + 1), ver[3][0] + 1):
                            for j in range(hor[0][0], min(hor[1][0] - 1, hor[2][0] - 2) + 1):
                                if self.matrix[i][j] == WALL_HOR or self.matrix[i][j] == WALL_VER:
                                    if y >= i:
                                        y = i - 1
                                    if x >= j:
                                        x = j - 1

                        for i in range(x, r2.x + 1):
                            self.matrix[y][i] = CORR_HOR
                        for i in range(r1.y + r1.h - 1, y + 1):
                            self.matrix[i][x] = CORR_VER
                        print(f'y = {y}, x = {x} L')

                    else:
                        for j in range(r2.x, r2.x + r2.w):
                            if self.matrix[r2.y][j] == CORR_VER:
                                x = j
                        if x == -1:
                            x = randint(max(hor[1][0] + 2, hor[2][0] + 1), hor[3][0] - 1)
                        for i in range(r1.y, r1.y + r1.h):
                            if self.matrix[i][r1.x + r1.w - 1] == CORR_HOR:
                                y = i
                        if y == -1:
                            y = randint(ver[0][0] + 1, min(ver[1][0] - 1, ver[2][0] - 2))

                        for i in range(ver[0][0] + 1, min(ver[1][0] - 1, ver[2][0] - 2) + 1):
                            for j in range(max(hor[1][0] + 2, hor[2][0] + 1), hor[3][0]):
                                if self.matrix[i][j] == WALL_HOR or self.matrix[i][j] == WALL_VER:
                                    if y <= i:
                                        y = i + 1
                                    if x >= j:
                                        x = j - 1

                        for i in range(y, r2.y + 1):
                            self.matrix[i][x] = CORR_VER
                        for j in range(r1.x + r1.w - 1, x + 1):
                            self.matrix[y][j] = CORR_HOR

                        print(f'y = {y}, x = {x} ┐')
                else:
                    if randint(0, 1):
                        for j in range(r1.x, r1.x + r1.w):
                            if self.matrix[r1.y + r1.h - 1][j] == CORR_VER:
                                x = j
                        if x == -1:
                            x = randint(hor[2][0] + 1, hor[3][0] - 1)
                        for i in range(r2.y + 1, r2.y + r2.h):
                            if self.matrix[i][r2.x + r2.w - 1] == CORR_HOR:
                                y = i
                        if y == -1:
                            y = randint(ver[2][0] + 1, ver[3][0] - 1)
                        for j in range(r2.x + r2.w - 1, x + 1):
                            self.matrix[y][j] = CORR_HOR
                        for i in range(r1.y + r1.h - 1, y + 1):
                            self.matrix[i][x] = CORR_VER
                        print(f'y = {y}, x = {x} ┘')     
                    else:
                        j = r2.x
                        while(j < r2.x + r2.w):
                            if self.matrix[r2.y][j] == CORR_VER:
                                x = j
                                j = 101
                            j += 1
                        # for j in range(r2.x, r2.x + r2.w):
                        #     if self.matrix[r2.y][j] == CORR_VER:
                        #         x = j
                        if x == -1:
                            x = randint(hor[0][0] + 1, hor[1][0] - 1)
                        i = r1.y
                        while i < r1.y + r1.h:
                            if self.matrix[i][r1.x] == CORR_HOR:
                                y = i
                                i = 101
                            i += 1

                        # for i in range(r1.y, r1.y + r1.h):
                        #     if self.matrix[i][r1.x] == CORR_HOR:
                        #         y = i
                        if y == -1:
                            y = randint(ver[0][0] + 1, ver[1][0] - 1)
                        for i in range(y, r2.y + 1):
                            self.matrix[i][x] = CORR_VER
                        for j in range(x, r1.x + 1):
                            self.matrix[y][j] = CORR_HOR

                        print(f'y = {y}, x = {x} ┌')                     

    def bottom_left_corner_connection_(self, r1:Room, r2:Room): # └ connection
        x = y = -1
        top_y = max(r2.y + 1, r1.y + r1.h)
        right_x = min(r1.x + r1.w - 2, r2.x - 1)
        print(f'top_y = {top_y}, right_x = {right_x} L', end = ' ')
        i = top_y
        while i < r2.y + r2.h - 1:
            if self.matrix[i][r2.x] == DOOR_V:
                y = i
                i = 101
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
        while i < y:
            j = right_x
            while j < r2.x:
                if self.matrix[i][j] in ROOM_WALLS:
                    y = i - 1
                j += 1 
            i += 1

        j = right_x
        while j > x:
            i = top_y
            while i < y:
                if self.matrix[i][j] in ROOM_WALLS:
                    x = j + 1
                i += 1
            j -= 1    
            

        for j in range(x, r2.x + 1):
            self.matrix[y][j] = CORR_HOR
        for i in range(r1.y + r1.h - 1, y + 1):
            self.matrix[i][x] = CORR_VER
        self.matrix[y][r2.x] = DOOR_V
        self.matrix[r1.y + r1.h - 1][x] = DOOR_H
        # self.matrix[y][x] = BLC
        print(f'y = {y}, x = {x} L')

    def top_right_corner_connection_(self, r1:Room, r2:Room): # ┐ connection
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

        
        # self.matrix[y][x] = URC
        print(f'y = {y}, x = {x} ┐')

    def bottom_right_corner_connection_(self, r1:Room, r2:Room): # ┘-connection
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
            j = left_x
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
        # self.matrix[y][x] = BRC
        print(f'y = {y}, x = {x} ┘') 

    def top_left_corner_connection_(self, r1:Room, r2:Room): # ┌-connection
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
            print(f'r1.y + 1 = {r1.y + 1}, bottom_y = {bottom_y}, x = {x}', end = ' ')
            y = randint(r1.y + 1, bottom_y)
        i = bottom_y
        while i >= y:
            j = right_x
            if self.matrix[i][j] in ROOM_WALLS:
                y = i + 1
                i += 1
            while j >= x:
                if self.matrix[i][j] in ROOM_WALLS:
                    x = j + 1
                j -= 1
            i -= 1

        for j in range(x, r1.x + 1):
            self.matrix[y][j] = CORR_HOR
        for i in range(y, r2.y + 1):
            self.matrix[i][x] = CORR_VER
        self.matrix[y][r1.x] = DOOR_V
        self.matrix[r2.y][x] = DOOR_H
        # self.matrix[y][x] = ULC
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
        print(*edges, sep='\n')
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
                self.corridors.append(Corridor(r1.y + r1.h, x, r2.y - 1, x, r1, r2))
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
                    self.corridors.append(Corridor(y, r1.x + r1.w, y, r2.x + 1, r1, r2))
                    for i in range(r1.x + r1.w - 1, r2.x + 1):
                        self.matrix[y][i] = CORR_HOR
                    self.matrix[y][r1.x + r1.w - 1] = DOOR_V
                    self.matrix[y][r2.x] = DOOR_V
            else:
                if r1.y > r2.y:
                    r1, r2 = r2, r1
                if r1.x < r2.x:
                    if randint(0, 1): # └ connection
                        self.bottom_left_corner_connection_(r1, r2)
                        # print('└ connection')
                    else: # ┐-connection
                        self.top_right_corner_connection_(r1, r2)
                        # print('┐ connection')
                else: 
                    if randint(0, 1):# ┘-connection
                        self.bottom_right_corner_connection_(r1, r2)
                        # print('┘ connection')
                    else: # ┌-connection
                        self.top_left_corner_connection_(r1, r2)
                        # print('┌ connection')

    def _fix_corridors(self):     
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



# ┣  ┫  ┳   ┻   ╋   ┏   ┓   ┗  ┛  



if __name__ == '__main__':
    # Level()
    # print(Level(), flush=True)
    l = Level()
    print(*l.rooms, sep='\n')
