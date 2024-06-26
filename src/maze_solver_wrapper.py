import ctypes
from ctypes import c_int, c_float, c_bool, c_char_p, POINTER, Structure

class Square(Structure):
    _fields_ = [("row", c_int), ("column", c_int), ("index", c_int), ("border", c_int), ("role", c_int)]

# Load the shared library
maze_solver_lib = ctypes.CDLL('src/maze_solver/libmaze_solver.dylib')

# Define the C functions
maze_solver_lib.solve_maze_c.argtypes = [c_int, c_int, POINTER(Square), c_int, c_int, c_int, c_int, c_char_p, c_bool, c_float, c_char_p]
maze_solver_lib.solve_maze_c.restype = None

maze_solver_lib.generate_svg_c.argtypes = [POINTER(Square), c_int, c_char_p]
maze_solver_lib.generate_svg_c.restype = None

maze_solver_lib.generate_animation_c.argtypes = [POINTER(POINTER(Square)), POINTER(c_int), c_int, c_char_p, c_float, c_bool]
maze_solver_lib.generate_animation_c.restype = None

def solve_maze(width, height, squares, start_row, start_col, goal_row, goal_col, algorithm, animation, delay, direction):
    # Construct Square instances correctly
    squares_array = (Square * len(squares))(*[Square(s.row, s.column, s.index, s.border, s.role) for s in squares])
    maze_solver_lib.solve_maze_c(width, height, squares_array, start_row, start_col, goal_row, goal_col, algorithm.encode('utf-8'), animation, delay, direction.encode('utf-8'))

def generate_svg(path, output_file):
    path_array = (Square * len(path))(*path)
    maze_solver_lib.generate_svg_c(path_array, len(path), output_file.encode('utf-8'))

def generate_animation(steps, output_dir, delay, top_down):
    steps_count = len(steps)
    steps_sizes = (c_int * steps_count)(*(len(step) for step in steps))
    steps_array = (POINTER(Square) * steps_count)()
    for i, step in enumerate(steps):
        steps_array[i] = (Square * len(step))(*step)
    maze_solver_lib.generate_animation_c(steps_array, steps_sizes, steps_count, output_dir.encode('utf-8'), delay, top_down)
