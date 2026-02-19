from json import dump, load
class Records:
    def __init__(self, size):
        self._file = 'records.json'
        self._size = size

    def add_new_record(self, model):
        try:
            with open(self._file) as file:
                data = load(file)
        except:
            data = []
        data.append(model.stats)
        with open(self._file, 'w') as file:
            dump(data, file, indent=2)

    @property
    def data(self):
        try:
            with open(self._file) as file:
                data = sorted(load(file), key=lambda x: x['treasure'], reverse=True)[:self._size]
                return [(d['treasure'], d['level_reached']) for d in data]
        except Exception as e:
            with open('log.txt', 'a') as f:
                f.write(f'Record can not load data {e}\n')
            return []

    @property
    def stats(self):
        try:
            with open(self._file) as file:
                data = sorted(load(file), key=lambda x: x['treasure'], reverse=True)[:self._size]
            with open(self._file, 'w') as file:
                dump(data, file, indent=2)
                return data
        except:
            return []