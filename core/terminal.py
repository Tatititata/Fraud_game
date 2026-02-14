import tty
import termios
import sys

class Terminal:

    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.original = termios.tcgetattr(self.fd)
    
    def __enter__(self):
        tty.setraw(self.fd)
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.write('\033[?25l')  
        sys.stdout.flush()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.original)

    @property
    def stdout(self):
        return sys.stdout

if __name__ == "__main__":
    with Terminal():
        pass