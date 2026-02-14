
from common.characters import *
from common.playground import *
from common.constants import *

SHIFT = 1
MENU_WIDTH = 26
MENU_HEIGHT = 13
INFO_MENU_POS_Y = 0
INFO_MENU_POS_X = 100

class Render:
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
        FLOOR : '\033[2m·\033[0m'
        }
    
    _positions = dict(zip(FULL_BACKPACK, range(len(FULL_BACKPACK))))

    def __init__(self, out):
        self._out = out
        self._render_game_border()
        # self.restore_pos = set()
        self.restore_backpack = set()
        self._old_gamestate = None
        # self._backpack_menu_height = MENU_HEIGHT
        self._out.write('\033[?25l')  # hide cursor
        self._out.flush()

    
    def update_layout(self, playground, info=None):

        self.clear_game_field()
        for (y, x), char in  playground.layout.items():
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{char}')
        
        

        # self._out.write('\033[?25l')  # hide cursor
        # self._out.write('\033[H')     # move cursor home: (1,1)
        # endl = '\r\n'
        # # level = [f"{i:02d}" + ''.join(l) for i, l in enumerate(self._layout)]
        # # s1 = '  ' + ''.join(str(i) + ' ' * 9 for i in range(10)) + endl
        # # s2 = '  ' + '0123456789' * 10 + endl
        # # self._out.write(s1 + s2 + endl.join(level))

        # level = [''.join(l) for l in self._layout]
        # self._out.write(endl.join(level))
        # self._draw_rectangle(INFO_MENU_POS_Y, INFO_MENU_POS_X, MENU_HEIGHT, MENU_WIDTH)
        # self._draw_game_info(INFO_MENU_POS_Y + 1, INFO_MENU_POS_X + 1)
        # self._render_backpack(INFO_MENU_POS_Y + 2, INFO_MENU_POS_X + 18)
        self._out.flush()

    def render(self, gamestate, entities:set, backpack, info=None):
        if gamestate == GAMEOVER:
            self.show_gameover_menu()
            return
        self._clear_backpack_menu()
        # if self._old_gamestate != gamestate:
        #     self._clear_backpack_menu()
        #     self._old_gamestate = gamestate
        if isinstance(backpack, set):
            self.restore_backpack = backpack - self.restore_backpack
            self._render_backpack(INFO_MENU_POS_Y + 2, INFO_MENU_POS_X + 18)
        else:
            self._render_backpack_details(backpack)
        if gamestate == NORMAL:
            self._render_game(entities)
        elif gamestate == FOOD:
            self._render_food_menu()
        elif gamestate == POTION:
            self._render_potion_menu()
        elif gamestate == SCROLL:
            self._render_scroll_menu()
        elif gamestate == WEAPON:
            self._render_weapon_menu()

        if info:
            self._show_current_danger(info)
        self._out.flush()

    def _show_current_danger(self, info):
        y, x = INFO_MENU_POS_Y + MENU_HEIGHT, INFO_MENU_POS_X
        for i in info:
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{i}')
            y += 1
        self._backpack_menu_height = y - INFO_MENU_POS_Y - MENU_HEIGHT

    def show_game_menu(self):
        self._draw_rectangle(INFO_MENU_POS_Y, INFO_MENU_POS_X, MENU_HEIGHT, MENU_WIDTH)
        self._draw_game_info(INFO_MENU_POS_Y + 1, INFO_MENU_POS_X + 1)
        self._render_backpack(INFO_MENU_POS_Y + 2, INFO_MENU_POS_X + 18)
        self._out.flush()       

    def _render_food_menu(self):
        y = INFO_MENU_POS_Y + MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write(' ===   FOOD    ===')
        
    def _render_potion_menu(self):
        y = INFO_MENU_POS_Y + MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write(' ===  POTION   ===')
        
    def _render_scroll_menu(self):
        y = INFO_MENU_POS_Y + MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write(' ===  SCROLL   ===')
        
    def _render_weapon_menu(self):
        y = INFO_MENU_POS_Y + MENU_HEIGHT + 1
        x = 101
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write(' ===  WEAPON   ===')

    def _render_backpack_details(self, backpack):
        y = INFO_MENU_POS_Y + MENU_HEIGHT + 2
        x = 101
        # self._out.write(f'\033[{51};{1}H{backpack}')
        for i, el in enumerate(backpack, 1):
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{i}.')
            for k, v in sorted((attr, getattr(el, attr)) for attr in dir(el) if not attr.startswith('_') and not attr == 'id'):
                self._out.write(f'\033[{y+SHIFT};{x+SHIFT + 3}H{k} - {v}')
                y += 1
        # self._out.write(f'\033[{53};{1}H y = {y}')   
        self._backpack_menu_height = y - INFO_MENU_POS_Y - MENU_HEIGHT + 1
        # if self._backpack_menu_height < 3:
            # self._backpack_menu_height += 1
        # self._out.write(f'\033[{52};{1}H self._backpack_menu_height = {self._backpack_menu_height}')
        self._draw_rectangle(INFO_MENU_POS_Y + MENU_HEIGHT, INFO_MENU_POS_X, self._backpack_menu_height, MENU_WIDTH)
        

    def _clear_backpack_menu(self):
        y, x = INFO_MENU_POS_Y + MENU_HEIGHT, INFO_MENU_POS_X
        for i in range(y, HEIGHT):
            self._out.write(f'\033[{SHIFT + i};{x+SHIFT}H\033[0K')
            # self._out.write(f'\033[{SHIFT + i};{x+SHIFT}H')
            # self._out.write(' ' * (w))

    def _render_game(self, entities:dict):
        for y, x, char in entities:
            self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H{self._symbols.get(char, char)}')


    def show_start_game_menu(self):
        # self._out.write('\033[2J\033[H')
        self._out.write(f'\033[3;3Hto start new game press any key')
        self._out.write(f'\033[4;3Hto quit press q')
        self._out.flush()


    def show_gameover_menu(self):
        self._out.write('\033[2J\033[H')
        self._out.write(f'\033[3;3Hgameover menu')
        self._out.write(f'\033[4;3Hpress any key')
        self._out.flush()

    def show_level(self, level):
        self._out.write(f'\033[{SHIFT};{45+SHIFT}H Level {level} ')

    def show_win_screen(self):
        self._out.write('\033[2J\033[H')
        self._out.write(f'\033[3;3HYOU WIN')
        self._out.write(f'\033[4;3Hpress any key')
        self._out.flush()


    # sys.stdout.write('\033[2J\033[H')  # Очистка экрана



    def _draw_game_info(self, y, x):
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write(' === GAME INFO ===')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('FOOD ----------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('POTION --------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('SCROLL --------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('WEAPON --------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('CURRENT_WEAPON - ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('DEXTERITY ------ ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('STRENGTH ------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('HEALTH --------- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('MAX HEALTH ----- ')
        y += 1
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write('TREASURE ------- ')
 
    def _render_backpack(self, y, x):
        for k, v in self.restore_backpack:
            self._out.write(f"\033[{y+SHIFT + self._positions[k]};{x+SHIFT}H{v:4d}")


    def _draw_rectangle(self, y, x, h, w):
        self._out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        self._out.write(TLCR)
        self._out.write(WALL_HOR * (w - 2))
        self._out.write(TRCR)
        for i in range(h - 2):
            self._out.write(f'\033[{y+SHIFT + 1 + i};{x+SHIFT}H')
            self._out.write(WALL_VER)
            self._out.write(f'\033[{y+SHIFT + 1 + i};{x+SHIFT + w - 1}H')
            self._out.write(WALL_VER)
        self._out.write(f'\033[{y+SHIFT + h - 1};{x+SHIFT}H')
        self._out.write(BLCR)
        self._out.write(WALL_HOR * (w - 2))
        self._out.write(BRCR)
 

    def _render_game_border(self):
        #vertical border lines
        for y in range(HEIGHT):
            self._out.write(f'\033[{y+SHIFT};{SHIFT}H{WALL_VER}')
            self._out.write(f'\033[{y+SHIFT};{SHIFT + WIDTH - 1}H{WALL_VER}')
        #horizontal border lines
        for x in range(WIDTH):
            self._out.write(f'\033[{SHIFT};{SHIFT + x - 1}H{WALL_HOR}')
            self._out.write(f'\033[{SHIFT + HEIGHT - 1};{SHIFT + x - 1}H{WALL_HOR}')

        # corners
        self._out.write(f'\033[{SHIFT};{SHIFT}H{TLCR}')
        self._out.write(f'\033[{SHIFT};{SHIFT + WIDTH - 1}H{TRCR}')
        self._out.write(f'\033[{SHIFT + HEIGHT - 1};{SHIFT}H{BLCR}')
        self._out.write(f'\033[{SHIFT + HEIGHT - 1};{SHIFT + WIDTH - 1}H{BRCR}')


    def clear_game_field(self):
        for y in range(HEIGHT - 2):
            for x in range(WIDTH - 2):
                self._out.write(f'\033[{y + SHIFT + 1};{x + SHIFT + 1}H{GROUND}')

    if __name__ == "__main__":
        pass