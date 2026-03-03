
from common.characters import *
from common.playground import *
from common.constants import *
from common.drawing_const import *
from .drawing import Draw


class FlatRender:
    _symbols = {
        PLAYER : '\033[1;37m@\033[0m',
        ZOMBIE : '\033[1;32mZ\033[0m',
        VAMPIRE : '\033[1;31mV\033[0m',
        GHOST : '\033[1;37mG\033[0m',
        OGRE : '\033[1;33mO\033[0m',
        SNAKE : '\033[1;37mS\033[0m',
        TREASURE : '\033[1;37m*\033[0m',
        FOOD : '\033[1;37m%\033[0m',
        POTION : '\033[1;37m!\033[0m',
        SCROLL : '\033[1;37m?\033[0m',
        WEAPON : '\033[1;37m)\033[0m',
        FLOOR : '\033[2m·\033[0m',
        MIMIC : '\033[1;37mM\033[0m',
        }
    
    # _positions = dict(zip(FULL_BACKPACK, range(len(FULL_BACKPACK))))

    def __init__(self, out, model):
        self._out = out
        self._model = model
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._render_game(self._model.first_screen)
        self.update()
        
    def update(self):
        if self._model.gamestate == NORMAL:
            self._render_game(self._model.data_for_rendering)

    def _render_game(self, data_for_rendering:dict):
        for (y, x), char in data_for_rendering.items():
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{self._symbols.get(char, char)}')






    if __name__ == "__main__":
        pass