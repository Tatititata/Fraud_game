from common.keymap import *
from .generator import Generator
from .model import Model
from datalayer.loader import Loader
from .adapter import Adapter


class ModelFactory:

    def __init__(self):
        self._adapter = Adapter()

    def new_model(self, command):
        if command == Command.LOAD:
            try: 
                return Model(Loader()) 
            except Exception as e:
                 return Model(Generator(self._adapter))
        elif command == Command.CREATE:
            return Model(Generator(self._adapter))
        
    def next_level(self, model):
        self._adapter.update(model)
        return Model(Generator(self._adapter, model.player), model.stats) 
