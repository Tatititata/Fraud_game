from common.characters import *
from .navigator import Navigator
from random import randint, choice


# - Персонаж:
#   + максимальный уровень здоровья,
#   + здоровье,
#   + ловкость,
#   + сила,
#   + текущее оружие;

# - Каждый противник имеет аналогичные игроку характеристики здоровья, ловкости и силы, 
# дополнительно к этому имеет характеристику враждебности.
# - Характеристика враждебности определяет расстояние, с которого противник начинает преследовать игрока.
# - 5 видов противников: 
#   + Зомби (отображение: зеленый z): низкая ловкость; средняя сила, враждебность; высокое здоровье. 
#   + Вампир (отображение: красная v): высокая ловкость, враждебность и здоровье; средняя сила. 
# Отнимает некоторое количество максимального уровня здоровья игроку при успешной атаке. 
# Первый удар по вампиру — всегда промах. 
#   + Привидение (отображение: белый g): высокая ловкость; низкая сила, враждебность и здоровье. 
# Постоянно телепортируется по комнате и периодически становится невидимым, пока игрок не вступил в бой. 
#   + Огр (отображение: желтый O): ходит по комнате на две клетки. Очень высокая сила и здоровье, 
# но после каждой атаки отдыхает один ход, затем гарантированно контратакует; низкая ловкость; 
# средняя враждебность.
#   + Змей-маг (отображение: белая s): очень высокая ловкость. 
# Ходит по карте по диагонали, постоянно меняя сторону. 
# У каждой успешной атаки есть вероятность «усыпить» игрока на один ход. Высокая враждебность.
# - Каждый тип противников имеет свой паттерн для передвижения по комнате.
# - Когда начинается преследование игрока, все монстры двигаются по одному паттерну, 
# кратчайшим путем по соседним клеткам в сторону игрока.
# - Если игрок находится в области, когда монстр должен начать его преследовать, 
# но при этом не существует пути к нему, то монстр продолжает двигаться случайным образом по своему паттерну.

class Color:
    _keys = [

    # '\033[1;37m',
    '\033[1;31m',  # красный
    '\033[1;32m',  # зеленый
    '\033[1;33m',  # желтый
    '\033[1;34m',  # синий
    '\033[1;35m',  # пурпурный
    '\033[1;36m',  # голубой
    # '\033[1;91m',  # ярко-красный
    '\033[1;92m',  # ярко-зеленый
    '\033[1;93m',  # ярко-желтый
    '\033[1;94m',  # ярко-синий
    '\033[1;95m',  # ярко-пурпурный
    '\033[1;96m' # ярко-голубой
    ]
    _index = 0

    def __new__(cls):
        color = cls._keys[cls._index]
        cls._index = (cls._index + 1) % len(cls._keys)
        return color

class Backpack:

    def __init__(self, data=None):
        self.have = dict((k, []) for k in ITEMS)
        if isinstance(data, dict):
            self._init_from_dict(data)

    def _init_from_dict(self, data:dict):
        for k, v in data.items():
            if k in ITEMS and len(v) <= CAPACITY:
                for i in v:
                    self.have[k].append(Item(i))
            else:
                raise AttributeError(f"{self.__class__.__name__}._init_from_dict")

    def __repr__(self):
        return str(self.to_dict())

    def place_item(self, item):
        if item.id in self.have and len(self.have[item.id]) < CAPACITY:
            self.have[item.id].append(item)
            return True
        return False

    def to_dict(self):
        return {k: [i.to_dict() for i in v] for k, v in self.have.items()}

    @property
    def dexterity(self):
        p = sum(i.power for i in self.have[POTION] if i.type == 'dexterity')
        s = sum(i.power for i in self.have[SCROLL] if i.type == 'dexterity')
        return  p + s 
    
    @property
    def strength(self):
        p = sum(i.power for i in self.have[POTION] if i.type == 'strength')
        s = sum(i.power for i in self.have[SCROLL] if i.type == 'strength')
        return  p + s 
    
    @property
    def health(self):
        p = sum(i.power for i in self.have[POTION] if i.type == 'max_health')
        s = sum(i.power for i in self.have[SCROLL] if i.type == 'max_health')
        return  p + s
    
    @property
    def food(self):
        return sum(i.power for i in self.have[FOOD])

    @property
    def weapon(self):
        if self.have[WEAPON]:
            return max(i.power for i in self.have[WEAPON])
        return 0


class Entity:
    def __init__(self, id=None, pos=None):
        self.id = id
        self.pos = pos

    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, pos):
        if isinstance(pos, list):
            self._pos = tuple(pos)
        else:
            self._pos = pos

    def to_dict(self):
        return {'pos': self._pos, 'id': self.id}
    
    def __str__(self):
        return '\033[1;37m' + self.id + '\033[0m'
    


class Door(Entity):
    def __init__(self, id, pos, color):
        super().__init__(id, pos)
        self.color = color
    

    def __str__(self):
        return f'{self.color + 'x\033[0m'}'

class Item(Entity):
    def __init__(self, data):

        if isinstance(data, tuple):
            self._init_new_item(data)
        elif isinstance(data, dict):
            self._init_from_dict(data)
        else:
            raise TypeError(f"{self.__class__.__name__}._init_ {type(data)}, {data}")

    def _init_from_dict(self, data:dict):
        if data.get('id'):
            for k, v in data.items():
                setattr(self, k, v)
        else:
            super().__init__(KEY, data.get('pos'))
            self.color = data.get('color')
            pos = data.get('door').get('pos')
            id = data.get('door').get('id')
            self.door = Door(id, pos, self.color)

    def _init_new_item(self, data):
        id, pos, k = data
        super().__init__(id, pos) 

        if self.id == WEAPON:
            self.type = choice(['spear', 'sword', 'knife'])
            self.power = randint(2, 5) + round(k)
        elif self.id == FOOD:
            self.type = choice(['bread', 'honey', 'steak', 'water'])
            self.power = round(randint(3, 8) * k)
        elif self.id == POTION:
            self.type = choice(['strength', 'dexterity', 'max_health'])
            self.power = round(randint(1, 3) * k)
            self.duration = round(randint(10, 20) * k)
        elif self.id == SCROLL:
            self.type = choice(['strength', 'dexterity', 'max_health'])
            self.power = round(randint(1, 2) * k)
        elif self.id == KEY:
            self.color = Color()
            id, pos = k
            self.door = Door(id, pos, self.color)


    def to_dict(self):
        if self.id == KEY:
            return {'color': self.color, 'pos': list(self.pos), 'door': self.door.to_dict()}
        d = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['pos'] = [*self.pos]
        return d
        
    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        if self.id == KEY:
            return f'{self.color + '&\033[0m'}'
        else:
            return super().__str__()


class Character(Entity):
    def __init__(self, id = None, pos=None, nav:Navigator=None):
        super().__init__(id, pos)
        self._nav = nav
        self.dexterity= 5
        self.strength = 5
        self.health = 20


            
        
