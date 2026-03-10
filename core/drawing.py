from common.drawing_const import *
from common.playground import *
class Draw:

    @staticmethod
    def rectangle(out, y, x, h, w):
        out.write(f'\033[{y+SHIFT};{x+SHIFT}H')
        out.write(TLCR)
        out.write(WALL_HOR * (w - 2))
        out.write(TRCR)
        for i in range(h - 2):
            out.write(f'\033[{y+SHIFT + 1 + i};{x+SHIFT}H')
            out.write(WALL_VER)
            out.write(f'\033[{y+SHIFT + 1 + i};{x+SHIFT + w - 1}H')
            out.write(WALL_VER)
        out.write(f'\033[{y+SHIFT + h - 1};{x+SHIFT}H')
        out.write(BLCR)
        out.write(WALL_HOR * (w - 2))
        out.write(BRCR)

    @staticmethod
    def clear_game_field(out, h, w):
            s = GROUND * (w - 2)
            for y in range(h - 2):
                out.write(f'\033[{y + SHIFT + 1};{SHIFT + 1}H{s}')

    @staticmethod
    def clear_lines(out, y, x, h):
        for i in range(y, y + h):
            out.write(f'\033[{SHIFT + i};{x+SHIFT}H\033[0K')