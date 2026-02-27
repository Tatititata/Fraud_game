
from domain.generator import Generator
from domain.model import Model
from core.render import MainRender
from core.flat_render import FlatRender
from core.raycasting import RayCasting
from core.terminal import Terminal
from core.input import InputHandler
from datalayer.records import Records
from datalayer.loader import Loader, Saver
from domain.adapter import Adapter
from common.keymap import *
import sys


class Rouge:

    def __init__(self):
        self._main_render = None
        self._user_input = None
        self._rec = None

    def run(self):
        with Terminal() as term:
            self._main_render = MainRender(term.stdout)
            self._user_input = InputHandler(term.fd)
            self._rec = Records(self._main_render.menu_height)
            self._start_game()

    def _start_game(self):
        while True:
            self._main_render.show_start_game_menu()
            self._main_render.show_game_menu()
            self._main_render.show_records(self._rec.data)
            ch = self._user_input.getchar()
            if ch == ESC:
                return
            self._game_loop(ch)

    def _game_loop(self, ch):
        renders = [FlatRender, RayCasting]
        mode = 0
        model = None
        if ch == 'l':
            try: 
                model = Model(Loader()) 
            except Exception as e:
                self._main_render.show_can_not_load_game_screen() 
                self._user_input.getchar()
        ad = Adapter()
        model = model or Model(Generator(ad)) # no statistic
        self._main_render.show_level(model.level)
        self._main_render.clear_game_field()

        render = renders[mode](self._main_render.out, model)
        render.render_first_screen()

        while model.gamestate: # >0
            ch = self._user_input.getchar()
            if ch == ESC:
                self._main_render.show_gameover_menu()
                return Saver().save(model)
            elif ch == F5:
                mode = not mode
                render = renders[mode](self._main_render.out, model)
            model.update(ch)
            if model.passed:
                if model.level >= 20:
                    Saver().remove_saved_model()
                    self._main_render.show_win_screen()
                    return self._user_input.getchar()
                Saver().save(model)
                ad.update(model)
                self._rec.add_new_record(model)
                model = Model(Generator(ad, model.player), model.stats) 
                self._main_render.clear_game_field()    
                self._main_render.show_level(model.level)
                self._main_render.show_records(self._rec.data)
            render.update()                
        else:
            self._rec.add_new_record(model)
            Saver().remove_saved_model()


if __name__ == '__main__':
    Rouge.game_loop()