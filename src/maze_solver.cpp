// maze_solver.cpp
#include <iostream>
#include <vector>
#include <queue>
#include <stack>
#include <map>
#include <unordered_map>
#include <set>
#include <unordered_set>
#include <algorithm>
#include <cmath>
#include <random>
#include <chrono>
#include <functional>
#include <limits>
#include <fstream>
#include <sstream>
#include <bitset>
#include <optional>

// Structure definitions

struct Square {
    int row, column, index;
    int border;
    int role;

    bool operator==(const Square& other) const {
        return row == other.row && column == other.column;
    }

    bool operator<(const Square& other) const {
        return std::tie(row, column) < std::tie(other.row, other.column);
    }
};

std::vector<std::vector<Square>> g_steps;
int g_step_count = 0;

// Custom hash function for Square
namespace std {
    template <>
    struct hash<Square> {
        size_t operator()(const Square& s) const {
            return hash<int>()(s.row) ^ hash<int>()(s.column);
        }
    };
}

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
        const int dx[] = {0, 1, 0, -1};
        const int dy[] = {1, 0, -1, 0};
        for (int i = 0; i < 4; ++i) {
            int new_row = square.row + dy[i];
            int new_col = square.column + dx[i];
            if (new_row >= 0 && new_row < height && new_col >= 0 && new_col < width) {
                if (!(square.border & (1 << i))) {
                    neighbors.push_back(get_square(new_row, new_col));
                }
            }
        }
        return neighbors;
    }
};

// Helper functions
std::vector<Square> reconstruct_path(const std::unordered_map<Square, Square>& came_from, const Square& start, const Square& current) {
    std::vector<Square> path;
    Square current_node = current;
    while (!(current_node == start)) {
        path.push_back(current_node);
        current_node = came_from.at(current_node);
    }
    path.push_back(start);
    std::reverse(path.begin(), path.end());
    return path;
}


// Algorithm implementations
std::vector<Square> bfs(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    std::queue<Square> frontier;
    frontier.push(start);
    std::unordered_map<Square, Square> came_from;
    came_from[start] = start;

    while (!frontier.empty()) {
        Square current = frontier.front();
        frontier.pop();

        if (current == goal) {
            auto path = reconstruct_path(came_from, start, goal);
            steps.push_back(path);
            return path;
        }

        for (const Square& next : maze.get_neighbors(current)) {
            if (came_from.find(next) == came_from.end()) {
                frontier.push(next);
                came_from[next] = current;
                steps.push_back(reconstruct_path(came_from, start, next));
            }
        }
    }

    return {};
}

// DFS implementation
std::vector<Square> dfs(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    std::stack<Square> frontier;
    frontier.push(start);
    std::unordered_map<Square, Square> came_from;
    came_from[start] = start;

    while (!frontier.empty()) {
        Square current = frontier.top();
        frontier.pop();

        if (current == goal) {
            auto path = reconstruct_path(came_from, start, goal);
            steps.push_back(path);
            return path;
        }

        for (const Square& next : maze.get_neighbors(current)) {
            if (came_from.find(next) == came_from.end()) {
                frontier.push(next);
                came_from[next] = current;
                steps.push_back(reconstruct_path(came_from, start, next));
            }
        }
    }

    return {};
}

// Dijkstra implementation
std::vector<Square> dijkstra(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    auto compare = [](const std::pair<int, Square>& a, const std::pair<int, Square>& b) {
        return a.first > b.first;
    };
    std::priority_queue<std::pair<int, Square>, std::vector<std::pair<int, Square>>, decltype(compare)> frontier(compare);
    frontier.push({0, start});
    std::unordered_map<Square, Square> came_from;
    std::unordered_map<Square, int> cost_so_far;
    came_from[start] = start;
    cost_so_far[start] = 0;

    while (!frontier.empty()) {
        Square current = frontier.top().second;
        frontier.pop();

        if (current == goal) {
            auto path = reconstruct_path(came_from, start, goal);
            steps.push_back(path);
            return path;
        }

        for (const Square& next : maze.get_neighbors(current)) {
            int new_cost = cost_so_far[current] + 1;
            if (cost_so_far.find(next) == cost_so_far.end() || new_cost < cost_so_far[next]) {
                cost_so_far[next] = new_cost;
                frontier.push({new_cost, next});
                came_from[next] = current;
                steps.push_back(reconstruct_path(came_from, start, next));
            }
        }
    }

    return {};
}

// A* implementation
std::vector<Square> a_star(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    auto heuristic = [](const Square& a, const Square& b) {
        return std::abs(a.row - b.row) + std::abs(a.column - b.column);
    };

    auto compare = [](const std::pair<int, Square>& a, const std::pair<int, Square>& b) {
        return a.first > b.first;
    };

    std::priority_queue<std::pair<int, Square>, std::vector<std::pair<int, Square>>, decltype(compare)> frontier(compare);
    frontier.push({0, start});
    std::unordered_map<Square, Square> came_from;
    std::unordered_map<Square, int> cost_so_far;
    came_from[start] = start;
    cost_so_far[start] = 0;

    while (!frontier.empty()) {
        Square current = frontier.top().second;
        frontier.pop();

        if (current == goal) {
            auto path = reconstruct_path(came_from, start, goal);
            steps.push_back(path);
            return path;
        }

        for (const Square& next : maze.get_neighbors(current)) {
            int new_cost = cost_so_far[current] + 1;
            if (cost_so_far.find(next) == cost_so_far.end() || new_cost < cost_so_far[next]) {
                cost_so_far[next] = new_cost;
                int priority = new_cost + heuristic(next, goal);
                frontier.push({priority, next});
                came_from[next] = current;
                steps.push_back(reconstruct_path(came_from, start, next));
            }
        }
    }

    return {};
}

// Greedy Best-First Search implementation
std::vector<Square> greedy_best_first(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    auto heuristic = [](const Square& a, const Square& b) {
        return std::abs(a.row - b.row) + std::abs(a.column - b.column);
    };

    auto compare = [](const std::pair<int, Square>& a, const std::pair<int, Square>& b) {
        return a.first > b.first;
    };

    std::priority_queue<std::pair<int, Square>, std::vector<std::pair<int, Square>>, decltype(compare)> frontier(compare);
    frontier.push({heuristic(start, goal), start});
    std::unordered_map<Square, Square> came_from;
    came_from[start] = start;

    while (!frontier.empty()) {
        Square current = frontier.top().second;
        frontier.pop();

        if (current == goal) {
            auto path = reconstruct_path(came_from, start, goal);
            steps.push_back(path);
            return path;
        }

        for (const Square& next : maze.get_neighbors(current)) {
            if (came_from.find(next) == came_from.end()) {
                int priority = heuristic(next, goal);
                frontier.push({priority, next});
                came_from[next] = current;
                steps.push_back(reconstruct_path(came_from, start, next));
            }
        }
    }

    return {};
}

// Wall Follower implementation
std::vector<Square> wall_follower(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    std::vector<Square> path;
    Square current = start;
    int direction = 0; // 0: right, 1: down, 2: left, 3: up
    const int dx[] = {0, 1, 0, -1};
    const int dy[] = {1, 0, -1, 0};

    while (!(current == goal)) {
        path.push_back(current);
        steps.push_back(path);

        int left_dir = (direction + 3) % 4;
        int new_row = current.row + dy[left_dir];
        int new_col = current.column + dx[left_dir];

        if (new_row >= 0 && new_row < maze.height && new_col >= 0 && new_col < maze.width &&
            !(current.border & (1 << left_dir))) {
            direction = left_dir;
            current = maze.get_square(new_row, new_col);
        }
        else if (!(current.border & (1 << direction))) {
            new_row = current.row + dy[direction];
            new_col = current.column + dx[direction];
            current = maze.get_square(new_row, new_col);
        }
        else {
            direction = (direction + 1) % 4;
        }
    }

    path.push_back(goal);
    steps.push_back(path);
    return path;
}

// Dead-end Filling implementation
std::vector<Square> dead_end_filling(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    Maze new_maze = maze;
    bool changed;
    do {
        changed = false;
        for (int i = 0; i < new_maze.height; ++i) {
            for (int j = 0; j < new_maze.width; ++j) {
                Square& square = new_maze.squares[i * new_maze.width + j];
                if (!(square == start) && !(square == goal) && std::bitset<4>(square.border).count() == 3) {
                    square.border = 15; // Mark as filled
                    changed = true;
                }
            }
        }
    } while (changed);

    return dijkstra(new_maze, start, goal, steps);
}

// Recursive Backtracking implementation
std::vector<Square> recursive_backtracking(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    std::vector<Square> path;
    std::set<Square> visited;

    std::function<bool(const Square&)> backtrack = [&](const Square& square) {
        if (square == goal) {
            path.push_back(square);
            steps.push_back(path);
            return true;
        }
        visited.insert(square);
        path.push_back(square);
        steps.push_back(path);

        for (const Square& neighbor : maze.get_neighbors(square)) {
            if (visited.find(neighbor) == visited.end()) {
                if (backtrack(neighbor)) {
                    return true;
                }
            }
        }

        path.pop_back();
        steps.push_back(path);
        return false;
    };

    backtrack(start);
    return path;
}

// Jump Point Search implementation
std::vector<Square> jump_point_search(const Maze& maze, const Square& start, const Square& goal, std::vector<std::vector<Square>>& steps) {
    auto heuristic = [](const Square& a, const Square& b) {
        return std::max(std::abs(a.row - b.row), std::abs(a.column - b.column));
    };

    auto identify_successors = [&](const Square& node, const Square& parent) {
        std::vector<Square> successors;
        int dx = node.column - parent.column;
        int dy = node.row - parent.row;

        // Implement diagonal and straight movement pruning rules
        // This is a simplified version and can be expanded for better performance

        for (const Square& neighbor : maze.get_neighbors(node)) {
            int new_dx = neighbor.column - node.column;
            int new_dy = neighbor.row - node.row;

            if ((new_dx == dx && new_dy == dy) || 
                (new_dx != 0 && new_dy != 0 && (maze.get_square(node.row, neighbor.column).border & 15) == 0 && (maze.get_square(neighbor.row, node.column).border & 15) == 0)) {
                successors.push_back(neighbor);
            }
        }

        return successors;
    };

    std::function<std::optional<Square>(int, int, int, int)> jump = [&](int x, int y, int dx, int dy) -> std::optional<Square> {
        int next_x = x + dx;
        int next_y = y + dy;

        if (!maze.get_square(next_y, next_x).border) {
            return std::nullopt;
        }

        Square next_square = maze.get_square(next_y, next_x);

        if (next_square == goal) {
            return next_square;
        }

        // Check for forced neighbors
        // This is a simplified check and can be expanded for better performance
        for (const Square& neighbor : maze.get_neighbors(next_square)) {
            Square current = maze.get_square(y, x);
            // Use the '==' operator and invert its logic to simulate '!='
            if (!(neighbor == current) && !neighbor.border) {
                return next_square;
            }
        }

        // Recursively apply jump in the direction of motion
        if (dx != 0 && dy != 0) {
            if (jump(next_x, next_y, dx, 0) || jump(next_x, next_y, 0, dy)) {
                return next_square;
            }
        }

        if (dx != 0 || dy != 0) {
            return jump(next_x, next_y, dx, dy);
        }

        return std::nullopt;
    };

    std::priority_queue<std::pair<int, Square>, std::vector<std::pair<int, Square>>, std::greater<>> open_set;
    std::unordered_map<Square, Square> came_from;
    std::unordered_map<Square, int> g_score;

    open_set.push({0, start});
    g_score[start] = 0;

    while (!open_set.empty()) {
        Square current = open_set.top().second;
        open_set.pop();

        if (current == goal) {
            auto path = reconstruct_path(came_from, start, goal);
            steps.push_back(path);
            return path;
        }

        for (const Square& successor : identify_successors(current, came_from[current])) {
            auto jump_point = jump(successor.column, successor.row, successor.column - current.column, successor.row - current.row);
            if (jump_point) {
                int tentative_g_score = g_score[current] + heuristic(current, *jump_point);
                if (g_score.find(*jump_point) == g_score.end() || tentative_g_score < g_score[*jump_point]) {
                    came_from[*jump_point] = current;
                    g_score[*jump_point] = tentative_g_score;
                    int f_score = tentative_g_score + heuristic(*jump_point, goal);
                    open_set.push({f_score, *jump_point});
                    steps.push_back(reconstruct_path(came_from, start, *jump_point));
                }
            }
        }
    }

    return {};
}

std::vector<Square> bidirectional_search(const Maze& maze, const Square& start, const Square& goal) {
    std::queue<Square> queue_start, queue_goal;
    std::unordered_map<Square, Square> came_from_start, came_from_goal;
    std::unordered_set<Square> visited_start, visited_goal;

    queue_start.push(start);
    queue_goal.push(goal);
    came_from_start[start] = start;
    came_from_goal[goal] = goal;
    visited_start.insert(start);
    visited_goal.insert(goal);

    while (!queue_start.empty() && !queue_goal.empty()) {
        // Expand from start
        Square current_start = queue_start.front();
        queue_start.pop();

        for (const Square& next : maze.get_neighbors(current_start)) {
            if (visited_start.find(next) == visited_start.end()) {
                queue_start.push(next);
                visited_start.insert(next);
                came_from_start[next] = current_start;

                if (visited_goal.find(next) != visited_goal.end()) {
                    // Path found
                    std::vector<Square> path_start = reconstruct_path(came_from_start, start, next);
                    std::vector<Square> path_goal = reconstruct_path(came_from_goal, goal, next);
                    std::reverse(path_goal.begin(), path_goal.end());
                    path_start.insert(path_start.end(), path_goal.begin() + 1, path_goal.end());
                    return path_start;
                }
            }
        }

        // Expand from goal
        Square current_goal = queue_goal.front();
        queue_goal.pop();

        for (const Square& next : maze.get_neighbors(current_goal)) {
            if (visited_goal.find(next) == visited_goal.end()) {
                queue_goal.push(next);
                visited_goal.insert(next);
                came_from_goal[next] = current_goal;

                if (visited_start.find(next) != visited_start.end()) {
                    // Path found
                    std::vector<Square> path_start = reconstruct_path(came_from_start, start, next);
                    std::vector<Square> path_goal = reconstruct_path(came_from_goal, goal, next);
                    std::reverse(path_goal.begin(), path_goal.end());
                    path_start.insert(path_start.end(), path_goal.begin() + 1, path_goal.end());
                    return path_start;
                }
            }
        }

        g_steps.push_back(reconstruct_path(came_from_start, start, current_start));
        g_steps.push_back(reconstruct_path(came_from_goal, goal, current_goal));
    }

    return {}; // No path found
}

// HTML generation functions
void generate_html(const std::vector<Square>& path, const std::string& filename) {
    std::ofstream html_file(filename);
    int square_size = 10;
    int width = 50 * square_size;
    int height = 50 * square_size;

    html_file << "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
              << "<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
              << "<title>Maze Solution</title>\n</head>\n<body>\n"
              << "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"" << width << "\" height=\"" << height << "\">\n";

    for (const Square& square : path) {
        html_file << "<rect x=\"" << square.column * square_size << "\" y=\"" << square.row * square_size
                  << "\" width=\"" << square_size << "\" height=\"" << square_size << "\" fill=\"black\" />\n";
    }

    html_file << "</svg>\n</body>\n</html>\n";
    html_file.close();
}

void generate_html_animation(const std::vector<std::vector<Square>>& steps, const Maze& maze, const std::string& output_file, float delay, bool top_down) {
    std::ofstream html_file(output_file);
    int square_size = 10;
    int width = maze.width * square_size;
    int height = maze.height * square_size;

    html_file << "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
              << "<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
              << "<title>Maze Solution Animation</title>\n<style>\n"
              << "svg { display: none; }\n"
              << "svg.active { display: block; }\n"
              << "</style>\n<script>\n"
              << "let currentStep = 0;\n"
              << "const steps = " << steps.size() << ";\n"
              << "const delay = " << (delay * 1000) << ";\n"
              << "function showNextStep() {\n"
              << "  const svgs = document.querySelectorAll('svg');\n"
              << "  svgs[currentStep].classList.remove('active');\n"
              << "  currentStep = (currentStep + 1) % steps;\n"
              << "  svgs[currentStep].classList.add('active');\n"
              << "}\n"
              << "window.onload = function() {\n"
              << "  document.querySelector('svg').classList.add('active');\n"
              << "  setInterval(showNextStep, delay);\n"
              << "}\n"
              << "</script>\n</head>\n<body>\n";

    for (const auto& step : steps) {
        html_file << "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"" << width << "\" height=\"" << height << "\">\n";
        for (const Square& square : step) {
            html_file << "<rect x=\"" << square.column * square_size << "\" y=\"" << square.row * square_size
                      << "\" width=\"" << square_size << "\" height=\"" << square_size << "\" fill=\"black\" />\n";
        }
        html_file << "</svg>\n";
    }

    html_file << "</body>\n</html>\n";
    html_file.close();
}

// Main solve_maze function
std::vector<Square> solve_maze(int width, int height, const std::vector<Square>& squares, int start_row, int start_col, int goal_row, int goal_col, const std::string& algorithm, bool animation, float delay, const std::string& direction) {
    Maze maze(width, height, squares);
    Square start = maze.get_square(start_row, start_col);
    Square goal = maze.get_square(goal_row, goal_col);

    g_steps.clear();
    std::vector<Square> path;

    if (algorithm == "bfs") {
        path = bfs(maze, start, goal, g_steps);
    } else if (algorithm == "dfs") {
        path = dfs(maze, start, goal, g_steps);
    } else if (algorithm == "dijkstra") {
        path = dijkstra(maze, start, goal, g_steps);
    } else if (algorithm == "a-star") {
        path = a_star(maze, start, goal, g_steps);
    } else if (algorithm == "greedy") {
        path = greedy_best_first(maze, start, goal, g_steps);
    } else if (algorithm == "wall-follower") {
        path = wall_follower(maze, start, goal, g_steps);
    } else if (algorithm == "dead-end") {
        path = dead_end_filling(maze, start, goal, g_steps);
    } else if (algorithm == "recursive-bt") {
        path = recursive_backtracking(maze, start, goal, g_steps);
    } else if (algorithm == "jump-point") {
        path = jump_point_search(maze, start, goal, g_steps);
    } else {
        std::cerr << "Unknown algorithm: " << algorithm << std::endl;
        return {};
    }

    g_step_count = g_steps.size();

    return path;
}


// C interface functions
extern "C" {
    Square** solve_maze(int width, int height, Square* squares, int start_row, int start_col, 
                        int goal_row, int goal_col, const char* algorithm, bool animation, 
                        float delay, bool top_down) {
        std::vector<Square> squares_vec(squares, squares + width * height);
        std::string algo_str(algorithm);
        std::string direction = top_down ? "top-down" : "bottom-up";
        std::vector<Square> solution = solve_maze(width, height, squares_vec, start_row, start_col, 
                                                  goal_row, goal_col, algo_str, animation, delay, direction);
        
        Square** result = new Square*[g_steps.size() + 1];  // +1 for null terminator
        for (size_t i = 0; i < g_steps.size(); ++i) {
            result[i] = new Square[g_steps[i].size()];
            std::copy(g_steps[i].begin(), g_steps[i].end(), result[i]);
        }
        result[g_steps.size()] = nullptr;  // Null terminator
        return result;
    }

    void free_steps(Square** steps) {
        for (int i = 0; steps[i] != nullptr; ++i) {
            delete[] steps[i];
        }
        delete[] steps;
    }

    void generate_html(Square* squares, const char* output_path) {
        int path_length = 0;
        while (squares[path_length].index != -1) {  // Assuming -1 index indicates end of path
            path_length++;
        }
        std::vector<Square> path_vec(squares, squares + path_length);
        generate_html(path_vec, output_path);
    }

    void generate_html_animation(int width, int height, Square** steps, 
                                 const char* output_path, float delay, bool top_down) {
        std::vector<std::vector<Square>> steps_vec;
        for (int i = 0; steps[i] != nullptr; ++i) {
            int step_length = 0;
            while (steps[i][step_length].index != -1) {
                step_length++;
            }
            steps_vec.emplace_back(steps[i], steps[i] + step_length);
        }
        Maze maze(width, height, std::vector<Square>(steps[0], steps[0] + width * height));
        generate_html_animation(steps_vec, maze, output_path, delay, top_down);
    }
}