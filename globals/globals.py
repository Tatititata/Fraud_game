# class GlobalCounter:
#     _value = 0
    
#     @property
#     def value(self):
#         res = self._value
#         self._value += 1
#         if self._value > 65:
#             self._value = 0
#         return res

import sys
_counter = 0
def global_counter():
    global _counter
    res = _counter
    _counter += 1
    if _counter > 60:
        clear_screen()
        _counter = 0
    return res

def clear_screen():
    for i in range(63):
        sys.stdout.write(f'\033[{1 + i};{104}H\033[K')