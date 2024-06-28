// maze.h
#ifndef MAZE_H
#define MAZE_H

#include <vector>
#include <map>
#include "square.h"

class Maze {
public:
    int width, height;
    std::vector<Square> squares;

    Maze(int w, int h, const std::vector<Square>& s) : width(w), height(h), squares(s) {}

    Square get_square(int row, int col) const {
        return squares[row * width + col];
    }

    std::vector<Square> get_neighbors(const Square& square) const {
        std::vector<Square> neighbors;
        // Example of 4-connectivity (up, right, down, left)
        int row = square.row, col = square.column;
        if (row > 0) neighbors.push_back(get_square(row - 1, col)); // up
        if (row < height - 1) neighbors.push_back(get_square(row + 1, col)); // down
        if (col > 0) neighbors.push_back(get_square(row, col - 1)); // left
        if (col < width - 1) neighbors.push_back(get_square(row, col + 1)); // right
        return neighbors;
    }
};

#endif // MAZE_H
