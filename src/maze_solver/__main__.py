import argparse
import pathlib

from maze_solver.models.maze import Maze
from maze_solver.graphs.solver import (
    solve_all_steps,
    animate_solution,
    bfs,
    dfs,
    dijkstra,
    greedy_best_first,
    wall_follower,
    dead_end_filling,
    recursive_backtracking
)
from maze_solver.view.renderer import SVGRenderer

def main() -> None:
    args = parse_args()
    maze = Maze.load(args.path)
    algorithm = args.algorithm

    if algorithm == 'a-star':
        solution_steps = solve_all_steps(maze)
    elif algorithm == 'bfs':
        solution_steps = bfs(maze, maze.entrance, maze.exit)
    elif algorithm == 'dfs':
        solution_steps = dfs(maze, maze.entrance, maze.exit)
    elif algorithm == 'dijkstra':
        solution_steps = dijkstra(maze, maze.entrance, maze.exit)
    elif algorithm == 'greedy':
        solution_steps = greedy_best_first(maze, maze.entrance, maze.exit)
    elif algorithm == 'wall-follower':
        solution_steps = wall_follower(maze, maze.entrance, maze.exit)
    elif algorithm == 'dead-end':
        solution_steps = dead_end_filling(maze, maze.entrance, maze.exit)
    elif algorithm == 'recursive-bt':
        solution_steps = recursive_backtracking(maze, maze.entrance, maze.exit)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    if solution_steps:
        if args.animation:
            animate_solution(maze, solution_steps, args.delay, args.direction)
        else:
            renderer = SVGRenderer()
            if args.direction == "bottom-up":
                solution_steps.reverse()
            svg = renderer.render_step(maze, solution_steps[-1])
            svg.preview()
    else:
        print("No solution found")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path, help="Path to the maze file")
    parser.add_argument(
        "--algorithm", choices=["a-star", "bfs", "dfs", "dijkstra", "greedy", "wall-follower", "dead-end", "recursive-bt"], default="a-star", help="Algorithm to use"
    )
    parser.add_argument(
        "--animation", action="store_true", help="Show an animated solution"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5, help="Delay between animation steps (in seconds)"
    )
    parser.add_argument(
        "--direction", choices=["top-down", "bottom-up"], default="top-down", help="Direction of the solution animation"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    main()
