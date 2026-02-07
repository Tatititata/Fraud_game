from common.constants import *
import tty
import termios
import sys

class UI:

    def __init__(self, layout, info=None):
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        self.update_layout(layout, info)

    def getchar(self):
        return sys.stdin.read(1)
    
    def update_layout(self, layout, info=None):
        self.layout = layout
        self.info = info
        self.restore_pos = set()
        sys.stdout.write('\033[?25l')
        sys.stdout.write('\033[H')
        endl = '\r\n'
        level = [f"{i:02d}" + ''.join(l) for i, l in enumerate(layout)]
        s1 = '  ' + ''.join(str(i) + ' ' * 9 for i in range(10)) + endl
        s2 = '  ' + '0123456789' * 10 + endl
        sys.stdout.write(s1 + s2 + endl.join(level))
        sys.stdout.flush()

    def render(self, entities:set):
        self.restore_pos -= entities
        for (y, x), _ in self.restore_pos:
            char = self.layout[y][x]
            sys.stdout.write(f'\033[{y+3};{x+3}H{char}')
        for (y, x), char in entities:
            sys.stdout.write(f'\033[{y+3};{x+3}H{char}')
        sys.stdout.flush()
        self.restore_pos = entities
        # sys.stdout.write('\033[2J\033[H')  # Очистка экрана

    
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