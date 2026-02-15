
from domain.generator import Generator
from domain.model import Model
from core.render import Render
from core.terminal import Terminal
from core.input import InputHandler
from datalayer.records import Records
from datalayer.loader import Loader
import sys


class Rouge:

    def __init__(self):
        self._render = None
        self._user_input = None
        self._records = None

    def run(self):
        with Terminal() as term:
            self._render = Render(term.stdout)
            self._user_input = InputHandler(term.fd)
            self._records = Records(self._render.menu_height)
            self._start_game()

    def _start_game(self):
        while True:
            self._render.show_start_game_menu()
            ch = self._user_input.getchar()
            if ch == 'q':
                return
            self._game_loop(ch)

    def _game_loop(self, ch):
        if ch == 'l':
            try: 
                loader = Loader()
                model = Model(loader.player, loader.data, loader.level) 
            except:
                self._render.show_can_not_load_file_screen()
                self._user_input.getchar()
                return
        else:
            model = Model(None, Generator().data, 0) #None = no player yet, 0 = level
        self._render.clear_game_field()
        self._render.show_game_menu()
        self._render.show_level(model.level + 1)
        self._render.show_records(self._records.data)
        self._render.render(model.gamestate, model.render_data(), model.backpack(), model.info())
        

        while model.gamestate: # >0
            ch = self._user_input.getchar()
            if ch == 'q':
                self._render.show_gameover_menu()
                # FIX ME save to json
                return
            model.update(ch)
            if model.passed:
                if model.level >= 20:
                    self._render.show_win_screen()
                    ch = self._user_input.getchar()
                    return

                model = Model(model.player, Generator().data, model.level + 1) 
                self._render.clear_game_field()    
                self._render.show_level(model.level + 1)
                self._render.show_records(self._records.data)
            self._render.render(model.gamestate, model.render_data(), model.backpack(), model.info())
        else:
            self._records.add_new_record([model.treasures_collected(), model.level + 1])
        
    # def _game_loop(self):

    #     sys.stdout.write(f'\033[{53};{1}H\033[2K{Generator()}')


if __name__ == '__main__':
    Rouge.game_loop()