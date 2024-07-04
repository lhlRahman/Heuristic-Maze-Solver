import ctypes
from typing import List
import os
import sys

def find_library(lib_name):
    possible_locations = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'),
        os.getcwd(),
    ]

    for location in possible_locations:
        lib_path = os.path.join(location, lib_name)
        if os.path.exists(lib_path):
            return lib_path

    raise FileNotFoundError(f"Could not find {lib_name} in any of the expected locations")

# Debug information
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Script directory:", os.path.dirname(os.path.abspath(__file__)))
print("Parent directory:", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to find and load the library
try:
    dylib_path = find_library('libmaze_solver.dylib')
    print(f"Found library at: {dylib_path}")
    maze_solver_lib = ctypes.CDLL(dylib_path)
    print("Successfully loaded the library")
    print("Available functions in the library:")
    for name in dir(maze_solver_lib):
        if not name.startswith('_'):
            print(f"  {name}")
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Please ensure that libmaze_solver.dylib is built and located in the project directory.")
    sys.exit(1)

# Define the SquareC class
class SquareC(ctypes.Structure):
    _fields_ = [("row", ctypes.c_int),
                ("column", ctypes.c_int),
                ("index", ctypes.c_int),
                ("border", ctypes.c_int),
                ("role", ctypes.c_int)]

# Try to set up function signatures
try:
    maze_solver_lib.solve_maze.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(SquareC),
                                           ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                           ctypes.c_char_p, ctypes.c_bool, ctypes.c_float, ctypes.c_bool]
    maze_solver_lib.solve_maze.restype = ctypes.POINTER(ctypes.POINTER(SquareC))

    maze_solver_lib.generate_html.argtypes = [ctypes.POINTER(SquareC), ctypes.c_char_p]
    maze_solver_lib.generate_html.restype = None

    maze_solver_lib.generate_html_animation.argtypes = [ctypes.c_int, ctypes.c_int, 
                                                        ctypes.POINTER(ctypes.POINTER(SquareC)),
                                                        ctypes.c_char_p, ctypes.c_float, ctypes.c_bool]
    maze_solver_lib.generate_html_animation.restype = None
    
    print("Successfully set up function signatures")
except AttributeError as e:
    print(f"Error setting up function signatures: {e}")
    print("This likely means that one or more expected functions are not present in the library.")
    print("Please check that the C++ library has been compiled correctly and includes all necessary functions.")
    sys.exit(1)

def solve_maze(width: int, height: int, squares: List[SquareC], start_row: int, start_col: int, 
               goal_row: int, goal_col: int, algorithm: str, animation: bool, delay: float, 
               top_down: bool) -> List[List[SquareC]]:
    squares_array = (SquareC * len(squares))(*squares)
    result = maze_solver_lib.solve_maze(width, height, squares_array, start_row, start_col, 
                                        goal_row, goal_col, algorithm.encode('utf-8'), 
                                        animation, delay, top_down)
    steps = []
    i = 0
    while result[i]:
        step = [result[i][j] for j in range(width * height)]
        steps.append(step)
        i += 1
    return steps

def generate_html(squares: List[SquareC], output_path: str) -> None:
    squares_array = (SquareC * len(squares))(*squares)
    maze_solver_lib.generate_html(squares_array, output_path.encode('utf-8'))

def generate_html_animation(width: int, height: int, steps: List[List[SquareC]], 
                            output_path: str, delay: float, top_down: bool) -> None:
    steps_array = (ctypes.POINTER(SquareC) * len(steps))()
    for i, step in enumerate(steps):
        step_array = (SquareC * len(step))(*step)
        steps_array[i] = step_array
    maze_solver_lib.generate_html_animation(width, height, steps_array, 
                                            output_path.encode('utf-8'), delay, top_down)

print("maze_solver_wrapper.py loaded successfully")