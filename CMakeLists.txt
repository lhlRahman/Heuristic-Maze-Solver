cmake_minimum_required(VERSION 3.10)
project(maze_solver)

set(CMAKE_CXX_STANDARD 11)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/src)

# Add the library
add_library(maze_solver SHARED
    src/maze_solver.cpp
    src/maze_solver.h
    src/square.h
)

# Specify output directories
set_target_properties(maze_solver PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/src/maze_solver
)
