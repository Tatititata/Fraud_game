
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
        EXIT : '\033[1;37m█\033[0m',
        }

    def __init__(self, out):
        self._mode = 0
        self._out = out
        Draw().rectangle(self._out, 0, 0, HEIGHT, WIDTH)
        self._menu_render = MenuRender(self)
        self._show_start_game_menu()
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
        self._out.write(f'\033[5;5HPress \'l\' to load saved game.')
        self._out.write(f'\033[6;5HPress \'esc\' to quit.')
        self._out.write(f'\033[7;5HPress any other key to start new game.')


    def show_gameover_menu(self):
        Draw().clear_lines(self._out,
                           INFO_MENU_POS_Y + INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT, 
                           INFO_MENU_POS_X,
                           HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT)
        self._show_start_game_menu()
        self._out.write(f'\033[3;5HGAME OVER')


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
            self._menu_render.update()
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
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        Draw().clear_lines(self._out,
                           INFO_MENU_POS_Y + INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT, 
                           INFO_MENU_POS_X,
                           HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT)
        self._mode = not self._mode
        self._render = self._renders[self._mode](self, self._model)


    def converter(self, obj):
        if isinstance(obj, Character):
            return f'{self._symbols.get(obj.id, obj.id)}'
        elif isinstance(obj, Door):
            return f'{obj.color + 'x\033[0m'}'
        elif isinstance(obj, Item):
            if hasattr(obj, 'color'):
                return f'{obj.color + '&\033[0m'}'
            else:
                return f'{self._symbols.get(obj.id, obj.id)}'
        else:
            return f'{self._symbols.get(obj, obj)}'


    if __name__ == "__main__":
        pass