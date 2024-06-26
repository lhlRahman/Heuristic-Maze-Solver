// bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "maze_solver.h"

namespace py = pybind11;

PYBIND11_MODULE(maze_solver_wrapper, m) {
    m.def("solve_maze", &solve_maze_c, "A function that solves the maze",
          py::arg("width"), py::arg("height"), py::arg("squares"),
          py::arg("start_row"), py::arg("start_col"), py::arg("goal_row"), py::arg("goal_col"),
          py::arg("algorithm"), py::arg("animation"), py::arg("delay"), py::arg("direction"));

    m.def("generate_svg", &generate_svg_c, "A function that generates an SVG from the solution path",
          py::arg("path"), py::arg("path_length"), py::arg("output_file"));

    m.def("generate_animation", &generate_animation_c, "A function that generates an animation from the solution steps",
          py::arg("steps"), py::arg("step_lengths"), py::arg("num_steps"), py::arg("output_dir"), py::arg("delay"), py::arg("top_down"));
}
