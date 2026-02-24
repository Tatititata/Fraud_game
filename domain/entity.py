from common.characters import *
from .navigator import Navigator
from random import randint, choice
# from globals.globals import global_counter
import sys
import copy

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

    '\033[1;37m',
    '\033[1;31m',  # красный
    '\033[1;32m',  # зеленый
    '\033[1;33m',  # желтый
    '\033[1;34m',  # синий
    '\033[1;35m',  # пурпурный
    '\033[1;36m',  # голубой
    '\033[1;91m',  # ярко-красный
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

class Key(Entity):

    # _keys = [

    # '\033[1;37m',
    # '\033[1;31m',  # красный
    # '\033[1;32m',  # зеленый
    # '\033[1;33m',  # желтый
    # '\033[1;34m',  # синий
    # '\033[1;35m',  # пурпурный
    # '\033[1;36m',  # голубой
    # '\033[1;91m',  # ярко-красный
    # '\033[1;92m',  # ярко-зеленый
    # '\033[1;93m',  # ярко-желтый
    # '\033[1;94m',  # ярко-синий
    # '\033[1;95m',  # ярко-пурпурный
    # '\033[1;96m' # ярко-голубой
    # ]
    # _count = 0

    def __init__(self, data, pos=None):
        if isinstance(data, set):
            super().__init__(KEY, pos)
            self.color = Color()
            self.doors = data
        elif isinstance(data, dict):
            super().__init__(KEY, data.get('pos'))
            self.color = data.get('color')
            self.doors = {tuple(d) for d in data.get('doors')}

    @property
    def full_id(self):
        return self.color + self.id + '\033[0m'

    def to_dict(self):
        return {'color': self.color, 'pos': list(self.pos), 'doors': [list(d) for d in self.doors]}

    def __repr__(self):

        return f'pos={self.pos}'


class Item(Entity):
    def __init__(self, data):

        if isinstance(data, tuple):
            self._init_new_item(data)
        elif isinstance(data, dict):
            self._init_from_dict(data)
        else:
            raise TypeError(f"{self.__class__.__name__}._init_ {type(data)}, {data}")

    def _init_from_dict(self, data:dict):
        if 'id' in data:
            for k, v in data.items():
                setattr(self, k, v)
        else:
            raise AttributeError(f"{self.__class__.__name__}._init_from_dict")

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


    def to_dict(self):
        d = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['pos'] = [*self.pos]
        return d
        
    def __repr__(self):
        return str(self.__dict__)




class Character(Entity):
    def __init__(self, id = None, pos=None, nav:Navigator=None):
        super().__init__(id, pos)
        self._nav = nav
        self.dexterity= 5
        self.strength = 5
        self.health = 20

    def attack(self, target):
        
            
        random_value = randint(1, self.dexterity + target.dexterity)

        if random_value <= self.dexterity:
            damage = self.strength - target.strength
            damage = 1 if damage < 1 else damage
            target.health -= damage
            self._nav.add_statistics('hits_taken')
            self._nav.add_statistics('health_used', damage)
            
        
class Player(Character):

    def __init__(self, data=None, nav:Navigator=None):
        super().__init__(PLAYER, None, nav)
        self._permanent_items = {}
        self._free_hands = Item((WEAPON, (0,0), 1))
        self._free_hands.power = 0
        self.current_weapon = self._free_hands

        if data is None:
            self.max_health = 20
            self.backpack = Backpack()
        else:
            self._init_from_dict(data)

    def _init_from_dict(self, data:dict):
        for k, v in data.items():
            if not isinstance(k, dict):
                setattr(self, k, v)
        self.backpack = Backpack(data.get('backpack'))
        self.current_weapon = Item(data.get('current_weapon'))
        self._permanent_items = {(i, j):k for i, j, k in data.get('_permanent_items')}

    def attack(self, target):
        random_value = randint(1, self.dexterity + target.dexterity)

        with open('monsters_attack.txt', 'a') as f:
            f.write(f'{target.id}, random value={random_value}, self.dex={self.dexterity}, target.health={target.health}\n')

        if random_value <= self.dexterity:
            damage = self.strength + self.current_weapon.power - target.strength
            damage = 1 if damage < 1 else damage
            target.health -= damage
            self._nav.add_statistics('hits_dealt')
            

    def to_dict(self):
        d = {
        'pos': self.pos, 
        'dexterity': self.dexterity, 
        'strength': self.strength, 
        'health': self.health, 
        'current_weapon': self.current_weapon.to_dict(), 
        'max_health': self.max_health, 
        'backpack': self.backpack.to_dict(),
        '_permanent_items': [[*k, v] for k, v in self._permanent_items.items()]
    }
        return d

    def get_item(self, item:Item):
        return self.backpack.place_item(item)

    def _place_current_weapon(self):
        if self.current_weapon.power:
            if self.backpack.place_item(self.current_weapon):
                self.current_weapon = self._free_hands
                return True
        return False
    
    def _drop_weapon(self):
        self._nav.place_weapon(self.pos, self.current_weapon)
        self.current_weapon = self._free_hands

    def use_backpack(self, gamestate, idx):
        idx = ord(idx) - 49 # idx = digit 1-10
        backpack = self.backpack.have.get(gamestate)

        if idx  == -1 and gamestate == WEAPON:
            return self._place_current_weapon()
        
        if not backpack: 
            return True
        
        if not (0 <= idx < len(backpack)):
            return False
        
        backpack[idx], backpack[-1] = backpack[-1], backpack[idx]
        item = backpack.pop()
        if gamestate == FOOD:
            self._use_food(item)
        elif gamestate == POTION:
            self._use_potion(item)
        elif gamestate == SCROLL:
            self._use_scroll(item, 'scrolls_read')
        else:
            self._use_weapon(item)
        return True

    def update(self):
        list_to_del = []
        for k, v in self._permanent_items.items():
            self._permanent_items[k] -= 1
            if v == 1:
                list_to_del.append(k)
                t, power = k
                setattr(self, t, getattr(self, t) - power)
        for k in list_to_del:
            del self._permanent_items[k]
        # sys.stdout.write(f'\033[{53};{1}H\033[2K{self._permanent_items}')

    def _use_food(self, item:Item):
        if self.health + item.power < self.max_health:
            power = item.power
        else:
            power = self.max_health - self.health
        self.health += power
        self._nav.add_statistics('food_eaten')
        self._nav.add_statistics('health_added', power)

    def _use_potion(self, item:Item):
        self._permanent_items[(item.type, item.power)] = item.duration + 1
        self._use_scroll(item, 'potions_drunk')

    def _use_scroll(self, item:Item, info):
        setattr(self, item.type, getattr(self, item.type) + item.power)
        if item.type == 'max_health':
            value = getattr(self, 'max_health') - getattr(self, 'health')
            self._nav.add_statistics('health_added', value)
            setattr(self, 'health', getattr(self, 'max_health'))
        self._nav.add_statistics(info)

    @property
    def weapon(self):
        return max(self.current_weapon.power, self.backpack.weapon)

    def _use_weapon(self, item:Item):
        if self.current_weapon.power:
            self._drop_weapon()
        self.current_weapon = item

    def __repr__(self):
        return repr({k: v for k, v in self.__dict__.items() if not k.startswith('_')})
    
#     + сокровища (имеют стоимость, накапливаются и влияют на итоговый рейтинг, 
# можно получить только при победе над монстром);
#   + еда (восстанавливает здоровье на некоторую величину);
#   + эликсиры (временно повышают одну из характеристик: ловкость, силу, максимальное здоровье);
#   + свитки (постоянно повышают одну из характеристик: ловкость, силу, максимальное здоровье);
#   + оружие (имеют характеристику силы, при использовании оружия меняется формула вычисления наносимого урона).
# Ключ (key): & (для дополнительного задания)

if __name__ == '__main__':
    print(Player().__dict__)