import struct
import argparse
import pathlib
import webbrowser
from typing import List

from maze_solver.view.renderer import SVGRenderer
from maze_solver_wrapper import solve_maze as solve_maze_cpp, generate_svg, generate_animation
from maze_solver.graphs.solver import animate_solution, bfs, dead_end_filling, dfs, dijkstra, greedy_best_first, wall_follower, recursive_backtracking
from maze_solver.models.maze import Maze
from maze_solver.models.square import Square
from maze_solver.models.role import Role
from maze_solver.models.border import Border

def main() -> None:
    args = parse_args()
    if args.use_cpp:
        solve_maze_cpp_wrapper(args.path, args.algorithm, args.animation, args.delay, args.direction, args.output_dir)
    else:
        solve_maze_python_wrapper(args.path, args.output_dir, args.algorithm, args.animation, args.delay, args.direction)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path, help="Path to the maze file")
    parser.add_argument("--algorithm", choices=["bfs", "dfs", "dijkstra", "greedy", "wall-follower", "dead-end", "recursive-bt"], default="bfs", help="Algorithm to use")
    parser.add_argument("--animation", action="store_true", help="Show an animated solution")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between animation steps (in seconds)")
    parser.add_argument("--direction", choices=["top-down", "bottom-up"], default="top-down", help="Direction of the solution animation")
    parser.add_argument("--use_cpp", action="store_true", help="Use C++ solver instead of Python solver")
    parser.add_argument("--output_dir", type=pathlib.Path, help="Directory to save the output files", default=pathlib.Path("./output"))
    return parser.parse_args()

def solve_maze_cpp_wrapper(path, algorithm, animation, delay, direction, output_dir):
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the maze from file
    with open(path, 'rb') as f:
        header = f.read(13)  # Read the first 13 bytes for the header
        magic_number, format_version, width, height = struct.unpack('<4sBII', header)
        square_values = f.read()

    squares = []
    for i in range(width * height):
        row, column = divmod(i, width)
        index = i
        border, role = decompress(square_values[i])
        squares.append(Square(index, row, column, border, role))

    print(f"Maze dimensions: {width}x{height}")
    print(f"Number of squares: {len(squares)}")

    # Define start and goal positions
    start_row, start_col = 0, 0  # or any other logic to determine start
    goal_row, goal_col = height - 1, width - 1  # or any other logic to determine goal

    # Solve the maze using the C++ solver
    squares_array = (Square * len(squares))(*squares)  # Create a ctypes array of Square
    solution = solve_maze_cpp(width, height, squares_array, start_row, start_col, goal_row, goal_col, algorithm, animation, delay, direction)

    if animation:
        # Generate the SVG content for each step in C++
        generate_animation(solution, str(output_dir), delay, direction == "top-down")
    else:
        # Generate the SVG content in C++
        svg_file_path = output_dir / "solution.svg"
        generate_svg(solution, str(svg_file_path))

        # Open the SVG file in the browser
        webbrowser.open(f"file://{svg_file_path}")

def solve_maze_python_wrapper(maze_path: pathlib.Path, output_dir: pathlib.Path, algorithm: str, animation: bool, delay: float, direction: str) -> None:
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    maze = Maze.load(maze_path)
    print(f"Loaded maze with dimensions: {maze.width}x{maze.height}")
    print(f"Number of squares: {len(maze.squares)}")

    if algorithm == "bfs":
        solution_steps = bfs(maze, maze.entrance, maze.exit)
    elif algorithm == "dfs":
        solution_steps = dfs(maze, maze.entrance, maze.exit)
    elif algorithm == "dijkstra":
        solution_steps = dijkstra(maze, maze.entrance, maze.exit)
    elif algorithm == "greedy":
        solution_steps = greedy_best_first(maze, maze.entrance, maze.exit)
    elif algorithm == "wall-follower":
        solution_steps = wall_follower(maze, maze.entrance, maze.exit)
    elif algorithm == "dead-end":
        solution_steps = dead_end_filling(maze, maze.entrance, maze.exit)
    elif algorithm == "recursive-bt":
        solution_steps = recursive_backtracking(maze, maze.entrance, maze.exit)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    if solution_steps:
        if animation:
            animate_solution(maze, solution_steps, delay, direction)
        else:
            renderer = SVGRenderer()
            if direction == "bottom-up":
                solution_steps.reverse()
            svg = renderer.render_step(maze, solution_steps[-1])
            svg_file_path = output_dir / "solution.svg"
            with open(svg_file_path, 'w') as f:
                f.write(svg.xml_content)
            svg.preview()
    else:
        print("No solution found")

def decompress(square_value: int) -> tuple[Border, Role]:
    return Border(square_value & 0xf), Role(square_value >> 4)

if __name__ == "__main__":
    main()
