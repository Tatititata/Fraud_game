from common.constants import *
from common.characters import *
from common.playground import *


class Layout:

    @staticmethod
    def create_layout(rooms, corridors, with_rooms=False):
        layout = {}
        for r in rooms:
            if with_rooms:
                char = str(r.id)
                for y, x in r.floor:
                    layout[(y, x)] = char
            for y, x in r.vertical_walls:
                layout[(y, x)] = WALL_VER
            for y, x in r.horizontal_walls:
                layout[(y, x)] = WALL_HOR

            y, x = r.blc
            layout[(y, x)] = BLCR
            y, x = r.tlc
            layout[(y, x)] = TLCR
            y, x = r.brc
            layout[(y, x)] = BRCR
            y, x = r.trc
            layout[(y, x)] = TRCR

        for corridor in corridors:
            for (y, x) in corridor.walls:
                if (y - 1, x) in corridor.walls:
                    if (y + 1, x) in corridor.walls:
                        if (y, x + 1) in corridor.walls: 
                            if (y, x - 1) in corridor.walls: 
                                layout[(y, x)] = H_V
                            else:
                                layout[(y, x)] = V_R
                        elif (y, x - 1)  in corridor.walls: 
                            layout[(y, x)] = V_L
                        else:
                            layout[(y, x)] = V
                    else:
                        if (y, x + 1) in corridor.walls: 
                            if (y, x - 1) in corridor.walls: 
                                layout[(y, x)] = H_T
                            else:
                                layout[(y, x)] = BLC
                        elif (y, x - 1) in corridor.walls: 
                            layout[(y, x)] = BRC
                        else:
                            layout[(y, x)] = V
                elif (y + 1, x) in corridor.walls:
                        if (y, x + 1) in corridor.walls: 
                            if (y, x - 1) in corridor.walls: 
                                layout[(y, x)] = H_B
                            else:
                                layout[(y, x)] = TLC
                        elif (y, x - 1) in corridor.walls: 
                            layout[(y, x)] = TRC
                        else:
                            layout[(y, x)] = V
                else:
                    layout[(y, x)] = H
        return layout
