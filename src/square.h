// square.h
#ifndef SQUARE_H
#define SQUARE_H

struct Square {
    int row, column;
    int border; // Assuming border is an integer bitmask
    int role;   // Role of the square

    bool operator==(const Square& other) const {
        return row == other.row && column == other.column;
    }

    bool operator<(const Square& other) const {
        return row < other.row || (row == other.row && column < other.column);
    }
};

#endif // SQUARE_H
