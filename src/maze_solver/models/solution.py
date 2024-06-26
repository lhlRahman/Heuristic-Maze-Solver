# solution.py
from dataclasses import dataclass
from typing import Iterator, List

from maze_solver.models.square import Square

@dataclass(frozen=True)
class Solution:
    squares: List[Square]

    def __len__(self) -> int:
        return len(self.squares)

    def __iter__(self) -> Iterator[Square]:
        return iter(self.squares)
