
from common.characters import *
from common.playground import *
from common.constants import *
from common.drawing_const import *
from .drawing import Draw



class FlatRender:


    def __init__(self, parent, model):
        self._out = parent._out
        self._parent = parent
        self._model = model
        self._old_visible = set()
        self._render_game(self._model.first_screen)
        
        self.update()
        
    def update(self):
        
        self._render_game(self._model.data_for_rendering)

    def _render_game(self, data:set):
        self._old_visible -= data
        for pos in self._old_visible:
            y, x = pos
            char = self._model.layout(pos)
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{char}')

        self._old_visible = data
        for pos in self._old_visible:
            obj = self._model.visible(pos)
            y, x = pos
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
            char = self._parent.converter(obj)
            self._out.write(char)



    if __name__ == "__main__":
        pass