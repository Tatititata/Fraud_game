class Room:

    def __init__(self, data):
        if isinstance(data, tuple):
            self._init_from_tuple(data)
        elif isinstance(data, dict):
            self._init_from_dict(data)
        else:
            raise TypeError(f"{self.__class__.__name__}._init_")
            
    def _init_from_dict(self, data:dict):
        for k, v in data.items():
            if k.startswith('_'):
                setattr(self, k, {tuple(coord) for coord in v})
            else:
                setattr(self, k, v)


    def _init_from_tuple(self, data:tuple):
        # y, x = up left corner
        id, y, x, h, w = data
        self.id = id
        self.y = y
        self.x = x
        self.h = h
        self.w = w
        self._gate = set()

    @property
    def floor(self):
        if not hasattr(self, '_floor'):
            floor = set((i, j) for i in range(self.y + 1, self.y + self.h - 1) for j in range(self.x + 1, self.x + self.w - 1))    
            setattr(self,  '_floor', floor)
            return floor
        return self._floor 
    
    @property
    def tlc(self):
        return (self.y, self.x)
    
    @property
    def trc(self):
        return (self.y, self.x + self.w - 1)

    @property
    def blc(self):
        return (self.y + self.h - 1, self.x)
    
    @property
    def brc(self):
        return (self.y + self.h - 1, self.x + self.w - 1)
    
    @property
    def vertical_walls(self):
        left_wall = set((i, self.x) for i in range(self.y + 1, self.y + self.h - 1))
        right_wall = set((i, self.x + self.w - 1) for i in range(self.y + 1, self.y + self.h - 1))
        left_wall.update(right_wall)
        left_wall -= self._gate
        return left_wall
    
    @property
    def horizontal_walls(self):
        top_wall = set((self.y, j) for j in range(self.x + 1, self.x + self.w - 1))
        bottom_wall = set((self.y + self.h - 1, j) for j in range(self.x + 1, self.x + self.w - 1))
        top_wall.update(bottom_wall)
        top_wall -= self.gate
        return top_wall
        

    def to_dict(self):
        d = {attr: getattr(self, attr) for attr in self.__dict__ if not attr.startswith('_')}
        d['_gate'] = [[y, x] for (y,x ) in self._gate]
        return d

    @property
    def center(self):
        return (self.y + self.h / 2, self.x + self.w / 2)
    
    @property
    def walls(self):
        return {self.tlc, self.trc, self.blc, self.brc} \
            | self.horizontal_walls | self.vertical_walls | self.gate

    @property
    def gate(self):
        return self._gate
    
    def make_gate(self, y, x):
        pos = (y, x)
        self._gate.add(pos)

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
            raise TypeError(f"{self.__class__.__name__}._init_")

    def _init_from_dict(self, data:dict):
        for k, v in data.items():
            if not hasattr(self, k):
                raise AttributeError(f"{self.__class__.__name__}._init_from_dict")
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
        # return repr({k: v for k, v in self.__dict__.items() if not k.startswith('__')})
        return str(self.connecting)
    

    def to_dict(self):
        d = {attr: getattr(self, attr) for attr in self.__dict__ if not attr.startswith('__')}
        for a, v in d.items():
            if isinstance(v, set):
                d[a] = [*v]

        return d