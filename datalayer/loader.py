from json import dump

class Loader:

    pass


class Saver():

    def __init__(self, model):
        self._file = 'saved_game.json'
        with open(self._file, 'w'):
            dump(self._file, model.data)