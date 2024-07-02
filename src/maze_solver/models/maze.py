# maze.py
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import List, Iterator

from maze_solver.models.role import Role
from maze_solver.models.square import Square

@dataclass(frozen=True)
class Maze:
    squares: List[Square]

    @classmethod
    def load(cls, path: Path) -> "Maze":
        from maze_solver.persistence.serializer import load_squares
        squares = list(load_squares(path))
        if not squares:
            raise ValueError("The maze file is empty or malformed")
        return cls(squares)

    def dump(self, path: Path) -> None:
        from maze_solver.persistence.serializer import dump_squares
        dump_squares(self.width, self.height, self.squares, path)

    @cached_property
    def width(self) -> int:
        return max(square.column for square in self.squares) + 1

    @cached_property
    def height(self) -> int:
        return max(square.row for square in self.squares) + 1

    @cached_property
    def entrance(self) -> Square:
        return self._get_square_by_role(Role.ENTRANCE)

    @cached_property
    def exit(self) -> Square:
        return self._get_square_by_role(Role.EXIT)

    def _get_square_by_role(self, role: Role) -> Square:
        for square in self.squares:
            if square.role is role:
                return square
        raise ValueError(f"No square with role {role}")

    def __iter__(self) -> Iterator[Square]:
        return iter(self.squares)
