class Adapter:
    def __init__(self):
        self._data = None
    

    def update(self, model):
        with open('apdater.txt', 'a') as f:
            f.write(f'{model.stats}\n')
