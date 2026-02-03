from common.constants import *
import tty
import termios
import sys

class UI:

    def __init__(self, playground, info=None):
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        self.playground = playground.matrix
        self.info = info
        self.restore_pos = set()
        sys.stdout.write('\033[?25l')
        sys.stdout.write('\033[H')
        sys.stdout.write(str(playground).replace('\n', '\r\n'))
        sys.stdout.flush()

    def getchar(self):
        return sys.stdin.read(1)
    
    
    def render(self, entities:list):
        new_pos = set((e.y, e.x, e.id) for e in entities)
        self.restore_pos -= new_pos
        for y, x, _ in self.restore_pos:
            char = self.playground[y][x]
            sys.stdout.write(f'\033[{y+3};{x+3}H{char}')
        for y, x, char in new_pos:
            sys.stdout.write(f'\033[{y+3};{x+3}H{char}')
        sys.stdout.flush()
        self.restore_pos = new_pos
        # sys.stdout.write('\033[2J\033[H')  # Очистка экрана
        # print(self.level, flush=True)
        # pass
    
    def _restore_terminal(self):
        if hasattr(self, 'old') and self.old:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
            self.old = None
            # sys.stdout.write('\r\n')
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.write('\033[?25h')

    def print_gameover_screen(self):
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.write('game over\r\npress any key\r\n')
        self.getchar()

     
    def __enter__(self):
        tty.setraw(self.fd)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._restore_terminal()

    def __del__(self):
        self._restore_terminal()
        



if __name__ == "__main__":
    UI.getchar()