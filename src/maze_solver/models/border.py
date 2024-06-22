from enum import IntFlag

class Border(IntFlag):
    NONE = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 4
    LEFT = 8

    @property
    def corner(self) -> bool:
        return bin(self.value).count("1") == 2

    @property
    def intersection(self) -> bool:
        return bin(self.value).count("1") == 3

    @property
    def dead_end(self) -> bool:
        return bin(self.value).count("1") == 1
