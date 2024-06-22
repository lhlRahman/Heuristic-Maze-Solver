import random
from typing import List
from maze_solver.models.border import Border
from maze_solver.models.maze import Maze
from maze_solver.models.role import Role
from maze_solver.models.square import Square
from maze_solver.persistence.serializer import dump_squares
from pathlib import Path

def generate_maze(width: int, height: int) -> Maze:
    maze = [[Square(row * width + col, row, col, Border.TOP | Border.BOTTOM | Border.LEFT | Border.RIGHT) 
             for col in range(width)] for row in range(height)]
    squares = []

    def carve_passages(cx: int, cy: int):
        directions = [(0, -1, Border.TOP, Border.BOTTOM), (1, 0, Border.RIGHT, Border.LEFT), 
                      (0, 1, Border.BOTTOM, Border.TOP), (-1, 0, Border.LEFT, Border.RIGHT)]
        stack = [(cx, cy)]
        
        while stack:
            (x, y) = stack[-1]
            current_square = maze[y][x]
            neighbors = []

            for dx, dy, border1, border2 in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and maze[ny][nx].border == (Border.TOP | Border.BOTTOM | Border.LEFT | Border.RIGHT):
                    neighbors.append((nx, ny, border1, border2))

            if neighbors:
                nx, ny, border1, border2 = random.choice(neighbors)
                new_current_square = Square(current_square.index, current_square.row, current_square.column, current_square.border & ~border1)
                next_square = maze[ny][nx]
                new_next_square = Square(next_square.index, next_square.row, next_square.column, next_square.border & ~border2)
                maze[y][x] = new_current_square
                maze[ny][nx] = new_next_square
                stack.append((nx, ny))
            else:
                stack.pop()
    
    carve_passages(0, 0)

    for row in maze:
        for square in row:
            squares.append(square)

    maze[0][0] = Square(maze[0][0].index, 0, 0, maze[0][0].border, Role.ENTRANCE)
    maze[height-1][width-1] = Square(maze[height-1][width-1].index, height-1, width-1, maze[height-1][width-1].border, Role.EXIT)

    squares[0] = maze[0][0]
    squares[-1] = maze[height-1][width-1]

    return Maze(squares=tuple(squares))


width, height = 100, 100
maze = generate_maze(width, height)
path = Path("large_example.maze")
dump_squares(maze.width, maze.height, maze.squares, path)

print(f"Maze of size {width}x{height} generated and saved to {path}.")
print(f"Entrance: {maze.squares[0]}")
print(f"Exit: {maze.squares[-1]}")
