from common.characters import *
from .navigator import Navigator
from random import randint, choice
from .entity import Character, Item, Backpack
from .monsters import Vampire, Ghost

class Player(Character):

    def __init__(self, data=None, nav:Navigator=None):
        super().__init__(PLAYER, None, nav)
        self._permanent_items = {}
        self._free_hands = Item((WEAPON, (0,0), 1))
        self._free_hands.power = 0
        self.current_weapon = self._free_hands
        self.angle = -1/2
        self.can_move = True

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
        self.facing = data.get('facing', 0)

    def attack(self, target):
        if isinstance(target, Vampire) and not target.first_hit:
            target.first_hit = True
            return
        if isinstance(target, Ghost):
            target.id = GHOST
            target.attacked = True
        random_value = randint(1, self.dexterity + target.dexterity)
        if random_value <= self.dexterity:
            damage = self.strength + self.current_weapon.power - target.strength
            damage = 1 if damage < 1 else damage
            target.health -= damage
            self._nav.add_statistics('hits_dealt')
            if target.health > 0:
                self._nav.add_danger(f'You hit {target.__class__.__name__} with damage {damage}! It\'s health is now {target.health}.')
            else:
                self._nav.add_danger(f'You killed {target.__class__.__name__}!')
        else:
            self._nav.add_danger(f'You tried to hit {target.__class__.__name__} and missed!')
         
    def to_dict(self):
        d = {
        'pos': self.pos, 
        'dexterity': self.dexterity, 
        'strength': self.strength, 
        'health': self.health, 
        'current_weapon': self.current_weapon.to_dict(), 
        'max_health': self.max_health, 
        'backpack': self.backpack.to_dict(),
        '_permanent_items': [[*k, v] for k, v in self._permanent_items.items()],
        'angle': self.angle
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
        if not isinstance(idx, str):
            return False
        idx = ord(idx) - 49 # idx = digit 1-10
        backpack = self.backpack.have.get(gamestate)

        if idx  == -1 and gamestate == WEAPON:
            return self._place_current_weapon()
        
        if not backpack: 
            return False
        
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
        elif gamestate == KEY:
            if not self._nav.open_door(item):
                self.get_item(item)
            return False # ??? may be true???
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