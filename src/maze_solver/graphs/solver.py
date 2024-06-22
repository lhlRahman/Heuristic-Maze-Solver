import heapq
from typing import Dict, List, Optional, Tuple
from maze_solver.models.border import Border
from maze_solver.models.maze import Maze
from maze_solver.models.solution import Solution
from maze_solver.models.square import Square

def heuristic(a: Square, b: Square) -> int:
    return abs(a.row - b.row) + abs(a.column - b.column)

def reconstruct_path(came_from: Dict[Square, Square], current: Square) -> List[Square]:
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    total_path.reverse()
    return total_path

def a_star_search(maze: Maze, start: Square, goal: Square) -> Optional[List[Square]]:
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from: Dict[Square, Square] = {}

    g_score = {square: float('inf') for square in maze.squares}
    g_score[start] = 0
    f_score = {square: float('inf') for square in maze.squares}
    f_score[start] = heuristic(start, goal)

    open_set_hash = {start}

    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)

        if current == goal:
            return reconstruct_path(came_from, current)

        neighbors = get_neighbors(maze, current)
        for neighbor in neighbors:
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)

    return None

def get_neighbors(maze: Maze, square: Square) -> List[Square]:
    neighbors = []
    directions = [
        (0, -1, Border.TOP, Border.BOTTOM),
        (1, 0, Border.RIGHT, Border.LEFT),
        (0, 1, Border.BOTTOM, Border.TOP),
        (-1, 0, Border.LEFT, Border.RIGHT),
    ]
    for dx, dy, own_border, neighbor_border in directions:
        nx, ny = square.column + dx, square.row + dy
        if 0 <= nx < maze.width and 0 <= ny < maze.height:
            neighbor = maze.squares[ny * maze.width + nx]
            if not (square.border & own_border) and not (neighbor.border & neighbor_border):
                neighbors.append(neighbor)
    return neighbors

def solve(maze: Maze) -> Optional[Solution]:
    start = maze.entrance
    goal = maze.exit
    path = a_star_search(maze, start, goal)
    if path:
        return Solution(squares=tuple(path))
    else:
        print("No path found")
        return None

def solve_all(maze: Maze) -> List[Solution]:
    solution = solve(maze)
    return [solution] if solution else []
