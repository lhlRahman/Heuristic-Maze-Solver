import random
from typing import List, Tuple
from maze_solver.models.border import Border
from maze_solver.models.maze import Maze
from maze_solver.models.role import Role
from maze_solver.models.square import Square
from maze_solver.persistence.serializer import dump_squares
from pathlib import Path

def generate_maze_dfs(width: int, height: int) -> Maze:
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

def generate_maze_kruskal(width: int, height: int) -> Maze:
    maze = [[Square(row * width + col, row, col, Border.TOP | Border.BOTTOM | Border.LEFT | Border.RIGHT) 
             for col in range(width)] for row in range(height)]
    squares = []
    
    parent = {}
    rank = {}
    
    def find(v):
        if parent[v] != v:
            parent[v] = find(parent[v])
        return parent[v]
    
    def union(v1, v2):
        root1 = find(v1)
        root2 = find(v2)
        if root1 != root2:
            if rank[root1] > rank[root2]:
                parent[root2] = root1
            else:
                parent[root1] = root2
                if rank[root1] == rank[root2]:
                    rank[root2] += 1
    
    edges = []
    for y in range(height):
        for x in range(width):
            if x < width - 1:
                edges.append((x, y, x + 1, y))
            if y < height - 1:
                edges.append((x, y, x, y + 1))
    
    random.shuffle(edges)
    
    for y in range(height):
        for x in range(width):
            parent[(x, y)] = (x, y)
            rank[(x, y)] = 0
    
    for (x1, y1, x2, y2) in edges:
        if find((x1, y1)) != find((x2, y2)):
            union((x1, y1), (x2, y2))
            if x1 == x2:
                maze[min(y1, y2)][x1] = Square(maze[min(y1, y2)][x1].index, min(y1, y2), x1, maze[min(y1, y2)][x1].border & ~Border.BOTTOM)
                maze[max(y1, y2)][x2] = Square(maze[max(y1, y2)][x2].index, max(y1, y2), x2, maze[max(y1, y2)][x2].border & ~Border.TOP)
            else:
                maze[y1][min(x1, x2)] = Square(maze[y1][min(x1, x2)].index, y1, min(x1, x2), maze[y1][min(x1, x2)].border & ~Border.RIGHT)
                maze[y2][max(x1, x2)] = Square(maze[y2][max(x1, x2)].index, y2, max(x1, x2), maze[y2][max(x1, x2)].border & ~Border.LEFT)
    
    for row in maze:
        for square in row:
            squares.append(square)
    
    maze[0][0] = Square(maze[0][0].index, 0, 0, maze[0][0].border, Role.ENTRANCE)
    maze[height-1][width-1] = Square(maze[height-1][width-1].index, height-1, width-1, maze[height-1][width-1].border, Role.EXIT)
    
    squares[0] = maze[0][0]
    squares[-1] = maze[height-1][width-1]
    
    return Maze(squares=tuple(squares))

def generate_maze_prims(width: int, height: int) -> Maze:
    maze = [[Square(row * width + col, row, col, Border.TOP | Border.BOTTOM | Border.LEFT | Border.RIGHT) 
             for col in range(width)] for row in range(height)]
    squares = []

    walls = []
    start_x, start_y = 0, 0
    maze[start_y][start_x] = Square(maze[start_y][start_x].index, start_y, start_x, maze[start_y][start_x].border & ~Border.RIGHT & ~Border.BOTTOM)
    walls.append((start_x, start_y, 1, 0, Border.RIGHT, Border.LEFT))
    walls.append((start_x, start_y, 0, 1, Border.BOTTOM, Border.TOP))

    while walls:
        x, y, dx, dy, border1, border2 = random.choice(walls)
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and maze[ny][nx].border == (Border.TOP | Border.BOTTOM | Border.LEFT | Border.RIGHT):
            maze[y][x] = Square(maze[y][x].index, y, x, maze[y][x].border & ~border1)
            maze[ny][nx] = Square(maze[ny][nx].index, ny, nx, maze[ny][nx].border & ~border2)
            walls.append((nx, ny, 1, 0, Border.RIGHT, Border.LEFT))
            walls.append((nx, ny, 0, 1, Border.BOTTOM, Border.TOP))
            walls.append((nx, ny, -1, 0, Border.LEFT, Border.RIGHT))
            walls.append((nx, ny, 0, -1, Border.TOP, Border.BOTTOM))
        walls.remove((x, y, dx, dy, border1, border2))

    for row in maze:
        for square in row:
            squares.append(square)

    maze[0][0] = Square(maze[0][0].index, 0, 0, maze[0][0].border, Role.ENTRANCE)
    maze[height-1][width-1] = Square(maze[height-1][width-1].index, height-1, width-1, maze[height-1][width-1].border, Role.EXIT)

    squares[0] = maze[0][0]
    squares[-1] = maze[height-1][width-1]

    return Maze(squares=tuple(squares))


def main():
    width = int(input("Enter maze width: "))
    height = int(input("Enter maze height: "))
    print("Select maze generation algorithm:")
    print("1. Depth-First Search (DFS)")
    print("2. Kruskal's Algorithm")
    print("3. Prim's Algorithm")
    choice = int(input("Enter choice (1-3): "))

    if choice == 1:
        maze = generate_maze_dfs(width, height)
    elif choice == 2:
        maze = generate_maze_kruskal(width, height)
    elif choice == 3:
        maze = generate_maze_prims(width, height)
    else:
        print("Invalid choice")
        return

    path = Path("large_example.maze")
    dump_squares(maze.width, maze.height, maze.squares, path)

    print(f"Maze of size {width}x{height} generated and saved to {path}.")
    print(f"Entrance: {maze.squares[0]}")
    print(f"Exit: {maze.squares[-1]}")

if __name__ == "__main__":
    main()
