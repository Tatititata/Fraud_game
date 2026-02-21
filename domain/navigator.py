class Navigator:

    def __init__(self, model):
        self._model = model

    def place_entity(self, pos, e):
        return self._model.place_entity(pos, e)

    def room_number(self, pos):
        return self._model.room_number(pos)
    
    def walkable(self, pos):
        return self._model.walkable(pos)

    def place_weapon(self, pos, weapon):
        return self._model.place_weapon(pos, weapon)
    
    def add_statistics(self, key:str, value:int=1):
        return self._model.add_statistics(key, value)
    
    def valid(self, pos):
        return self._model.valid(pos)
    