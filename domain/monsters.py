from common.characters import *
from .entity import Character, Entity
from random import randint, choice
from .bresenham import Bresenham
from common.playground import GROUND

class Monster(Character):
    def __init__(self, id, pos, r):
        super().__init__(id, pos)
        self.room = r
        self._patrol_moves = ((1, 0), (0, 1), (-1, 0), (0, -1))
        self._go_home_moves = self._patrol_moves

    def set_features(self, data, nav):
        for k, v in data.items():
            setattr(self, k, v)
        self._nav = nav

    def set_init_values(self, k):
        for value in ('health', 'hostility', 'dexterity', 'strength'):
            val = randint(getattr(self, 'MIN_' + value), getattr(self, 'MAX_' + value))
            val = round(val * k)
            setattr(self, value, val)

    def drop_treasure(self):
        return randint(1, self.hostility + self.strength + self.dexterity+ self.MAX_health)


    def _patrol(self, player=None):
        idx = randint(0, len(self._patrol_moves) - 1)
        pos = (self.pos[0] + self._patrol_moves[idx][0], self.pos[1] + self._patrol_moves[idx][1])
        if self._nav.valid_for_monsters(pos) and self._nav.room_number(pos) == self.room:
            self._pos = pos


    def attack(self, target):
        random_value = randint(1, self.dexterity + target.dexterity)
        if random_value <= self.dexterity:
            damage = self.strength - target.strength
            damage = 1 if damage < 1 else damage
            target.health -= damage
            self._nav.add_statistics('hits_taken')
            self._nav.add_statistics('health_used', damage)
            self._nav.add_danger(f'{self.__class__.__name__} hit you!')
        else:
            self._nav.add_danger(f'{self.__class__.__name__} tried to hit you and missed!')

    def move(self, player):
        pos = self._step_to_player(player)
        if pos is not None:
            if pos != player.pos:
                self._nav.add_danger(f'{self.__class__.__name__} sees you! It\'s health is {self.health}.')
                if self._nav.valid_for_monsters(pos):
                    self.pos = pos
            else:
                self.attack(player)
        else:
            if self.room != self._nav.room_number(self.pos):
                self._go_home()
            else:
                self._patrol(player)

    def _step_to_player(self, player):
        y0, x0 = self.pos
        y1, x1 = player.pos
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        if max(dy, dx) > self.hostility:
            return None
        return Bresenham().find_path(self.pos, player.pos, self._nav)


    def _go_home(self):
        stack = [self.pos]
        path = {self.pos: None}
        while stack:
            new_stack = []
            for pos in stack:
                for move in self._go_home_moves:
                    new_pos = (pos[0] + move[0], pos[1]+ move[1])
                    if new_pos not in path and self._nav.valid(pos):
                        room = self._nav.room_number(new_pos)
                        if self.room == room:
                            while pos != self.pos:
                                new_pos = pos
                                pos = path[pos]
                            if self._nav.valid(new_pos):
                                self._pos = new_pos
                            return
                        new_stack.append(new_pos)
                        path[new_pos] = pos
            stack = new_stack

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
        'class': self.__class__.__name__,
        'id': self.id,
        'pos': self.pos, 
        'room': self.room,
        'hostility': self.hostility,
        'dexterity': self.dexterity, 
        'strength': self.strength, 
        'health': self.health
        }
    

class Snake(Monster):
    MIN_health = 4
    MAX_health = 6
    MIN_strength = 2
    MAX_strength = 3
    MIN_dexterity = 6
    MAX_dexterity = 8
    MIN_hostility = 5
    MAX_hostility = 6

    def __init__(self, pos=None, r=None):
        super().__init__(SNAKE, pos, r)
        self._patrol_moves = ((1, 1), (-1, 1), (1, -1), (-1, -1))
        # self._go_home_moves = ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))

  # Змей-маг (отображение: белая s): очень высокая ловкость. 
  # Ходит по карте по диагонали, постоянно меняя сторону. 
  # У каждой успешной атаки есть вероятность «усыпить» игрока на один ход. 
  # Высокая враждебность.

    def attack(self, target):
        random_value = randint(1, self.dexterity + target.dexterity)
        if random_value <= self.dexterity:
            target.can_move = False
            self._nav.add_statistics('hits_taken')
            self._nav.add_danger(f'The Snake put you to sleep for 1 turn.')
        else:
            self._nav.add_danger(f'The Snake tried to hit you and missed!')


class Ogre(Monster):

    MIN_health = 15
    MAX_health = 18
    MIN_strength = 5
    MAX_strength = 6
    MIN_dexterity = 1
    MAX_dexterity = 2
    MIN_hostility = 4
    MAX_hostility = 5

    def __init__(self, pos=None, r=None):
        super().__init__(OGRE, pos, r)
        self.can_attack = True
        self._patrol_moves = ((1, 0), (0, 1), (-1, 0), (0, -1), 
                              (2, 0), (0, 2), (-2, 0), (0, -2)
                              )
# Огр (отображение: желтый O): ходит по комнате на две клетки. 
# Очень высокая сила и здоровье, но после каждой атаки отдыхает один ход, 
# затем гарантированно контратакует; низкая ловкость; средняя враждебность.

    def attack(self, target):
        if self.can_attack:
            damage = self.strength - target.strength
            damage = 1 if damage < 1 else damage
            target.health -= damage
            self._nav.add_statistics('hits_taken')
            self._nav.add_statistics('health_used', damage)
            self._nav.add_danger(f'Ogre hit you!')
            self.can_attack = False
        else:
            self.can_attack = True
            self._nav.add_danger(f'Ogre rests.')



class Vampire(Monster):

    MIN_health = 10
    MAX_health = 12
    MIN_strength = 4
    MAX_strength = 5
    MIN_dexterity = 5
    MAX_dexterity = 6
    MIN_hostility = 5
    MAX_hostility = 6

    def __init__(self, pos=None, r=None):
        super().__init__(VAMPIRE, pos, r)
        self.first_hit = False


# Вампир (отображение: красная v): высокая ловкость, враждебность и здоровье; 
# средняя сила. Отнимает некоторое количество максимального уровня здоровья 
# игроку при успешной атаке. Первый удар по вампиру — всегда промах. 
    def attack(self, target):
        random_value = randint(1, self.dexterity + target.dexterity)
        if random_value <= self.dexterity:
            damage = 1
            target.max_health -= damage
            if target.health > target.max_health:
                target.health = target.max_health
            self._nav.add_statistics('hits_taken')
            self._nav.add_statistics('health_used', damage)
            self._nav.add_danger(f'{self.id} hit you!')
        else:
            self._nav.add_danger(f'{self.id} tried to hit you and missed!')


class Ghost(Monster):

    MIN_health = 5
    MAX_health = 7
    MIN_strength = 2
    MAX_strength = 3
    MIN_dexterity = 7
    MAX_dexterity = 8
    MIN_hostility = 3
    MAX_hostility = 4

    def __init__(self, pos=None, r=None):
        super().__init__(GHOST, pos, r)
        self.attacked = False
# Привидение (отображение: белый g): высокая ловкость; низкая сила, враждебность и здоровье. 
# Постоянно телепортируется по комнате и периодически становится невидимым, 
# пока игрок не вступил в бой.

    def move(self, player):
        super().move(player)
        pos = self._pos
        if not self.attacked:
            if randint(0, 1):
                self.id = GHOST
            else:
                self.id = self._nav.layout(pos)
                if self.id == GROUND:
                    value = self._nav.visible(pos)
                    if isinstance(value, Entity):
                        self.id = value.id
                    else:
                        self.id = value
            
    def _patrol(self, player):
        idx = randint(0, len(self._patrol_moves) - 1)
        pos = self._patrol_moves[idx]
        if self._nav.valid_for_monsters(pos) and pos != player.pos:
            self._pos = pos



class Zombie(Monster):

    MIN_health = 8
    MAX_health = 12
    MIN_strength = 3
    MAX_strength = 5
    MIN_dexterity = 1
    MAX_dexterity = 2
    MIN_hostility = 3
    MAX_hostility = 4

    def __init__(self, pos=None, r=None):
        super().__init__(ZOMBIE, pos, r)
    # Зомби (отображение: зеленый z): низкая ловкость; 
    # средняя сила, враждебность; высокое здоровье.


class Mimic(Monster):
# - Добавь в игру противника Мимик (белая m), который имитирует предметы. 
# Высокая ловкость, низкая сила, высокое здоровье и низкая враждебность. 
    MIN_health = 8
    MAX_health = 12
    MIN_strength = 2
    MAX_strength = 3
    # ловкость
    MIN_dexterity = 7
    MAX_dexterity = 8
    # враждебность
    MIN_hostility = 3
    MAX_hostility = 4

    def __init__(self, pos=None, r=None):
        char = choice([FOOD, POTION, SCROLL, WEAPON])
        self._active = False
        super().__init__(char, pos, r)
        
    def activate(self):
        self._active = True
        self.id = MIMIC
        
    def move(self, player):
        if not self._active:
            return
        super().move(player)

    def _patrol(self):
        if not self._active:
            return
        super()._patrol()

    def to_dict(self):
        d = super().to_dict()
        d['_active'] = self._active
        return d

    @property
    def active(self):
        return self._active


