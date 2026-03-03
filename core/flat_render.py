
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
    
    _positions = dict(zip(FULL_BACKPACK, range(len(FULL_BACKPACK))))

    def __init__(self, out, model):
        self._out = out
        self._model = model
        self.restore_backpack = set()
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        self._render_game(self._model.first_screen)
        self.update()
        
    def update(self):
        gamestate = self._model.gamestate
        backpack = self._model.backpack
        self._clear_backpack_menu()
        if isinstance(backpack, set):
            self.restore_backpack = backpack - self.restore_backpack
            self._render_backpack(INFO_MENU_POS_Y + 2, INFO_MENU_POS_X + 18)
            if self._model.danger:
                self._show_danger(self._model.danger)
            if gamestate == GAMEOVER:
                self.show_gameover_menu()
                return
        else:
            self._render_backpack_details(backpack)
        if gamestate == NORMAL:
            self._render_game(self._model.data_for_rendering)
        elif gamestate == FOOD:
            self._render_food_menu()
        elif gamestate == POTION:
            self._render_potion_menu()
        elif gamestate == SCROLL:
            self._render_scroll_menu()
        elif gamestate == WEAPON:
            self._render_weapon_menu()
        elif gamestate == KEY:
            self._render_key_menu()
        self._out.flush()

    def _show_danger(self, danger):
        y, x = INFO_MENU_POS_Y + INFO_MENU_HEIGHT, INFO_MENU_POS_X
        danger = iter(danger)
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

    def _render_backpack_details(self, backpack):
        y = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + 2
        x = 101
        for i, el in enumerate(backpack, 1):
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

    def _render_game(self, data_for_rendering:dict):
        for (y, x), char in data_for_rendering.items():
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{self._symbols.get(char, char)}')
 
    def _render_backpack(self, y, x):
        for k, v in self.restore_backpack:
            self._out.write(f"\033[{y+SHIFT + self._positions[k]};{x+SHIFT}H{v:4d}")

    @property
    def menu_height(self):
        return INFO_MENU_HEIGHT - 4

    if __name__ == "__main__":
        pass