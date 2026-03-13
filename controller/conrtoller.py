

from domain.model_factory import ModelFactory
from core.main_render import MainRender

from core.terminal import TerminalFactory
from core.command_interpreter import InputHandler, CommanInterpreter
from datalayer.records import Records
from datalayer.loader import Saver

from common.keymap import Command
import sys



class Rouge:

    def __init__(self):
        self._render = None

    def run(self):

        with TerminalFactory().create() as term:
            self._render = MainRender(term.stdout)
            self._user_input = InputHandler(term)
            
            self._start_game()

    def _start_game(self):

        while True:
            self._render.show_records(Records())
            self._commander = CommanInterpreter(self._render)
            command = self._commander.update(self._user_input.getchar())
            if command == Command.ESCAPE:
                return
            self._game_loop(command)

    def _game_loop(self, command):

        factory = ModelFactory()
        model, flag = factory.new_model(command)
        if not flag:
            self._render.show_can_not_load_game_screen()
            self._user_input.getchar()
    
        self._render.set_up(model)

        while model.gamestate: # >0

            command = self._commander.update(self._user_input.getchar())
            if command == Command.ESCAPE:
                self._render.show_gameover_menu()
                return Saver().save(model)
            elif command == Command.CHANGE_RENDER:
                self._render.change_mode()

            model.update(command)

            if model.passed:

                if model.level >= 21:
                    Saver().remove_saved_model()
                    self._render.show_win_screen()
                    return self._user_input.getchar()
                
                Saver().save(model)
                Records().add_new_record(model)
                model = factory.next_level(model)
                self._render.set_up(model)
                self._render.show_records(Records())

            self._render.update()                
        else:
            Records().add_new_record(model)
            Saver().remove_saved_model()


if __name__ == '__main__':
    Rouge.game_loop()