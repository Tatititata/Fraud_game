
from common.characters import *
from common.playground import *
from common.constants import *
from common.drawing_const import *
from .drawing import Draw
from .flat_render import FlatRender
from .raycasting import RayCasting
from .menu_render import MenuRender



class MainRender:

    _renders = [FlatRender, RayCasting]

    def __init__(self, out):
        self._mode = 0
        self._out = out
        Draw().rectangle(self._out, 0, 0, HEIGHT, WIDTH)
        self._menu_render = MenuRender(self._out)
        self._show_start_game_menu()
        self._out.flush()

    def set_up(self, model):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._model = model
        self._menu_render.set_up(model)
        self._render = self._renders[self._mode](self._out, model)
        self._show_level()
        self._out.flush()

    def show_can_not_load_game_screen(self):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._out.write(f'\033[3;5HNo saved game')
        self._out.write(f'\033[4;5HPress any key to start new game')
        self._out.flush()

    def _show_start_game_menu(self):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._out.write(f'\033[5;5HPress \'l\' to load saved game.')
        self._out.write(f'\033[6;5HPress \'esc\' to quit.')
        self._out.write(f'\033[7;5HPress any other key to start new game.')
        # self._out.flush()

    def show_gameover_menu(self):
        self._show_start_game_menu()
        self._out.write(f'\033[3;5Hgame over')


    def _show_level(self):
        self._out.write(f'\033[{SHIFT};{45+SHIFT}H Level {self._model.level} ')

    def show_win_screen(self):
        self._out.write('\033[2J\033[H')
        self._out.write(f'\033[3;3HYOU WIN')
        self._out.write(f'\033[4;3Hpress any key')
        self._out.flush()

    def show_records(self, records):
        self._menu_render.update_records(records)

    def update(self):
        if self._model.gamestate:
            self._render.update()
        else:
            self.show_gameover_menu()
        self._out.flush()

    @property
    def out(self):
        return self._out
    
    @property
    def menu_height(self):
        return INFO_MENU_HEIGHT - 4

    @property
    def mode(self):
        return self._mode

    def change_mode(self):
        self._mode = not self._mode
        self._render = self._renders[self._mode](self._out, self._model)


    if __name__ == "__main__":
        pass