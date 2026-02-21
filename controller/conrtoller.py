
from domain.generator import Generator
from domain.model import Model
from core.render import Render
from core.terminal import Terminal
from core.input import InputHandler
from datalayer.records import Records
from datalayer.loader import Loader, Saver
from domain.adapter import Adapter
import sys


class Rouge:

    def __init__(self):
        self._render = None
        self._user_input = None
        self._rec = None

    def run(self):
        with Terminal() as term:
            self._render = Render(term.stdout)
            self._user_input = InputHandler(term.fd)
            self._rec = Records(self._render.menu_height)
            # Generator(Adapter()).data
            self._start_game()

    def _start_game(self):
        while True:
            self._render.show_start_game_menu()
            ch = self._user_input.getchar()
            if ch == 'q':
                return
            self._game_loop(ch)

    def _game_loop(self, ch):
        model = None
        if ch == 'l':
            try: 
                model = Model(Loader()) 
            except Exception as e:
                self._render.show_can_not_load_game_screen() 
                self._user_input.getchar()
        ad = Adapter()
        model = model or Model(Generator(ad)) # no statistic
        self._render.clear_game_field()
        self._render.show_game_menu()
        self._render.show_level(model.level)
        self._render.show_records(self._rec.data)
        self._render.render_first_screen(model)

        while model.gamestate: # >0

            ch = self._user_input.getchar()
            if ch == 'q':
                self._render.show_gameover_menu()
                return Saver().save(model)
            model.update(ch)

            if model.passed:

                if model.level >= 20:
                    Saver().remove_saved_model()
                    self._render.show_win_screen()
                    return self._user_input.getchar()
                
                Saver().save(model)
                ad.update(model)
                self._rec.add_new_record(model)
                model = Model(Generator(ad, model.player), model.stats) 
                self._render.clear_game_field()    
                self._render.show_level(model.level)
                self._render.show_records(self._rec.data)

            self._render.render(model)                
        else:
            self._rec.add_new_record(model)
            Saver().remove_saved_model()


if __name__ == '__main__':
    Rouge.game_loop()