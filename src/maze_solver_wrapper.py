import ctypes
from ctypes import c_bool, c_char_p, c_float, c_int, Structure, POINTER
from typing import List, Iterable

class SquareC(Structure):
    _fields_ = [
        ("row", c_int),
        ("column", c_int),
        ("index", c_int),
        ("border", c_int),
        ("role", c_int)
    ]

# Load the shared library
maze_solver_lib = ctypes.CDLL('src/maze_solver/libmaze_solver.dylib')

# Define the C functions
maze_solver_lib.solve_maze_c.argtypes = [c_int, c_int, POINTER(SquareC), c_int, c_int, c_int, c_int, c_char_p, c_bool, c_float, c_char_p]
maze_solver_lib.solve_maze_c.restype = None

maze_solver_lib.generate_html_c.argtypes = [POINTER(SquareC), c_int, c_char_p]
maze_solver_lib.generate_html_c.restype = None

maze_solver_lib.generate_html_animation_c.argtypes = [c_int, c_int, POINTER(SquareC), POINTER(c_int), c_int, c_char_p, c_float, c_bool]
maze_solver_lib.generate_html_animation_c.restype = None

def solve_maze(width, height, squares, start_row, start_col, goal_row, goal_col, algorithm, animation, delay, direction):
    # Construct Square instances correctly
    SquareArrayType = SquareC * len(squares)
    squares_array = SquareArrayType(*squares)
    
    steps = []
    maze_solver_lib.solve_maze_c(width, height, squares_array, start_row, start_col, goal_row, goal_col, algorithm.encode('utf-8'), animation, delay, direction.encode('utf-8'))
    
    if animation:
        # Collect the steps for animation
        steps = collect_animation_steps(width, height)
    else:
        steps = [squares_array]  # Final path

    return steps

def collect_animation_steps(width, height):
    # Simulate collecting steps from C++ (for demonstration purposes)
    steps = []
    for i in range(10):  # Simulate 10 steps
        step = (SquareC * (width * height))()
        for j in range(width * height):
            step[j] = SquareC(j // width, j % width, j, 0, 0)  # Fill with dummy data
        steps.append(step)
    return steps

def generate_html(path, output_file):
    SquareArrayType = SquareC * len(path)
    path_array = SquareArrayType(*path)
    maze_solver_lib.generate_html_c(path_array, len(path), output_file.encode('utf-8'))

def validate_steps(steps: List[List[SquareC]]) -> bool:
    for step in steps:
        if not isinstance(step, Iterable):
            print(f"Step {step} is not an iterable")
            return False
        if not all(isinstance(sq, SquareC) for sq in step):
            print(f"Step {step} contains non-SquareC elements")
            return False
    return True

def generate_html_animation(width, height, steps, output_dir, delay, top_down):
    steps_count = len(steps)
    steps_sizes = (c_int * steps_count)(*(len(step) for step in steps))
    steps_array = (SquareC * sum(len(step) for step in steps))()

    offset = 0
    for step in steps:
        for square in step:
            steps_array[offset] = square
            offset += 1
    
    maze_solver_lib.generate_html_animation_c(width, height, steps_array, steps_sizes, steps_count, output_dir.encode('utf-8'), delay, top_down)
