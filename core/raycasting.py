from common.constants import *
from common.drawing_const import *
from math import sin, cos, pi
from .drawing import Draw
from domain.model import Model

FOV = pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH - 2
ANGLE_DELTA = FOV / NUM_RAYS
MAX_DEPTH = 98
MAX_VISIBLE_DEPTH = 20

    
class RayCasting:

    def __init__(self, parent, model:Model):
        self._out = parent._out
        self._symbols = parent._symbols
        self._model = model
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        Draw().rectangle(self._out, INFO_MENU_POS_Y + INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT, INFO_MENU_POS_X, 
                    HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT, INFO_MENU_WIDTH * 2)

    def _ray_casting(self):
            # return
            visible = self._model.data_for_rendering
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
                    pos = (round(y), round(x))

                    if pos not in visible:
                        break
                depths.append(depth)

                r_angle += ANGLE_DELTA
            hights = []

            max_visible = MAX_VISIBLE_DEPTH
            room_hight = 46
            base_color = (110, 100, 100)
                
            for j in range(len(depths)):
                depth = depths[j]
                if depth < max_visible:
                    norm_dist = depth / max_visible
                    b = int(255 * (1 - norm_dist))
                else:
                    b = 0
                height = min(int(room_hight / depth), room_hight)
                hights.append(height)
                ceil = min((room_hight - height) // 2, room_hight)
                char = '░'
                for i in range(ceil, ceil + height):
                    r = int(base_color[0] * (b / 255))
                    g = int(base_color[1] * (b / 255))
                    b_color = int(base_color[2] * (b / 255))
                    chars[i][j] = f"\033[38;2;{r};{g};{b_color}m█"

            i = 0
            for line in chars:
                self._out.write(f'\033[{i+SHIFT + 1};{SHIFT + 1}H')
                self._out.write(''.join(line))
                i += 1
            self._out.write('\033[0m')


    def _draw_map(self):
        map_height = HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT - 2
        map_width = INFO_MENU_WIDTH * 2 - 2
        visible = self._model.data_for_rendering
        y, x = self._model.player.pos
        start_y = y - map_height // 2
        start_x = x - map_width // 2
        cursor_y, cursor_x = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT + 2, INFO_MENU_POS_X + 2
        for y in range(start_y, start_y + map_height):
            line = []
            for x in range(start_x, start_x + map_width):
                if (y, x) in visible:
                    char = self._model.visible((y, x))
                elif (y, x) in self._model._explored:
                    char = self._model.layout((y, x))
                else:
                    char = ' '
                line.append(char)
            self._out.write(f'\033[{cursor_y};{cursor_x}H')
            self._out.write(f'{"".join(line)}')
            cursor_y += 1

    
    def update(self):
        self._ray_casting()
        self._draw_map()



if __name__ == '__main__':
    pass
