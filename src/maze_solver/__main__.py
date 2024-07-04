# __main__.py

import struct
import argparse
import pathlib
import webbrowser
from typing import List
import time
from pathlib import Path

from maze_solver.view.renderer import SVGRenderer
from maze_solver_wrapper import solve_maze, generate_html, generate_html_animation, SquareC
from maze_solver.graphs.solver import (
    animate_solution, bfs, dead_end_filling, dfs, dijkstra, greedy_best_first,
    wall_follower, recursive_backtracking, a_star_search_steps,
    tremaux_algorithm, bellman_ford_algorithm, lee_algorithm, genetic_algorithm,
    ant_colony_optimization, best_first_graph_search,
    wavefront_expansion, jump_point_search, fringe_search, iddfs
)
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
    parser.add_argument("--algorithm", choices=["bfs", "a-star", "dfs", "dijkstra", "greedy", "wall-follower", "dead-end", "recursive-bt", "tremaux", "bellman-ford", "lee", "genetic", "ant-colony", "best-first", "wavefront", "jump-point", "fringe", "iddfs"], default="bfs", help="Algorithm to use")
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

    print(f"Magic number: {magic_number}")
    print(f"Format version: {format_version}")
    print(f"Width: {width}, Height: {height}")

    squares = []
    for i in range(width * height):
        row, column = divmod(i, width)
        index = i
        border, role = decompress(square_values[i])
        squares.append(SquareC(row, column, index, border, role))

    print(f"Number of squares read: {len(squares)}")

    # Define start and goal positions
    start_row, start_col = 0, 0
    goal_row, goal_col = height - 1, width - 1

    # Solve the maze using the C++ solver
    steps = solve_maze(width, height, squares, start_row, start_col, goal_row, goal_col, 
                       algorithm, animation, delay, direction)

    if animation:
        # Generate the HTML content for animation
        generate_html_animation(width, height, steps, str(output_dir), delay, direction == "top-down")
        html_file_path = output_dir / "animation.html"
    else:
        # Generate the HTML content for the final solution
        html_file_path = output_dir / "solution.html"
        generate_html(steps[-1], str(html_file_path))

    # Open the HTML file in the browser
    webbrowser.open(f"file://{html_file_path.resolve()}")

def solve_maze_python_wrapper(maze_path: pathlib.Path, output_dir: pathlib.Path, algorithm: str, animation: bool, delay: float, direction: str, test = False) -> None:
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
    elif algorithm == "a-star":
        solution_steps = a_star_search_steps(maze, maze.entrance, maze.exit)
    elif algorithm == "tremaux":
        solution_steps = tremaux_algorithm(maze, maze.entrance, maze.exit)
    elif algorithm == "bellman-ford":
        solution_steps = bellman_ford_algorithm(maze, maze.entrance, maze.exit)
    elif algorithm == "lee":
        solution_steps = lee_algorithm(maze, maze.entrance, maze.exit)
    elif algorithm == "genetic":
        solution_steps = genetic_algorithm(maze, maze.entrance, maze.exit)
    elif algorithm == "ant-colony":
        solution_steps = ant_colony_optimization(maze, maze.entrance, maze.exit)
    elif algorithm == "best-first":
        solution_steps = best_first_graph_search(maze, maze.entrance, maze.exit)
    elif algorithm == "wavefront":
        solution_steps = wavefront_expansion(maze, maze.entrance, maze.exit)
    elif algorithm == "jump-point":
        solution_steps = jump_point_search(maze, maze.entrance, maze.exit)
    elif algorithm == "fringe":
        solution_steps = fringe_search(maze, maze.entrance, maze.exit)
    elif algorithm == "iddfs":
        solution_steps = iddfs(maze, maze.entrance, maze.exit)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    if solution_steps and not test:
        renderer = SVGRenderer()
        if animation:
            animate_solution(maze, solution_steps, delay, direction)
        else:
            # Render the final step to get the complete solution
            final_solution_step = solution_steps[-(len(solution_steps) - 1)]
            svg_content = renderer.render(maze, final_solution_step).xml_content
            
            # Generate HTML to embed the SVG and open it in the browser
            html_content = f"""\
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Maze Solution</title>
            </head>
            <body>
                {svg_content}
            </body>
            </html>
            """
            html_file_path = output_dir / "solution.html"
            with open(html_file_path, 'w') as html_file:
                html_file.write(html_content)
            webbrowser.open(f"file://{html_file_path.resolve()}")
        
    elif test:
        print("solved: " + algorithm)
    else:
        print("No solution found")

def decompress(square_value: int) -> tuple[Border, Role]:
    return Border(square_value & 0xf), Role(square_value >> 4)

def time_algorithms(maze_path: Path, output_dir: Path, animation: bool, delay: float, direction: str) -> None:
    algorithms = [
        "bfs", "a-star", "dfs", "dijkstra", "greedy", "wall-follower", 
        "dead-end", "tremaux", "lee", 
        "best-first", "wavefront", "jump-point", 
        "fringe"]
    
    results = []
    
    for algorithm in algorithms:
        start_time = time.time()
        try:
            print(f"Timing {algorithm} algorithm")
            solve_maze_python_wrapper(maze_path, output_dir, algorithm, animation, delay, direction, True)
            elapsed_time = time.time() - start_time
            print(f"{algorithm}: {elapsed_time:.2f} seconds")
            results.append((algorithm, elapsed_time))
        except Exception as e:
            results.append((algorithm, float('inf')))  # Use inf to indicate failure
            print(f"{algorithm}: Failed with error: {e}")

    # Sort results by elapsed time
    results.sort(key=lambda x: x[1])

    # Print sorted results
    for algorithm, elapsed_time in results:
        if elapsed_time == float('inf'):
            print(f"{algorithm}: Failed")
        else:
            print(f"{algorithm}: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    time_algorithms(Path("large_example.maze"), Path("output"), False, 0.5, "top-down")