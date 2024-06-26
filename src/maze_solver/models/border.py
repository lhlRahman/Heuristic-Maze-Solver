# border.py
from enum import IntFlag

class Border(IntFlag):
    NONE = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 4
    LEFT = 8
