from json import dump, load


class Loader:
    def __init__(self):
        self._file = 'saved_game.json'

    @property
    def data(self):
        with open(self._file) as file:
            data = load(file)
            return data


class Saver():
    def __init__(self):
        self._file = 'saved_game.json'

    def save(self, model):
        with open(self._file, 'w') as file:
            dump(model.data_for_saving(), file, indent = 2)

    def remove_saved_model(self):
        with open(self._file, 'w') as file:
            return