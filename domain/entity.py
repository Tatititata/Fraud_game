from common.constants import *
# from domain.model import Model
from random import randint
# from collections import deque
import sys

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

class Entity:
    def __init__(self, pos):
        self.pos = pos
        self.health = 1 # 0 = dead
        self.dexterity = 5
        self.strength = 10


class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos)
        self.id = PLAYER
        self.max_health = 10
        self.weapon = 1
        self.backpack = Backpack()



class Monster(Entity):
    def __init__(self, pos, r, id):
        super().__init__(pos)
        self._count = 0
        self.id = id
        self.room = r
        self.valid_moves = ((1, 0), (0, 1), (-1, 0), (0, -1))

    def _patrol(self, model):
        idx = randint(0, len(self.valid_moves) - 1)
        pos = (self.pos[0] + self.valid_moves[idx][0], self.pos[1] + self.valid_moves[idx][1])
        model.place_entity(pos, self)

    def move(self, model, player):
        if self._player_visible(model, player):
            path = self._get_path_to_player(player)
            self._attack(path)
        else:
            if self.room != model.room_number(self.pos):
                self._go_home(model)
            else:
                self._patrol(model)

    def _go_home(self, model):
        stack = [self.pos]
        path = {self.pos: None}
        while True:
            new_stack = []
            for pos in stack:
                for move in self.valid_moves:
                    new_pos = (pos[0] + move[0], pos[1]+ move[1])
                    room = model.room_number(new_pos)
                    if room is not None:
                        if self.room == room:
                            sys.stdout.write(f'\033[{1 + self._count};{103}H{new_pos}, {path}')
                            self._count += 1
                            while pos != self.pos:
                                new_pos = pos
                                pos = path[pos]
                            model.place_entity(new_pos, self)
                            return
                        new_stack.append(new_pos)
                        path[new_pos] = pos
            stack = new_stack

    def _player_visible(self, model, player): 
        y0, x0 = self.pos
        y1, x1 = player.pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        x, y = x0, y0
        if dx > dy:
            d = 2*dy - dx
            while True: 
                x += sx
                if y == y1 and x == x1:
                    return True
                if not model.walkable((y, x)):
                    return False          
                if d >= 0:
                    y += sy      
                    if y == y1 and x == x1:
                        return True
                    d -= 2*dx
                    if not model.walkable((y, x)):
                        return False
                d += 2*dy        
        else:        
            d = 2*dx - dy
            while True:
                y += sy       
                if y == y1 and x == x1:
                    return True   
                if not model.walkable((y, x)):
                    return False
                if d >= 0:
                    x += sx  
                    if y == y1 and x == x1:
                        return True   
                    d -= 2*dy  
                    if not model.walkable((y, x)):
                        return False
                d += 2*dx   

    def _get_path_to_player(self, player): 
        y0, x0 = self.pos
        y1, x1 = player.pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        x, y = x0, y0
        path = []
        if dx > dy:
            d = 2*dy - dx
            while True: 
                x += sx
                if y == y1 and x == x1:
                    return path         
                path.append((y, x))
                if d >= 0:
                    y += sy      
                    if y == y1 and x == x1:
                        return path
                    d -= 2*dx
                    path.append((y, x))
                d += 2*dy                        
        else:        
            d = 2*dx - dy
            while True:
                y += sy       
                if y == y1 and x == x1:
                    return path   
                path.append((y, x))
                if d >= 0:
                    x += sx  
                    if y == y1 and x == x1:
                        return path   
                    d -= 2*dy  
                    path.append((y, x))
                d += 2*dx 

    def _attack(self, path):
        pass





class Snake(Monster):
    def __init__(self, pos, r):
        super().__init__(pos, r, SNAKE)

        
class Ogre(Monster):
    def __init__(self, pos, r, ):
        super().__init__(pos, r, OGRE)


class Vampire(Monster):
    def __init__(self, pos, r, ):
        super().__init__(pos, r, VAMPIRE)


class Ghost(Monster):
    def __init__(self, pos, r, ):
        super().__init__(pos, r, GHOST)


class Zombie(Monster):
    def __init__(self, pos, r, ):
        super().__init__(pos, r, ZOMBIE)


class Backpack:

#     + сокровища (имеют стоимость, накапливаются и влияют на итоговый рейтинг, 
# можно получить только при победе над монстром);
#   + еда (восстанавливает здоровье на некоторую величину);
#   + эликсиры (временно повышают одну из характеристик: ловкость, силу, максимальное здоровье);
#   + свитки (постоянно повышают одну из характеристик: ловкость, силу, максимальное здоровье);
#   + оружие (имеют характеристику силы, при использовании оружия меняется формула вычисления наносимого урона).
    
    def __init__(self):
        self.capacity = 9
        self.treasure = 0
        self.food = 1
        self.elixir = 1
        self.scroll = 1
        self.weapon = {}




if __name__ == '__main__':
    print(Player().__dict__)