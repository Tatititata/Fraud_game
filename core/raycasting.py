from common.constants import *
from math import sin, cos, tan, pi

FOV = pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH - 2
ANGLE_DELTA = FOV / NUM_RAYS


class RayCasting:

    def __init__(self, out):
        self._out = out
        self._out.write('\033[?25l')  # hide cursor
        self._out.flush()


    def _ray_casting(self):
        pass

    def update(self, model):
        pass

