from common.constants import *
from common.drawing_const import *
from math import sin, cos, pi
from .drawing import Draw

FOV = pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH - 2
ANGLE_DELTA = FOV / NUM_RAYS
MAX_DEPTH = 98
MAX_VISIBLE_DEPTH = 20

    
class RayCasting:

    def __init__(self, out, model):
        self._out = out
        self._model = model
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)

    def _ray_casting(self):
            chars = []
            b = 250
            for _ in range((HEIGHT - 2) // 2):
                chars.append([f"\033[38;2;{b};{b};{b}m█" for _ in range(WIDTH - 2)])
                b -= 10

            b = 0
            for _ in range((HEIGHT - 2) // 2):
                chars.append([f"\033[38;2;{b};{b};{b}m░" for _ in range(WIDTH - 2)])
                b += 10
            depths = []
            step = 0.01
            r_angle = self._model.player.angle * pi - HALF_FOV
            for r in range(NUM_RAYS):

                sin_a = sin(r_angle) * step
                cos_a = cos(r_angle) * step

                depth = 0
                y, x = self._model.player.pos
                while depth < MAX_DEPTH:
                    y += sin_a
                    x += cos_a
                    depth += step
                    pos_ver = (round(y), round(x))

                    if not self._model.valid(pos_ver):
                        break
                depths.append(depth)

                r_angle += ANGLE_DELTA
            hights = []

            max_visible = MAX_VISIBLE_DEPTH
            room_hight = 48
            for r in range(len(depths)):
                depth = depths[r]
                if depth < max_visible:
                    norm_dist = depth / max_visible
                    b = int(255 * (1 - norm_dist))
                else:
                    b = 0
                height = min(int(room_hight / depth), room_hight)
                hights.append(height)
                ceil = min((48 - height) // 2, room_hight)
                char = '░'
                # for i in range(ceil):
                #     self._out.write(f'\033[{i+SHIFT + 1};{r+SHIFT}H')
                #     self._out.write(f"\033[48;2;{200};{200};{200}m \033[0m")
                # for i in range(ceil, ceil + height):
                #     self._out.write(f'\033[{i+SHIFT + 1};{r+SHIFT}H')
                #     self._out.write(f"\033[38;2;{brightness};{brightness};{brightness}m{char}\033[0m")
                # for i in range(ceil + height, 48):
                #     self._out.write(f'\033[{i+SHIFT + 1};{r+SHIFT}H')
                #     self._out.write(' ')
                for i in range(ceil, ceil + height):
                    chars[i][r] = f"\033[38;2;{b};{b};{b}m{char}"



            i = 0
            for line in chars:
                self._out.write(f'\033[{i+SHIFT + 1};{SHIFT + 1}H')
                self._out.write(''.join(line))
                i += 1
            self._out.write('\033[0m')
            self._out.flush()


    
    def update(self):
        self._ray_casting()



if __name__ == '__main__':
    pass
