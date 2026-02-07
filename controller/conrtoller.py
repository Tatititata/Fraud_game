
from domain.level import Level
from domain.model import Model
from ui.ui import UI
import sys

class Rouge:

    @staticmethod
    def game_loop():


        # print(self.level)
        # return
        game_over = False
        level = Level()
        with UI(level.layout) as ui:
            model = Model(0, level.matrix, level.rooms, level.start)
            ui.render(model.entities())
            # self.level.start_game()
            # sys.stdout.write('\r\n' + str(self.level.corridors) + '\r\n')
            # sys.stdout.write('\r\n' + str(self.level.rooms) + '\r\n')
            # sys.stdout.write('\r\n' + str(self.level.gates) + '\r\n')
            while not game_over and model.level < 22:
                ch = ui.getchar()
                if ch == 'q':
                    game_over = True
                    ui.print_gameover_screen()
                else:
                    model.handle_move(ch)
                    if model.passed:
                        level = Level()
                        model = Model(model.level + 1, level.matrix, level.rooms, level.start)
                        ui.update_layout(level.layout)
                    ui.render(model.entities())
                
                

            



# if __name__ == '__main__':
#     Rouge.game_loop()