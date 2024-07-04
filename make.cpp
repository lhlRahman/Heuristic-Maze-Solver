#include <iostream>
#include <vector>
#include <fstream>
#include <random>
#include <chrono>
#include <algorithm>
#include <stack>
#include <queue>
#include <unordered_set>
#include <cstdint>
#include <array>

enum Border : uint8_t {
    NONE = 0,
    TOP = 1,
    RIGHT = 2,
    BOTTOM = 4,
    LEFT = 8,
    ALL = TOP | RIGHT | BOTTOM | LEFT
};

enum Role : uint8_t {
    ROLE_NONE = 0,
    ENTRANCE = 1,
    EXIT = 2
};

struct Square {
    uint32_t index;
    uint16_t row, column;
    Border border;
    Role role;

    Square() : index(0), row(0), column(0), border(Border::ALL), role(Role::ROLE_NONE) {}
    Square(uint32_t idx, uint16_t r, uint16_t c, Border b, Role rl = Role::ROLE_NONE) 
        : index(idx), row(r), column(c), border(b), role(rl) {}
};

class Maze {
public:
    std::vector<Square> squares;
    uint32_t width_, height_;

    Maze(uint32_t w, uint32_t h) : width_(w), height_(h), squares(w * h) {
        for (uint32_t y = 0; y < h; ++y) {
            for (uint32_t x = 0; x < w; ++x) {
                at(y, x) = Square(y * w + x, y, x, Border::ALL);
            }
        }
    }

    uint32_t width() const { return width_; }
    uint32_t height() const { return height_; }

    Square& at(uint32_t row, uint32_t col) {
        return squares[row * width_ + col];
    }

    const Square& at(uint32_t row, uint32_t col) const {
        return squares[row * width_ + col];
    }
};

inline Border operator|(Border lhs, Border rhs) {
    return static_cast<Border>(static_cast<uint8_t>(lhs) | static_cast<uint8_t>(rhs));
}

inline Border operator&(Border lhs, Border rhs) {
    return static_cast<Border>(static_cast<uint8_t>(lhs) & static_cast<uint8_t>(rhs));
}

inline Border operator~(Border border) {
    return static_cast<Border>(~static_cast<uint8_t>(border));
}

void dump_squares(const Maze& maze, const std::string& path) {
    std::ofstream ofs(path, std::ios::binary | std::ios::out);
    if (!ofs) {
        throw std::runtime_error("Failed to open file for writing");
    }

    const char MAGIC_NUMBER[4] = {'M', 'A', 'Z', 'E'};
    const uint8_t FORMAT_VERSION = 1;
    
    ofs.write(MAGIC_NUMBER, 4);
    ofs.write(reinterpret_cast<const char*>(&FORMAT_VERSION), sizeof(FORMAT_VERSION));
    ofs.write(reinterpret_cast<const char*>(&maze.width_), sizeof(maze.width_));
    ofs.write(reinterpret_cast<const char*>(&maze.height_), sizeof(maze.height_));

    for (const auto& square : maze.squares) {
        uint8_t compressed_square = (static_cast<uint8_t>(square.role) << 4) | static_cast<uint8_t>(square.border);
        ofs.write(reinterpret_cast<const char*>(&compressed_square), sizeof(compressed_square));
    }
}


Maze generate_maze_dfs(uint32_t width, uint32_t height) {
    Maze maze(width, height);
    std::stack<std::pair<uint32_t, uint32_t>> stack;
    std::mt19937 gen(std::random_device{}());

    static const std::array<std::pair<int32_t, int32_t>, 4> directions = {{{0, -1}, {1, 0}, {0, 1}, {-1, 0}}};
    static const std::array<Border, 4> borders = {Border::TOP, Border::RIGHT, Border::BOTTOM, Border::LEFT};

    auto carve_passages = [&](uint32_t cx, uint32_t cy) {
        stack.emplace(cx, cy);
        while (!stack.empty()) {
            auto [x, y] = stack.top();
            std::vector<uint8_t> unvisited_neighbors;

            for (uint8_t i = 0; i < 4; ++i) {
                uint32_t nx = x + directions[i].first;
                uint32_t ny = y + directions[i].second;
                if (nx < width && ny < height && maze.at(ny, nx).border == Border::ALL) {
                    unvisited_neighbors.push_back(i);
                }
            }

            if (!unvisited_neighbors.empty()) {
                uint8_t dir = unvisited_neighbors[std::uniform_int_distribution<>(0, unvisited_neighbors.size() - 1)(gen)];
                uint32_t nx = x + directions[dir].first;
                uint32_t ny = y + directions[dir].second;
                maze.at(y, x).border = maze.at(y, x).border & ~borders[dir];
                maze.at(ny, nx).border = maze.at(ny, nx).border & ~borders[(dir + 2) % 4];
                stack.emplace(nx, ny);
            } else {
                stack.pop();
            }
        }
    };

    carve_passages(0, 0);

    maze.at(0, 0).role = Role::ENTRANCE;
    maze.at(height - 1, width - 1).role = Role::EXIT;

    return maze;
}

class DisjointSet {
    std::vector<uint32_t> parent, rank;

public:
    DisjointSet(uint32_t size) : parent(size), rank(size, 0) {
        for (uint32_t i = 0; i < size; ++i) parent[i] = i;
    }

    uint32_t find(uint32_t x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }

    void unite(uint32_t x, uint32_t y) {
        x = find(x), y = find(y);
        if (x == y) return;
        if (rank[x] < rank[y]) std::swap(x, y);
        parent[y] = x;
        if (rank[x] == rank[y]) ++rank[x];
    }
};

Maze generate_maze_kruskal(uint32_t width, uint32_t height) {
    Maze maze(width, height);
    std::mt19937 gen(std::random_device{}());

    struct Edge {
        uint32_t x1, y1, x2, y2;
        Border border;
    };

    std::vector<Edge> edges;
    edges.reserve(2 * width * height - width - height);

    for (uint32_t y = 0; y < height; ++y) {
        for (uint32_t x = 0; x < width; ++x) {
            if (x < width - 1) edges.push_back({x, y, x + 1, y, Border::RIGHT});
            if (y < height - 1) edges.push_back({x, y, x, y + 1, Border::BOTTOM});
        }
    }

    std::shuffle(edges.begin(), edges.end(), gen);

    DisjointSet ds(width * height);

    for (const auto& edge : edges) {
        uint32_t id1 = edge.y1 * width + edge.x1;
        uint32_t id2 = edge.y2 * width + edge.x2;

        if (ds.find(id1) != ds.find(id2)) {
            ds.unite(id1, id2);
            maze.at(edge.y1, edge.x1).border = maze.at(edge.y1, edge.x1).border & ~edge.border;
            maze.at(edge.y2, edge.x2).border = maze.at(edge.y2, edge.x2).border & ~(edge.border == Border::RIGHT ? Border::LEFT : Border::TOP);
        }
    }

    maze.at(0, 0).role = Role::ENTRANCE;
    maze.at(height - 1, width - 1).role = Role::EXIT;

    return maze;
}

Maze generate_maze_prim(uint32_t width, uint32_t height) {
    Maze maze(width, height);
    std::mt19937 gen(std::random_device{}());

    static const std::array<std::pair<int32_t, int32_t>, 4> directions = {{{0, -1}, {1, 0}, {0, 1}, {-1, 0}}};
    static const std::array<Border, 4> borders = {Border::TOP, Border::RIGHT, Border::BOTTOM, Border::LEFT};

    std::vector<std::pair<uint32_t, uint32_t>> frontier;
    std::vector<std::vector<bool>> in_maze(height, std::vector<bool>(width, false));

    auto add_to_frontier = [&](uint32_t x, uint32_t y) {
        if (x < width && y < height && !in_maze[y][x]) {
            frontier.emplace_back(x, y);
            in_maze[y][x] = true;
        }
    };

    // Start with the cell at (0, 0)
    in_maze[0][0] = true;
    add_to_frontier(1, 0);
    add_to_frontier(0, 1);

    while (!frontier.empty()) {
        auto [x, y] = frontier[std::uniform_int_distribution<>(0, frontier.size() - 1)(gen)];
        frontier.erase(std::remove(frontier.begin(), frontier.end(), std::make_pair(x, y)), frontier.end());

        std::vector<uint8_t> neighbors;
        for (uint8_t i = 0; i < 4; ++i) {
            uint32_t nx = x + directions[i].first;
            uint32_t ny = y + directions[i].second;
            if (nx < width && ny < height && in_maze[ny][nx] && maze.at(ny, nx).border & borders[(i + 2) % 4]) {
                neighbors.push_back(i);
            }
        }

        if (!neighbors.empty()) {
            uint8_t dir = neighbors[std::uniform_int_distribution<>(0, neighbors.size() - 1)(gen)];
            uint32_t nx = x + directions[dir].first;
            uint32_t ny = y + directions[dir].second;
            maze.at(y, x).border = maze.at(y, x).border & ~borders[dir];
            maze.at(ny, nx).border = maze.at(ny, nx).border & ~borders[(dir + 2) % 4];
        }

        for (uint8_t i = 0; i < 4; ++i) {
            add_to_frontier(x + directions[i].first, y + directions[i].second);
        }
    }

    maze.at(0, 0).role = Role::ENTRANCE;
    maze.at(height - 1, width - 1).role = Role::EXIT;

    return maze;
}

int main() {
    uint32_t width, height;
    int choice;
    std::cout << "Enter maze width: ";
    std::cin >> width;
    std::cout << "Enter maze height: ";
    std::cin >> height;
    std::cout << "Select maze generation algorithm:\n";
    std::cout << "1. Depth-First Search (DFS)\n";
    std::cout << "2. Kruskal's Algorithm\n";
    std::cout << "3. Prim's Algorithm\n";
    std::cout << "Enter choice (1-3): ";
    std::cin >> choice;

    auto start = std::chrono::high_resolution_clock::now();

    Maze maze(width, height);
    switch (choice) {
        case 1:
            maze = generate_maze_dfs(width, height);
            break;
        case 2:
            maze = generate_maze_kruskal(width, height);
            break;
        case 3:
            maze = generate_maze_prim(width, height);
            break;
        default:
            std::cerr << "Invalid choice\n";
            return 1;
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;
    std::cout << "Maze generation took " << duration.count() << " seconds.\n";

    std::string path = "large_example.maze";
    dump_squares(maze, path);

    std::cout << "Maze of size " << width << "x" << height << " generated and saved to " << path << ".\n";
    return 0;
}