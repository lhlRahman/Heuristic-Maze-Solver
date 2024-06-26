# Heuristic-Maze-Solver

## Overview

 Heuristic-Maze-Solver is a Python project designed to solve complex mazes. It includes functionalities to generate, solve, and visualize mazes using various algorithms and techniques, leveraging both Python and C++ (dont work rn) for improved performance.

## Features

- **Maze Generation**: Create mazes of various sizes and complexities.
- **Maze Solving**: Implement different algorithms to find solutions to the generated mazes.
- **Visualization**: Render mazes and their solutions graphically.
- **Bindings**: Interface with C++ code using pybind11 for performance-critical parts.

## Installation

### Prerequisites

- Python 3.9 or higher
- CMake
- pybind11

### Steps

1. Clone the repository:
    ```sh
    git clone https://github.com/lhlRahman/Heuristic-Maze-Solver.git
    cd Heuristic-Maze-Solver
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```


3. Build the C++ extensions (dont work rn):
    ```sh
    mkdir build
    cd build
    cmake ..
    make
    ```

## Usage

### Command Line Interface

You can genrate mazes using maze.py
```sh
python maze.py
```

You can run the maze solver from the command line with the following syntax:

```sh
python -m maze_solver <maze_file> --algorithm <algorithm> --animation --delay <delay>
```

### Example Command

To solve the `large_example.maze` file using the BFS algorithm with an animation delay of 0.1 seconds, run:

```sh
python -m maze_solver large_example.maze --algorithm bfs --animation --delay 0.1
```

### Options

- `<maze_file>`: Path to the maze file.
- `--algorithm`: Algorithm to use for solving the maze (`bfs`, `dfs`, `dijkstra`, `greedy`, `wall-follower`, `dead-end`, `recursive-bt`).
- `--animation`: Show an animated solution.
- `--delay`: Delay between animation steps (in seconds).

## Project Structure

- `large_example.maze`: Example maze file.
- `make.py`: Script to build and run the project.
- `src/maze_solver/`: Main Python package for the maze solver.
- `src/maze_solver/graphs/`: Contains graph algorithms for maze solving.
- `src/maze_solver/models/`: Maze model definitions.
- `src/maze_solver/persistence/`: File format and serialization utilities.
- `src/maze_solver/view/`: Visualization components.
- `src/maze_solver.cpp`, `src/maze_solver.h`: C++ source and header files.
- `pybind11/`: Pybind11 library for C++ bindings.
- `.vscode/`: VSCode configuration files.
- `CMakeLists.txt`, `Makefile`: Build system files.

### Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push your branch.
4. Create a pull request to the main branch.
