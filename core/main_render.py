
from common.characters import *
from common.playground import *
from common.constants import *
from common.drawing_const import *
from .drawing import Draw
from .flat_render import FlatRender
from .raycasting import RayCasting



class MainRender:

    _renders = [FlatRender, RayCasting]


    def __init__(self, out):
        self._mode = 0
        self._out = out
        Draw().rectangle(self._out, 0, 0, HEIGHT, WIDTH)
        self._out.write('\033[?25l')  # hide cursor
        self.show_start_game_menu()
        self.show_game_menu()
        self._out.flush()

    def set_up(self, model):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._model = model
        self._render = self._renders[self._mode](self._out, model)
        self._show_level()

    def show_game_menu(self):
        Draw().rectangle(self._out, INFO_MENU_POS_Y, INFO_MENU_POS_X, INFO_MENU_HEIGHT, INFO_MENU_WIDTH)
        self._draw_game_info()
        # self._out.flush()       

    def show_can_not_load_game_screen(self):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._out.write(f'\033[3;5HNo saved game')
        self._out.write(f'\033[5;5HPress any key to start new game')
        self._out.flush()

    def show_start_game_menu(self):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._out.write(f'\033[3;5HPress \'l\' to load saved game.')
        self._out.write(f'\033[4;5HPress \'esc\' to quit.')
        self._out.write(f'\033[5;5HPress any other key to start new game.')
        # self._out.flush()

    def show_gameover_menu(self):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._out.write(f'\033[3;3Hgameover menu')
        self._out.write(f'\033[4;3Hpress any key')
        self._out.flush()

    def _show_level(self):
        self._out.write(f'\033[{SHIFT};{45+SHIFT}H Level {self._model.level} ')

    def show_win_screen(self):
        self._out.write('\033[2J\033[H')
        self._out.write(f'\033[3;3HYOU WIN')
        self._out.write(f'\033[4;3Hpress any key')
        self._out.flush()

    def show_records(self, records):
        Draw().rectangle(self._out, REC_MENU_POS_Y, REC_MENU_POS_X, REC_MENU_HEIGHT, REC_MENU_WIDTH)
        y = REC_MENU_POS_Y + 1
        x = REC_MENU_POS_X + 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('=== BEST RECORDS ==='.center(INFO_MENU_WIDTH - 2))
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('treasure      level'.center(INFO_MENU_WIDTH - 2))
        y += 1
        for t, l in records.data[:INFO_MENU_HEIGHT - 4]:
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
            self._out.write(f'{t:<8d} - - - {l:2d}'.center(INFO_MENU_WIDTH - 2))
            y += 1
        self._out.flush()

    def _draw_game_info(self):

        y, x = INFO_MENU_POS_Y + 1, INFO_MENU_POS_X + 2

        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write(' === GAME  INFO ===')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('food (j) ------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('potion (k) ----- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('scroll (u) ----- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('weapon (h) ----- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('current weapon - ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('dexterity ------ ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('strength ------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('health --------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('max health ----- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('keys (m) ------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('treasure ------- ')

    # def _clear_game_field(self):
    #     for y in range(HEIGHT - 2):
    #         for x in range(WIDTH - 2):
    #             self._out.write(f'\033[{y + SHIFT + 1};{x + SHIFT + 1}H{GROUND}')

    def update(self):
        self._render.update()

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