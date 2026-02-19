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

class Backpack:

    def __init__(self, data=None):
        self.have = dict((k, []) for k in ITEMS)
        if isinstance(data, dict):
            self._init_from_dict(data)

    def _init_from_dict(self, data:dict):
        for k, v in data.items():
            if k in ITEMS and len(v) < CAPACITY:
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

class Item:
    def __init__(self, data, level=0):
        if isinstance(data, str):
            self._init_new_item(data, level)
        elif isinstance(data, dict):
            self._init_from_dict(data)
        else:
            raise TypeError(f"{self.__class__.__name__}._init_ {type(data)}")

    def _init_from_dict(self, data:dict):
        if 'id' in data:
            for k, v in data.items():
                setattr(self, k, v)
        else:
            raise AttributeError(f"{self.__class__.__name__}._init_from_dict")

    def _init_new_item(self, id, level=0):
        self.id = id  
        if id == WEAPON:
            self.type = choice(['spear', 'sword', 'knife'])
            self.power = randint(1 + level // 3, 5 + level // 2)
        elif id == FOOD:
            self.type = choice(['bread', 'honey', 'steak', 'water'])
            self.power = randint(3, 8) + level // 2
        elif id == POTION: # tempopary
            self.type = choice(['strength', 'dexterity', 'max_health'])
            self.power = randint(1, 3) + level // 4
            self.duration = 15 + level * 2
        elif id == SCROLL: # permanent
            self.type = choice(['strength', 'dexterity', 'max_health'])
            self.power = randint(1, 2) + level // 5

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
    def __repr__(self):
        return str(self.to_dict())

class Entity:
    def __init__(self, id = None, pos=None):
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


class Character(Entity):
    def __init__(self, id = None, nav:Navigator=None, pos=None ):
        super().__init__(id, pos)
        self._nav = nav
        self.dexterity= 10 # Ловкость (dexterity) влияет на шанс попадания: hit_chance = a.dex / (a.dex + d.dex).
        self.strength = 10 # Сила (strength) — базовый урон: damage = max(1, a.str - d.str // 3) ???
        self.health = 20

    def attack(self, target):
        random_value = randint(1, self.dexterity + target.dexterity)
        if random_value <= self.dexterity:
            damage = self.strength - target.strength
            damage = 1 if damage < 1 else damage
            target.health -= damage
            self._nav.add_statistics('hits_taken')
            self._nav.add_statistics('health_used', -damage)
            
        
class Player(Character):
    def __init__(self, data=None, nav:Navigator=None):
        super().__init__(PLAYER, nav)
        self.max_health = 30
        self.backpack = None
        self._permanent_items = {}
        self._free_hands = Item(WEAPON, 0)
        self._free_hands.power = 0
        self.current_weapon = self._free_hands
        if data is None:
            self.backpack = Backpack()
        else:
            self._init_from_dict(data)

    def _init_from_dict(self, data:dict):
        for k, v in data.items():
            if hasattr(self, k):
                if not isinstance(k, dict):
                    setattr(self, k, v)
            else:
                raise AttributeError(f"{self.__class__.__name__}._init_from_dict {k}")
            
        self.backpack = Backpack(data['backpack'])
        self.current_weapon = Item(data['current_weapon'])
        self._permanent_items = {(i, j):k for i, j, k in data['_permanent_items']}

    def attack(self, target):
        random_value = randint(1, self.dexterity + target.dexterity)
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
        'max_health': 30, 
        'backpack': self.backpack.to_dict(),
        '_permanent_items': [[*k, v] for k, v in self._permanent_items.items()]
    }
        return d

    def get_item(self, item:Item):
        if item.id == FOOD:
            self._nav.add_statistics('health_added', item.power)
        elif item.id != WEAPON:
            t = item.type.split('_')[-1] + '_added'
            self._nav.add_statistics(t, item.power)
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
                type, power = k
                setattr(self, type, getattr(self, type) - power)
        for k in list_to_del:
            del self._permanent_items[k]
        # sys.stdout.write(f'\033[{53};{1}H\033[2K{self._permanent_items}')

    def _use_food(self, item:Item):
        if self.health + item.power < self.max_health:
            self.health += item.power
        else:
            self.health = self.max_health
        self._nav.add_statistics('food_eaten')

    def _use_potion(self, item:Item):
        self._permanent_items[(item.type, item.power)] = item.duration + 1
        self._use_scroll(item, 'potions_drunk')

    def _use_scroll(self, item:Item, info):
        power = getattr(self, item.type) + item.power
        setattr(self, item.type, power)
        t = item.type.split('_')[-1] + '_used'
        if item.type == 'max_health':
            setattr(self, 'health', getattr(self, 'max_health'))
        self._nav.add_statistics(info)
        self._nav.add_statistics(t, -power)

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