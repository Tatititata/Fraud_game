from os import read
from common.keymap import *


class InputHandler:

    def __init__(self, fd):
        self._fd = fd

    def getchar(self):
        return read(self._fd, 5).decode()


class CommanInterpreter:

    _ESC = '\x1b'
    _F5 = '\x1b[15~'

    def __init__(self, render):
        self._game_state = 0
        self._render = render


    def update(self, char):
        if char == self._ESC:
            return Command.ESCAPE
        if self._game_state:
            if char == self._F5:
                return Command.CHANGE_RENDER
            elif char == 'w':
                return Command.MOVE_FORWARD
            elif char == 's':
                return Command.MOVE_BACK
            elif char == 'a':
                if self._render.mode:
                    return Command.ROTATE_LEFT
                else:
                    return Command.MOVE_LEFT
            elif char == 'd':
                if self._render.mode:
                    return Command.ROTATE_RIGHT
                else:
                    return Command.MOVE_RIGHT
            return char

        else:
            self._game_state = 1
            if char == 'l':
                return Command.LOAD
            return Command.CREATE

if __name__ == "__main__":
    InputHandler.getchar()