from common.characters import *
from common.playground import *
from common.constants import *
from common.drawing_const import *
from .drawing import Draw


class MenuRender:
    def __init__(self, out):
        self._out = out
        self._show_game_menu()
        self._show_record_menu()
        Draw().rectangle(self._out, INFO_MENU_POS_Y + INFO_MENU_HEIGHT + 12, INFO_MENU_POS_X, 
                         HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT, INFO_MENU_WIDTH * 2)

    def _show_game_menu(self):
        Draw().rectangle(self._out, INFO_MENU_POS_Y, INFO_MENU_POS_X, INFO_MENU_HEIGHT, INFO_MENU_WIDTH)
        self._draw_game_info()

    def _show_record_menu(self):
        Draw().rectangle(self._out, REC_MENU_POS_Y, REC_MENU_POS_X, REC_MENU_HEIGHT, REC_MENU_WIDTH)
        y = REC_MENU_POS_Y + 1
        x = REC_MENU_POS_X + 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('=== BEST RECORDS ==='.center(INFO_MENU_WIDTH - 2))
        self._out.write(f'\033[{y+SHIFT + 1};{x+SHIFT}H')
        self._out.write('treasure      level'.center(INFO_MENU_WIDTH - 2))

    def update_records(self, records):
        Draw().rectangle(self._out, REC_MENU_POS_Y, REC_MENU_POS_X, REC_MENU_HEIGHT, REC_MENU_WIDTH)
        y = REC_MENU_POS_Y + 3
        x = REC_MENU_POS_X + 1
        records = iter(records.data)
        record = next(records, None)
        while y < INFO_MENU_HEIGHT - 1 and record:
            t, l = record
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
            self._out.write(f'{t:<8d} - - - {l:2d}'.center(INFO_MENU_WIDTH - 2))
            record = next(records)
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