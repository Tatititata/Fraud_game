
from common.characters import ITEMS

class Adapter:
    def __init__(self):
        self.level_reached = [1]
        self.K_monster_quantity = [1]
        self.K_monster_strength = [1]
        self.K_items_quantity = [1]
        self.K_items_power = [1]

  
    def update(self, model):
        with open('adapter.txt', 'a') as f:
            f.write(f'\nmodel.full_statistics\n')
            for k, v in model.full_statistics.items():
                if not hasattr(self, k):
                    setattr(self, k, [])
                l = getattr(self, k).append(v)
                f.write(f'{k} - {v}\n')
            f.write(f'\n')

        monsters_killed = self.monsters_killed[-1]
        monsters_left = self.monsters_left[-1]
        hits_dealt = self.hits_dealt[-1]
        hits_taken = self.hits_taken[-1]
        healed = self.health_added[-1]
        damage = self.health_used[-1]
        fight_success = (monsters_killed / (monsters_left + 1)) * (hits_dealt / (hits_taken + 1))

        strength = self.strength[-1] + self.weapon[-1]
        dexterity = self.dexterity[-1]
        level_reached = self.level_reached[-1]
        progress = (strength + dexterity) / (level_reached * 2)
        max_health = self.max_health[-1]

        # self.K_monster_quantity.append(1 + (level_reached / 20) + (fight_success * 0.2))
        # self.K_monster_strength.append(1 + (level_reached / 20) + (health * 0.2) + (strength / 20) + (dexterity / 20))
        # self.K_items_quantity.append(1 - (progress * 0.2))
        # self.K_items_power.append(1 + ((damage - healed) / (damage + healed + 1)))

        self.K_monster_quantity.append(1 + (level_reached / 15) + (fight_success * 0.5))
        self.K_monster_strength.append(1 + (level_reached / 12) + ((damage - healed) / max_health) * 0.8)
        self.K_items_quantity.append(max(0.3, 1 + (level_reached / 10) - (progress * 0.2)))
        self.K_items_power.append(1 + (level_reached / 15) + ((damage - healed) / max_health) * 0.5)



        
    @property
    def data(self):
        with open('adapter.txt', 'a') as f:
            f.write(f'\nadapter \n')
            for k, v in {k: v for k, v in self.__dict__.items() if not k.startswith('_')}.items():
                f.write(f'{k} - {v}\n')
        return  {k: v[-1] for k, v in self.__dict__.items() if not k.startswith('_')}






