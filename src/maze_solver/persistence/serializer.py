# serializer.py
import array
import pathlib
from typing import Iterator

from maze_solver.models.border import Border
from maze_solver.models.role import Role
from maze_solver.models.square import Square
from maze_solver.persistence.file_format import FileBody, FileHeader

FORMAT_VERSION: int = 1

def compress(square: Square) -> int:
    return (square.role << 4) | square.border.value

def decompress(square_value: int) -> tuple[Border, Role]:
    return Border(square_value & 0xf), Role(square_value >> 4)

def serialize(width: int, height: int, squares: tuple[Square, ...]) -> tuple[FileHeader, FileBody]:
    header = FileHeader(FORMAT_VERSION, width, height)
    body = FileBody(array.array("B", map(compress, squares)))
    return header, body

def dump_squares(width: int, height: int, squares: tuple[Square, ...], path: pathlib.Path) -> None:
    header, body = serialize(width, height, squares)
    with path.open(mode="wb") as file:
        header.write(file)
        body.write(file)

def load_squares(path: pathlib.Path) -> Iterator[Square]:
    print(f"Attempting to load maze from {path}")
    with path.open("rb") as file:
        header = FileHeader.read(file)
        if header.format_version != FORMAT_VERSION:
            raise ValueError(f"Unsupported file format version: {header.format_version}")
        body = FileBody.read(header, file)
        squares = list(deserialize(header, body))
        
        # Ensure entrance and exit are set
        if squares[0].role != Role.ENTRANCE:
            squares[0] = Square(squares[0].index, squares[0].row, squares[0].column, squares[0].border, Role.ENTRANCE)
        if squares[-1].role != Role.EXIT:
            squares[-1] = Square(squares[-1].index, squares[-1].row, squares[-1].column, squares[-1].border, Role.EXIT)
        
        return iter(squares)

def deserialize(header: FileHeader, body: FileBody) -> Iterator[Square]:
    for index, square_value in enumerate(body.square_values):
        row, column = divmod(index, header.width)
        border, role = decompress(square_value)
        yield Square(index, row, column, border, role)
