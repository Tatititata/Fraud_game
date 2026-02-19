
# ┏  # U+250F BOX DRAWINGS HEAVY DOWN AND RIGHT
# ┓  # U+2513 BOX DRAWINGS HEAVY DOWN AND LEFT
# ┗  # U+2517 BOX DRAWINGS HEAVY UP AND RIGHT  
# ┛  # U+251B BOX DRAWINGS HEAVY UP AND LEFT
# ┃  # U+2503 BOX DRAWINGS HEAVY VERTICAL
# ━  # U+2501 BOX DRAWINGS HEAVY HORIZONTAL
# ┣  # U+2523 BOX DRAWINGS HEAVY VERTICAL AND RIGHT
# ┫  # U+252B BOX DRAWINGS HEAVY VERTICAL AND LEFT
# ┳  # U+2533 BOX DRAWINGS HEAVY DOWN AND HORIZONTAL
# ┻  # U+253B BOX DRAWINGS HEAVY UP AND HORIZONTAL
# ╋  # U+254B BOX DRAWINGS HEAVY VERTICAL AND HORIZONTAL


EXIT =  '█' #'>'

ROOMS = 9
OFFSET = 0
MIN_ROOM_WIDTH = 8 + OFFSET
MAX_ROOM_WIDTH = 20 + OFFSET
MIN_ROOM_HEIGHT = 6 + OFFSET
MAX_ROOM_HEIGHT = 15 + OFFSET

MIN_ROOM_AREA = MIN_ROOM_WIDTH * MIN_ROOM_HEIGHT
MAX_ROOM_AREA = MAX_ROOM_WIDTH * MAX_ROOM_HEIGHT

WIDTH = 100
HEIGHT = 50
STATISTICS = ("treasure",
              "level_reached",
              "monsters_killed",
              "food_eaten",
              "potions_drunk",
              "scrolls_read",
              "hits_dealt",
              "hits_taken",
              "cells_moved",
              "dexterity_used",
              "dexterity_added",
              "strength_used",
              "strength_added",
              "health_used",
              "health_added"
              )





