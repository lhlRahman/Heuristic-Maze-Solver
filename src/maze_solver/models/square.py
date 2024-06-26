# square.py
from dataclasses import dataclass
from maze_solver.models.border import Border
from maze_solver.models.role import Role

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
