
from common.characters import ITEMS

class Adapter:
    def __init__(self):
        self.level_reached = [1]
        self.K_monster_quantity = [1]
        self.K_monster_strength = [1]
        self.K_items_quantity = [1]
        self.K_items_power = [1]

  
    def update(self, model):
        with open('adapter.txt', 'w') as f:
            f.write(f'\nmodel.full_statistics\n')
            for k, v in model.full_statistics.items():
                if not hasattr(self, k):
                    setattr(self, k, [])
                l = getattr(self, k).append(v)
                f.write(f'{k} - {v}\n')
            f.write(f'\n')

        m_killed = self.monsters_killed[-1]
        m_left = self.monsters_left[-1]
        m_total = m_killed + m_left
        kill_ratio = (m_killed + 1) / (m_total + 1)

        path = self.path_length[-1]
        steps = self.steps[-1]    
        damage = self.health_used[-1]
        health = self.health[-1]
        healed = self.health_added[-1]
        health_loss_per_step = damage / steps

        if damage == 0 or self.hits_taken[-1] == 0:
            k = self.K_monster_strength[-1] * 1.2
            self.K_monster_strength.append(k)
            k = self.K_monster_quantity[-1] * 1.2
            self.K_monster_quantity.append(k)

        elif kill_ratio < 0.3 and health_loss_per_step < 0.02:
            k = self.K_monster_strength[-1] * 1.2
            self.K_monster_strength.append(k)
            k = self.K_monster_quantity[-1] * 1.3
            self.K_monster_quantity.append(k)

        elif kill_ratio < 0.5 and damage >= health:
            k = self.K_monster_strength[-1]
            self.K_monster_strength.append(k)
            k = self.K_monster_quantity[-1] * 0.85
            self.K_monster_quantity.append(k)

        elif steps / path > 1.5 and kill_ratio > 0.5:
            k = self.K_monster_strength[-1] * 1.15 
            self.K_monster_strength.append(k)
            k = self.K_monster_quantity[-1] * 1.1  
            self.K_monster_quantity.append(k)

        elif steps / path > 1.5 and kill_ratio <= 0.5:
            k = self.K_monster_strength[-1]
            self.K_monster_strength.append(k)
            k = self.K_monster_quantity[-1] * 1.1
            self.K_monster_quantity.append(k)
            
        else:
            k = self.K_monster_strength[-1]
            self.K_monster_strength.append(k)
            k = self.K_monster_quantity[-1]
            self.K_monster_quantity.append(k)         

        K_items_quantity = ((healed + 1) / (damage + 1)) * (steps / path)
        if K_items_quantity > 1.2:
            k = self.K_items_quantity[-1] * 0.8
            self.K_items_quantity.append(k)
        elif K_items_quantity < 0.5:
            k = self.K_items_quantity[-1] * 1.2
            self.K_items_quantity.append(k)
        else:
            k = self.K_items_quantity[-1]
            self.K_items_quantity.append(k)

        K_items_power = (healed + 1) / (damage + 1)
        if K_items_power > 0.8:
            k = self.K_items_power[-1] * 0.8
            self.K_items_power.append(k)
        elif K_items_power < 0.3:
            k = self.K_items_power[-1] * 1.2
            self.K_items_power.append(k)
        else:
            k = self.K_items_power[-1]
            self.K_items_power.append(k)
        
        if m_left == 0:
            self.K_items_quantity[-1] /= 1.2
            self.K_items_power[-1] /= 1.2
            self.K_monster_strength[-1] *= 1.2
            self.K_monster_quantity[-1] *= 1.2


    @property
    def data(self):
        with open('adapter.txt', 'a') as f:
            f.write(f'\nadapter \n')
            for k, v in {k: v for k, v in self.__dict__.items() if not k.startswith('_')}.items():
                f.write(f'{k} - {v}\n')
        return  {k: v[-1] for k, v in self.__dict__.items() if not k.startswith('_')}






