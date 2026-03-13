from common.characters import *
from common.playground import *
from common.constants import *
from common.drawing_const import *
from .drawing import Draw


class MenuRender:

    _positions = dict(zip(FULL_BACKPACK, range(len(FULL_BACKPACK))))

    def __init__(self, parent):
        self._out = parent._out
        self._show_game_menu()
        self._show_record_menu()
        self._clear_backpack_menu()
        self._old_backpack = set()

    def set_up(self, model):
        self._model = model
        self._render_backpack(INFO_MENU_POS_Y + 2, INFO_MENU_POS_X + 18)

    def _show_game_menu(self):
        Draw().rectangle(self._out, INFO_MENU_POS_Y, INFO_MENU_POS_X, INFO_MENU_HEIGHT, INFO_MENU_WIDTH)
        self._draw_game_info()

    def _show_record_menu(self):
        Draw().rectangle(self._out, REC_MENU_POS_Y, REC_MENU_POS_X, REC_MENU_HEIGHT, REC_MENU_WIDTH)
        Draw().rectangle(self._out, REC_MENU_POS_Y, REC_MENU_POS_X, REC_MENU_HEIGHT, REC_MENU_WIDTH)
        y = REC_MENU_POS_Y + 1
        x = REC_MENU_POS_X + 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('=== BEST RECORDS ==='.center(INFO_MENU_WIDTH - 2))
        self._out.write(f'\033[{y+SHIFT + 1};{x+SHIFT}H')
        self._out.write('treasure      level'.center(INFO_MENU_WIDTH - 2))

    def update_records(self, records):
        y = REC_MENU_POS_Y + 3
        x = REC_MENU_POS_X + 1
        records = iter(records.data)
        record = next(records, None)
        while y < REC_MENU_POS_Y + INFO_MENU_HEIGHT - 1 and record:
            t, l = record
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
            self._out.write(f'{t:<8d} - - - {l:2d}'.center(INFO_MENU_WIDTH - 2))
            record = next(records, None)
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
    
    def update(self):
        gamestate = self._model.gamestate
        self._clear_backpack_menu()
        
        if gamestate == NORMAL:
            self._show_danger()
            self._render_backpack(INFO_MENU_POS_Y + 2, INFO_MENU_POS_X + 18)
            return
        self._render_backpack_details()
        if gamestate == FOOD:
            self._render_food_menu()
        elif gamestate == POTION:
            self._render_potion_menu()
        elif gamestate == SCROLL:
            self._render_scroll_menu()
        elif gamestate == WEAPON:
            self._render_weapon_menu()
        elif gamestate == KEY:
            self._render_key_menu()

        
        
    def _show_danger(self):
        if not self._model.danger:
            return

        y, x = INFO_MENU_POS_Y + INFO_MENU_HEIGHT, INFO_MENU_POS_X
        danger = iter(self._model.danger)
        d = next(danger, None)
        while d and y < INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT:
            self._out.write(f'\033[{SHIFT + y};{x+SHIFT}H{d}')
            d = next(danger, None)
            y += 1

    def _render_food_menu(self):
        y = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('=== FOOD ==='.center(INFO_MENU_WIDTH * 2 - 2))
        
    def _render_potion_menu(self):
        y = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('=== POTION ==='.center(INFO_MENU_WIDTH * 2 - 2))
        
    def _render_scroll_menu(self):
        y = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('=== SCROLL ==='.center(INFO_MENU_WIDTH * 2 - 2))
        
    def _render_weapon_menu(self):
        y = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('=== WEAPON ==='.center(INFO_MENU_WIDTH * 2 - 2))

    def _render_key_menu(self):
        y = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('=== KEY ==='.center(INFO_MENU_WIDTH * 2 - 2))

    def _render_backpack_details(self):
        y = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + 2
        x = 101
        for i, el in enumerate(self._model.backpack, 1):
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
            self._out.write(f'{i}. {el}')
            y += 1
   
        menu_height = y - INFO_MENU_POS_Y - INFO_MENU_HEIGHT + 1
        Draw().rectangle(self._out, 
                         INFO_MENU_POS_Y + INFO_MENU_HEIGHT, 
                         INFO_MENU_POS_X, 
                         menu_height, 
                         INFO_MENU_WIDTH * 2)
        
    def _clear_backpack_menu(self):
        y, x = INFO_MENU_POS_Y + INFO_MENU_HEIGHT, INFO_MENU_POS_X
        for i in range(y, y + BACKPACK_MENU_HEIGHT):
            self._out.write(f'\033[{SHIFT + i};{x+SHIFT}H\033[0K')

    def _render_backpack(self, y, x):
        self._old_backpack = self._model.backpack - self._old_backpack
        for k, v in self._old_backpack:
            self._out.write(f"\033[{y+SHIFT + self._positions[k]};{x+SHIFT}H{v:4d}")