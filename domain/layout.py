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
                                layout[(y, x)] = '╋' #1
                            else:
                                layout[(y, x)] = '┣'#2
                        elif (y, x - 1)  in corridor.walls: 
                            layout[(y, x)] = '┫'
                        else:
                            layout[(y, x)] = '┃'
                    else:
                        if (y, x + 1) in corridor.walls: 
                            if (y, x - 1) in corridor.walls: 
                                layout[(y, x)] = '┻'
                            else:
                                layout[(y, x)] = '┗'
                        elif (y, x - 1) in corridor.walls: 
                            layout[(y, x)] = '┛'
                        else:
                            layout[(y, x)] = '┃'
                elif (y + 1, x) in corridor.walls:
                        if (y, x + 1) in corridor.walls: 
                            if (y, x - 1) in corridor.walls: 
                                layout[(y, x)] = '┳'
                            else:
                                layout[(y, x)] = '┏'
                        elif (y, x - 1) in corridor.walls: 
                            layout[(y, x)] = '┓'
                        else:
                            layout[(y, x)] = '┃'
                else:
                    layout[(y, x)] = '━'
        return layout
