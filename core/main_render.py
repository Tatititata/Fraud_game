
from common.characters import *
from common.playground import *
from common.constants import *
from common.drawing_const import *
from .drawing import Draw
from .flat_render import FlatRender
from .raycasting import RayCasting
from .menu_render import MenuRender
from domain.entity import Character, Item, Door



class MainRender:

    _renders = [FlatRender, RayCasting]

    def __init__(self, out):
        self._mode = 0
        self._out = out
        Draw().rectangle(self._out, 0, 0, HEIGHT, WIDTH)
        self._menu_render = MenuRender(self)
        self._show_start_game_menu()
        # self._show_controls()
        self._out.flush()

    def set_up(self, model):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._model = model
        self._menu_render.set_up(self._model)
        self._render = self._renders[self._mode](self, model)
        self._show_level()
        self._out.flush()

    def show_can_not_load_game_screen(self):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._out.write(f'\033[3;5HNo saved game')
        self._out.write(f'\033[4;5HPress any key to start new game')
        self._out.flush()

    def _show_start_game_menu(self):
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._out.write('\033[6;2H')
        self._out.write('===================================='.center(WIDTH - 2))
        self._out.write('\033[7;2H')
        self._out.write('\033[1mCONTROLS\033[0m'.center(WIDTH - 2))
        self._out.write('\033[8;2H')
        self._out.write('===================================='.center(WIDTH - 2))
        self._out.write('\033[10;2H')
        self._out.write('2D VIEW:'.center(WIDTH - 2))
        self._out.write('\033[12;2H')
        self._out.write('\033[1mw\033[0m - move up  '.center(WIDTH - 2))
        self._out.write('\033[13;2H')
        self._out.write('\033[1ms\033[0m - move down'.center(WIDTH - 2))
        self._out.write('\033[14;2H')
        self._out.write('\033[1ma\033[0m - move left'.center(WIDTH - 2))
        self._out.write('\033[15;2H')
        self._out.write('\033[1md\033[0m - move right'.center(WIDTH - 2))
        self._out.write('\033[17;2H')
        self._out.write('------------------------------------'.center(WIDTH - 2))
        self._out.write('\033[18;2H')
        self._out.write('\033[1mF5\033[0m - change view (2D/3D)'.center(WIDTH - 2))
        self._out.write('\033[19;2H')
        self._out.write('------------------------------------'.center(WIDTH - 2))
        self._out.write('\033[21;2H')
        self._out.write('3D VIEW:'.center(WIDTH - 2))
        self._out.write('\033[23;2H')
        self._out.write('\033[1mw\033[0m - move forward  '.center(WIDTH - 2))
        self._out.write('\033[24;2H')
        self._out.write('\033[1ms\033[0m - move backward'.center(WIDTH - 2))
        self._out.write('\033[25;2H')
        self._out.write('\033[1ma\033[0m - rotate left  '.center(WIDTH - 2))
        self._out.write('\033[26;2H')
        self._out.write('\033[1md\033[0m - rotate right  '.center(WIDTH - 2))
        self._out.write('\033[28;2H')
        self._out.write('------------------------------------'.center(WIDTH - 2))
        self._out.write('\033[29;2H')
        self._out.write('\033[1mESC\033[0m - quit'.center(WIDTH - 2))
        self._out.write('\033[30;2H')
        self._out.write('------------------------------------'.center(WIDTH - 2))
        self._out.write('\033[32;2H')
        self._out.write('\033[1ml\033[0m - load saved game'.center(WIDTH - 2))
        self._out.write('\033[34;2H')
        self._out.write('Press any other key to start new game'.center(WIDTH - 2))


    def show_gameover_menu(self):
        Draw().clear_lines(self._out,
                           INFO_MENU_POS_Y + INFO_MENU_HEIGHT, 
                           INFO_MENU_POS_X,
                           HEIGHT - INFO_MENU_HEIGHT)
        self._show_start_game_menu()
        self._out.write(f'\033[3;2H')
        self._out.write('GAME OVER'.center(WIDTH - 2))


    def _show_level(self):
        self._out.write(f'\033[{SHIFT};{45+SHIFT}H Level {self._model.level} ')

    def show_win_screen(self):
        Draw().clear_lines(self._out,
                           INFO_MENU_POS_Y + INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT, 
                           INFO_MENU_POS_X,
                           HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT)
        self._out.write('\033[2J\033[H')
        self._out.write(f'\033[3;3HYOU WIN')
        self._out.write(f'\033[4;3Hpress any key')
        self._out.flush()

    def show_records(self, records):
        self._menu_render.update_records(records)

    def update(self):
        
        if self._model.gamestate:
            if self._model.gamestate == NORMAL:
                self._render.update()
            
        else:
            self.show_gameover_menu()
        self._menu_render.update()
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
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        Draw().clear_lines(self._out,
                           INFO_MENU_POS_Y + INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT, 
                           INFO_MENU_POS_X,
                           HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT)
        self._mode = not self._mode
        # self._show_controls()
        self._render = self._renders[self._mode](self, self._model)
        


    def _show_controls(self):
        y = CONTROLS_POS_Y
        x = CONTROLS_POS_X
        self._out.write(f'\033[{y + SHIFT};{x + SHIFT}H')
        if self._mode:
            self._out.write('w: forward | d: rotate right')
            y += 1
            self._out.write(f'\033[{y + SHIFT};{x + SHIFT}H')
            self._out.write('s: back | a: rotate left')
        else:
            self._out.write('w: up, s: down, d: right, a: left'.center(INFO_MENU_WIDTH * 2))


    def converter(self, obj):
        if obj == FLOOR:
            return '\033[2m·\033[0m'
        return str(obj)


    if __name__ == "__main__":
        pass