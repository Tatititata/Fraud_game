
from domain.level import Level
from domain.model import Model
from ui.ui import UI
import sys

class Rouge:

    def __init__(self):
        self.level = 0
        self.model = None
        self.game_over = False

    def game_loop(self):


        # print(self.level)
        # return

        level = Level()
        with UI(level.layout) as ui:
            self.model = Model(self.level, level.matrix, level.rooms, level.start)
            ui.render(self.model.entities())
            # self.level.start_game()
            # sys.stdout.write('\r\n' + str(self.level.corridors) + '\r\n')
            # sys.stdout.write('\r\n' + str(self.level.rooms) + '\r\n')
            # sys.stdout.write('\r\n' + str(self.level.gates) + '\r\n')
            while not self.game_over and self.level < 22:
                ch = ui.getchar()
                if ch == 'q':
                    self.game_over = True
                    ui.print_gameover_screen()
                else:
                    self.model.handle_move(ch)
                    if self.model.passed:
                        self.level += 1
                        level = Level()
                        self.model = Model(self.level, level.matrix, level.rooms, level.start)
                        ui.update_layout(self.level.layout)
                    ui.render(self.model.entities())
                
                

            



# if __name__ == '__main__':
#     Rouge.game_loop()