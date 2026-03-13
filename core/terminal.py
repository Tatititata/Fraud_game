# import tty
# import termios
import sys


class TerminalInterface:
    def __enter__(self): pass
    def __exit__(self, *args): pass
    @property
    def stdout(self): pass



class LinuxTerminal(TerminalInterface):

    def __init__(self):
        from tty import setraw
        from termios import tcgetattr, tcsetattr, TCSADRAIN
        self._setraw = setraw
        self.fd = sys.stdin.fileno()
        self.original = tcgetattr(self.fd)
        self._setattr = tcsetattr
        self._TCSADRAIN = TCSADRAIN
    
    def __enter__(self):
        self._setraw(self.fd)
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.write('\033[?25l')  
        sys.stdout.flush()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
        self._setattr(self.fd, self._TCSADRAIN, self.original)

    @property
    def stdout(self):
        return sys.stdout



class WindowsTerminal(TerminalInterface):
    def __init__(self):
        from msvcrt import getch
        self._getch = getch
    
    def __enter__(self):
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    
    def getchar(self):
        first = self._getch()
        
        if first in (b'\x00', b'\xe0'):  
            second = self._getch() 
            if second == b'?': 
                return '\x1b[15~'  
            return ''  
        
        return first.decode('utf-8', errors='ignore')

    @property
    def stdout(self):
        return sys.stdout


class TerminalFactory:
    @staticmethod
    def create():
        if sys.platform.startswith('win'):
            return WindowsTerminal()
        else:
            return LinuxTerminal()



if __name__ == "__main__":
    with LinuxTerminal():
        pass