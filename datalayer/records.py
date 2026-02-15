from json import dump, load
class Records:
    def __init__(self, size):
        self._data = None
        try:
            with open('records.json') as file:
                self._data = sorted((data for data in load(file) if all(isinstance(d, int) and d >= 0 for d in data)), reverse=True)[:size]
        except:
            self._data = []

    def add_new_record(self, new_data):
        try:
            with open('records.json') as file:
                data = load(file)
        except:
            data = []
        data.append(new_data)
        with open('records.json', 'w') as file:
            dump(data, file)
        self._data.append(new_data)
        self._data.sort(reverse=True)
        self._data.pop()

    @property
    def data(self):
        return self._data