from common.constants import *
from .entity import Player
from random import randint, choice


class Model:

    def __init__(self, level, matrix, rooms, start_room):
        self.level = level
        self.matrix = matrix
        self.rooms = rooms
        self._place_player(start_room)
        self._entities = []
        self._place_monsters(start_room)
        self.passed = False

    def handle_move(self, char):
        if char in 'awsd':
            self.handle_player_move(char)
            self.handle_enemies()

    def handle_player_move(self, char):
        new_y, new_x = self.player.y, self.player.x
        if char == 'w':
            new_y -= 1
        elif char == 'a':
            new_x -= 1
        elif char == 's':
            new_y += 1
        elif char == 'd':
            new_x += 1
        pos = (new_y, new_x)
        value = self.matrix.get(pos)
        if value is not None:
            if value[1] == EXIT:
                self.passed = True
            elif value[1] is None:
                self.matrix[pos][1] = PLAYER
                self.matrix[(self.player.y, self.player.x)][1] = None
                self.player.y = new_y
                self.player.x = new_x
        # elif (new_y, new_x) in self.gates:


    def _place_player(self, start):
        pos = choice(list(self.rooms[start].floor))
        self.player = Player(pos, PLAYER)
        self.matrix[pos][1] = PLAYER
        

    def _place_monsters(self, start):
        pass

    def entities(self):
        result = [(self.player.y, self.player.x, self.player.id)]
        for e in self._entities:
            result.append((e.y, e.x, e.id))
        return result
    
    
    def handle_enemies(self):
        pass