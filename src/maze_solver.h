#ifndef MAZE_SOLVER_H
#define MAZE_SOLVER_H

#include <vector>
#include <string>
#include <iostream>
#include <stdexcept>

struct Square {
    int row;
    int column;
    int index;
    int border;
    int role;

    bool operator<(const Square& other) const {
        return std::tie(row, column, index) < std::tie(other.row, other.column, other.index);
    }

    bool operator==(const Square& other) const {
        return row == other.row && column == other.column && index == other.index;
    }
};

class Maze {
public:
    int width;
    int height;
    std::vector<Square> squares;

    Maze(int w, int h, std::vector<Square> sq) : width(w), height(h), squares(sq) {}

    Square get_square(int row, int column) const {
        if (row < 0 || row >= height || column < 0 || column >= width) {
            std::cerr << "Index out of bounds: row=" << row << ", column=" << column << std::endl;
            throw std::out_of_range("Index out of bounds in get_square");
        }
        return squares.at(row * width + column);  // Use .at() for bounds checking
    }

    std::vector<Square> get_neighbors(const Square& square) const {
        std::vector<Square> neighbors;
        if (square.row > 0) neighbors.push_back(get_square(square.row - 1, square.column));
        if (square.row < height - 1) neighbors.push_back(get_square(square.row + 1, square.column));
        if (square.column > 0) neighbors.push_back(get_square(square.row, square.column - 1));
        if (square.column < width - 1) neighbors.push_back(get_square(square.row, square.column + 1));
        return neighbors;
    }
};

// C-compatible function signatures
extern "C" {
    void solve_maze_c(int width, int height, Square* squares, int start_row, int start_col, int goal_row, int goal_col, const char* algorithm, bool animation, float delay, const char* direction);
    void generate_svg_c(const Square* path, int path_size, const char* output_file);
    void generate_animation_c(const Square* steps, int* steps_sizes, int steps_count, const char* output_dir, float delay, bool top_down);
}

#endif // MAZE_SOLVER_H
