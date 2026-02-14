from os import read

class InputHandler:

    def __init__(self, fd):
        self._fd = fd

    def getchar(self):
        return read(self._fd, 1).decode()

if __name__ == "__main__":
    InputHandler.getchar()