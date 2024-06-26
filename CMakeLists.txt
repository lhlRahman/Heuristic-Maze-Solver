cmake_minimum_required(VERSION 3.10)
project(maze_solver)

set(CMAKE_CXX_STANDARD 11)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/src)

# Add the library
add_library(maze_solver SHARED
    src/maze_solver.cpp
    src/maze_solver.h
)

# Find Python
find_package(Python3 COMPONENTS Interpreter Development)
if (NOT Python3_FOUND)
    message(FATAL_ERROR "Python3 not found")
endif()

# Add pybind11
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG v2.9.0
)
FetchContent_MakeAvailable(pybind11)

# Add the bindings
pybind11_add_module(maze_solver_wrapper src/bindings.cpp)
target_link_libraries(maze_solver_wrapper PRIVATE maze_solver)

# Specify output directories
set_target_properties(maze_solver PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/src/maze_solver
)
set_target_properties(maze_solver_wrapper PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/src/maze_solver
)
