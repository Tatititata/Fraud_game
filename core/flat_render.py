
from common.characters import *
from common.playground import *
from common.constants import *
from common.drawing_const import *
from .drawing import Draw


class FlatRender:


    def __init__(self, parent, model):
        self._out = parent._out
        self._symbols = parent._symbols
        self._model = model
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._old_visible = set()
        self._render_game(self._model.first_screen)
        
        self.update()
        
    def update(self):
        if self._model.gamestate == NORMAL:
            self._render_game(self._model.data_for_rendering)

    def _render_game(self, data:set):
        self._old_visible -= data
        for pos in self._old_visible:
            y, x = pos
            char = self._model.layout(pos)
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{char}')

        self._old_visible = data
        for pos in self._old_visible:
            y, x = pos
            char = self._model.visible(pos)
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{self._symbols.get(char, char)}')

    if __name__ == "__main__":
        pass