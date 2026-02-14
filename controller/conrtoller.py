
from domain.generator import Generator
from domain.model import Model
from core.render import Render
from core.terminal import Terminal
from core.input import InputHandler
import sys


class Rouge:

    def __init__(self):
        self._render = None
        self._user_input = None
        

    def run(self):
        with Terminal() as term:
            self._render = Render(term.stdout)
            self._user_input = InputHandler(term.fd)
            self._start_game()

    def _start_game(self):
        while True:
            self._render.show_start_game_menu()
            if self._user_input.getchar() == 'q':
                return
            self._game_loop()

    def _game_loop(self):
        model = Model(None, Generator().data, 0) #None = no player yet, 0 = level
        self._render.clear_game_field()
        self._render.show_game_menu()
        self._render.show_level(1)
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
            self._render.render(model.gamestate, model.render_data(), model.backpack(), model.info())
        
    # def _game_loop(self):

    #     sys.stdout.write(f'\033[{53};{1}H\033[2K{Generator()}')


if __name__ == '__main__':
    Rouge.game_loop()