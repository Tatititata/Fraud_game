from common.constants import *
from common.drawing_const import *
from math import sin, cos, pi
from .drawing import Draw
from domain.model import Model
from domain.monsters import Monster
from domain.entity import Entity, Player
from common.playground import *

FOV = pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH - 2
ANGLE_DELTA = FOV / NUM_RAYS
MAX_DEPTH = 98
MAX_VISIBLE_DEPTH = 20
SCREEN_H = HEIGHT - 2
WALL_HIGHT = 48
    
class RayCasting:

    def __init__(self, parent, model:Model):
        self._out = parent._out
        self._parent = parent
        self._model = model
        Draw().clear_game_field(self._out, HEIGHT, WIDTH)
        Draw().rectangle(self._out, INFO_MENU_POS_Y + INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT, INFO_MENU_POS_X, 
                    HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT, INFO_MENU_WIDTH * 2)

    def _ray_casting(self):
            # return
            chars = []
            b = 250
            for _ in range((HEIGHT - 2) // 2):
                chars.append([f"\033[38;2;{b};{b};{b}m█" for _ in range(WIDTH - 2)])
                b -= 10

            b = 0
            for _ in range((HEIGHT - 2) // 2):
                chars.append([f"\033[38;2;{b};{b};{b}m░" for _ in range(WIDTH - 2)])
                b += 10
            depths = self._get_depths()

            max_visible = MAX_VISIBLE_DEPTH

            base_color = (110, 100, 100)
                
            for j in range(NUM_RAYS):
                depth = depths[j]
                if depth[-1] < max_visible:
                    norm_dist = depth[-1] / max_visible
                    br = int(255 * (1 - norm_dist))
                else:
                    br = 0
                height = min(int(WALL_HIGHT / depth[-1]), WALL_HIGHT)

                ceil = (WALL_HIGHT - height) // 2
                char =  '█'  #'░█'
                for i in range(ceil, ceil + height):
                    r = int(base_color[0] * (br / 255))
                    g = int(base_color[1] * (br / 255))
                    b = int(base_color[2] * (br / 255))
                    chars[i][j] = f"\033[38;2;{r};{g};{b}m{char}"

                top = SCREEN_H - 1

                if len(depth) > 1:
                    for d in depth[:-1]:
                        dist, char, size = d
                        height = min(int(WALL_HIGHT / dist), WALL_HIGHT)
                        ceil = (WALL_HIGHT - height) // 2
                        size = round(height * size)
                        start_point = min(height + ceil, top)
                        end_point = max(height + ceil - size, 0)
                        top = end_point
                        for i in range(start_point, end_point - 1, -1):
                            chars[i][j] = char
                        # if top <= 0:
                        #     break

            i = 0
            for line in chars:
                self._out.write(f'\033[{i+SHIFT + 1};{SHIFT + 1}H')
                self._out.write(''.join(line))
                i += 1
            self._out.write('\033[0m')


    def _draw_map(self):
        map_height = HEIGHT - INFO_MENU_HEIGHT - BACKPACK_MENU_HEIGHT - 2
        map_width = INFO_MENU_WIDTH * 2 - 2

        y, x = self._model.player.pos
        start_y = y - map_height // 2
        start_x = x - map_width // 2
        cursor_y, cursor_x = INFO_MENU_POS_Y + INFO_MENU_HEIGHT + BACKPACK_MENU_HEIGHT + 2, INFO_MENU_POS_X + 2
        for y in range(start_y, start_y + map_height):
            line = []
            for x in range(start_x, start_x + map_width):
                pos = (y, x)
                if pos in self._visible:
                    obj = self._model.visible(pos)
                    char = self._parent.converter(pos, obj)
                elif pos in self._model._explored:
                    char = self._model.layout(pos)
                else:
                    char = ' '
                line.append(char)
            self._out.write(f'\033[{cursor_y};{cursor_x}H')
            self._out.write(f'{"".join(line)}')
            cursor_y += 1

    
    def update(self):
        self._visible = self._model.data_for_rendering
        self._ray_casting()
        self._draw_map()

    def _get_depths(self):
        depths = {i: [] for i in range(NUM_RAYS)}
        step = 0.09
        r_angle = self._model.player.angle * pi - HALF_FOV
        for i in range(NUM_RAYS):
            
            old_pos = None

            sin_a = sin(r_angle) * step
            cos_a = cos(r_angle) * step
            depth = 0

            y, x = self._model.player.pos

            while depth < MAX_DEPTH:
                y += sin_a
                x += cos_a
                depth += step
                pos = (round(y), round(x))
                if pos != old_pos:
                    old_pos = pos
                    
                    if pos not in self._visible:
                        break
                    obj = self._model.visible(pos)
                    if obj in ROOM_WALLS:
                        break
                    if obj != FLOOR and not isinstance(obj, Player):
                        if isinstance(obj, Monster):
                            depths[i].append((depth, self._parent.converter(pos, obj), 0.8))
                        elif isinstance(obj, Entity):
                            depths[i].append((depth, self._parent.converter(pos, obj), 0.3))


            depths[i].append(depth)
            r_angle += ANGLE_DELTA

        return depths

if __name__ == '__main__':
    pass
