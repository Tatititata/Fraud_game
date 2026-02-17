class Room:

    def __init__(self, data):
        self.id = None
        self.floor = None
        self.tlc = None
        self.trc = None
        self.blc = None
        self.brc = None
        self.left_wall = None
        self.right_wall = None
        self.top_wall = None
        self.bottom_wall = None
        self.gate = None

        if isinstance(data, tuple):
            self._init_from_tuple(data)
        elif isinstance(data, dict):
            self._init_from_dict(data)
        else:
            raise

    # def _init_from_dict(self, data:dict):
    #     with open('loader.txt', 'a') as f:
    #         f.write(f'\nJSON\n{data.items()}\n')
    #         f.write(f'\n_self\n{dir(self)}\n')

    #         for k, v in data.items():
    #             if hasattr(self, k):
    #                 if k == 'id':
    #                     setattr(self, k, v)
    #                 else:
    #                     setattr(self, k, {(i[0], i[1]) for i in v})
    #                 f.write(f'\n_self\n{k}, {v}\n')
    #             else:
    #                 raise
            
    def _init_from_dict(self, data:dict):
        SINGLE_COORDS = {'tlc', 'trc', 'blc', 'brc'}
        MULTI_COORDS = {'floor', 'left_wall', 'right_wall', 'top_wall', 'bottom_wall', 'gate'}
        
        for k, v in data.items():
            if not hasattr(self, k):
                raise AttributeError(f"{k} not in Room")
            if k == 'id':
                setattr(self, k, v)
            elif k in SINGLE_COORDS:
                setattr(self, k, tuple(v))
            elif k in MULTI_COORDS:
                setattr(self, k, {tuple(coord) for coord in v})



    def _init_from_tuple(self, data:tuple):
        # y, x = up left corner
        id, y, x, h, w = data
        self.id = id
        self.floor = set((i, j) for i in range(y + 1, y + h - 1) for j in range(x + 1, x + w - 1))
        self.tlc = (y, x)
        self.trc = (y, x + w - 1)
        self.blc = (y + h - 1, x)
        self.brc = (y + h - 1, x + w - 1)
        self.left_wall = set((i, x) for i in range(y + 1, y + h - 1))
        self.right_wall = set((i, x + w - 1) for i in range(y + 1, y + h - 1))
        self.top_wall = set((y, j) for j in range(x + 1, x + w - 1))
        self.bottom_wall = set((y + h - 1, j) for j in range(x + 1, x + w - 1))
        self.gate = set()

    def to_dict(self):
        d = {attr: getattr(self, attr) for attr in self.__dict__ if not attr.startswith('_')}
        for a, v in d.items():
            if isinstance(v, set):
                d[a] = [*v]

        return d

    @property
    def y(self):
        return self.tlc[0]
    @property
    def x(self):
        return self.tlc[1]
    @property
    def h(self):
        return self.blc[0] - self.tlc[0] + 1
    @property
    def w(self):
        return self.trc[1] - self.tlc[1] + 1
    @property
    def center(self):
        return (self.tlc[0] + self.blc[0]) / 2, (self.tlc[1] + self.trc[1]) / 2
    
    @property
    def walls(self):
        return {self.tlc, self.trc, self.blc, self.brc} \
            | self.left_wall | self.right_wall | self.top_wall | self.bottom_wall | self.gate

    def make_gate(self, y, x):
        pos = (y, x)
        self.gate.add(pos)
        # self.floor.add(pos)
        if pos in self.left_wall:
            self.left_wall.discard(pos)
        elif pos in self.right_wall:
            self.right_wall.discard(pos)
        elif pos in self.top_wall:
            self.top_wall.discard(pos)
        else:
            self.bottom_wall.discard(pos)

    def __repr__(self):
        return repr({k: v for k, v in self.__dict__.items() if not k.startswith('_')})
        return f"[y={self.y}, x={self.x}, h={self.h}, w={self.w}, gate={repr(self.gate)}]"
    

class Corridor:

    def __init__(self, data):
        self._connecting = None
        self._path = None

        if isinstance(data, tuple):
            self._init_from_tuple(data)
        elif isinstance(data, dict):
            self._init_from_dict(data)
        else:
            raise

    def _init_from_dict(self, data:dict):
        for k, v in data.items():
            if not hasattr(self, k):
                raise AttributeError(f"{k} not in Room")
            if k == '_connecting':
                setattr(self, k, set(v))
            elif k == '_path':
                setattr(self, k, {tuple(coord) for coord in v})

    def _init_from_tuple(self, data:tuple):
        y1, x1, y2, x2, r1, r2 = data
        self._connecting = {r1, r2}

        # y1 <= y2, x1 <= x2
        self._path = set()
        self.add_path(y1, x1, y2, x2)

    @property
    def walls(self):
        return self._path
    
    @property
    def connecting(self):
        return self._connecting

    def add_connection(self, rooms_num:set):
        self._connecting.update(rooms_num)

    def add_walls(self, walls:set):
        self._path.update(walls)

    def add_path(self, y1, x1, y2, x2):
        self._path.update(set((i, x1) for i in range(y1, y2 + 1)))
        self._path.update(set((y2, j) for j in range(x1, x2 + 1)))

    def __repr__(self):
        return repr({k: v for k, v in self.__dict__.items() if not k.startswith('__')})
        return str(self.connecting)
    

    def to_dict(self):
        d = {attr: getattr(self, attr) for attr in self.__dict__ if not attr.startswith('__')}
        for a, v in d.items():
            if isinstance(v, set):
                d[a] = [*v]

        return d