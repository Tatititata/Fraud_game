from json import dump, load


class Loader:
    def __init__(self):
        self._file = 'saved_game.json'

    @property
    def data(self):
        with open(self._file) as file:
            data = load(file)
            # with open('loader.txt', 'w') as f:
            #     f.write(f'data\n{isinstance(data, dict)}\n')
            #     f.write(f'data keys\n{data.keys()}\n')
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