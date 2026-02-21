
from common.characters import ITEMS

class Adapter:
    def __init__(self):
        self.level_reached = 1
        self.K_total = 1
        self.K_monster_quantity = 1
        self.K_monster_strength = 1
        self.K_items_quantity = 1
        self.K_items_power = 1

  
    def update(self, model):
        with open('adapter.txt', 'a') as f:
            f.write(f'{model.full_statistics}\n')
            for k, v in model.full_statistics.items():
                f.write(f'{k} - {v}\n')

        
        
    @property
    def data(self):
        with open('adapter.txt', 'a') as f:
            f.write(f'adapter \n')
            for k, v in {k: v for k, v in self.__dict__.items() if not k.startswith('_')}.items():
                f.write(f'{k} - {v}\n')
        return  {k: v for k, v in self.__dict__.items() if not k.startswith('_')}






