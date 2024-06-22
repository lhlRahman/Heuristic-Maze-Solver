from dataclasses import dataclass
from enum import IntFlag, auto
from typing import Optional

class Border(IntFlag):
    NONE = 0
    TOP = auto()
    RIGHT = auto()
    BOTTOM = auto()
    LEFT = auto()

class Role(IntFlag):
    NONE = 0
    ENTRANCE = auto()
    EXIT = auto()

@dataclass(frozen=True)
class Square:
    index: int
    row: int
    column: int
    border: Border = Border.NONE
    role: Role = Role.NONE

    def __lt__(self, other):
        if not isinstance(other, Square):
            return NotImplemented
        return (self.row, self.column) < (other.row, other.column)
