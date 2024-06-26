// maze_solver.cpp
#include "maze_solver.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <stack>
#include <map>
#include <algorithm>
#include <sstream>
#include <filesystem>
#include <chrono>
#include <thread>
#include <set>
#include <bitset>
#include <functional>


std::vector<Square> reconstruct_path(const std::map<Square, Square>& came_from, const Square& start, const Square& goal) {
    std::vector<Square> path;
    Square current = goal;
    while (!(current == start)) {
        path.push_back(current);
        current = came_from.at(current);
    }
    path.push_back(start);
    std::reverse(path.begin(), path.end());
    return path;
}

std::vector<Square> bfs(const Maze &maze, const Square &start, const Square &goal) {
    std::queue<Square> queue;
    queue.push(start);
    std::map<Square, Square> came_from;
    came_from[start] = start;

    while (!queue.empty()) {
        Square current = queue.front();
        queue.pop();

        if (current == goal) {
            return reconstruct_path(came_from, start, goal);
        }

        for (const Square& neighbor : maze.get_neighbors(current)) {
            if (came_from.find(neighbor) == came_from.end()) {
                queue.push(neighbor);
                came_from[neighbor] = current;
            }
        }
    }

    return {};
}

std::vector<Square> dfs(const Maze &maze, const Square &start, const Square &goal) {
    std::stack<Square> stack;
    stack.push(start);
    std::map<Square, Square> came_from;
    came_from[start] = start;

    while (!stack.empty()) {
        Square current = stack.top();
        stack.pop();

        if (current == goal) {
            return reconstruct_path(came_from, start, goal);
        }

        for (const Square& neighbor : maze.get_neighbors(current)) {
            if (came_from.find(neighbor) == came_from.end()) {
                stack.push(neighbor);
                came_from[neighbor] = current;
            }
        }
    }

    return {};
}

std::vector<Square> dijkstra(const Maze &maze, const Square &start, const Square &goal) {
    auto compare = [](const std::pair<int, Square>& a, const std::pair<int, Square>& b) { return a.first > b.first; };
    std::priority_queue<std::pair<int, Square>, std::vector<std::pair<int, Square>>, decltype(compare)> queue(compare);
    queue.push({0, start});
    std::map<Square, Square> came_from;
    came_from[start] = start;
    std::map<Square, int> cost_so_far;
    cost_so_far[start] = 0;

    while (!queue.empty()) {
        Square current = queue.top().second;
        queue.pop();

        if (current == goal) {
            return reconstruct_path(came_from, start, goal);
        }

        for (const Square& neighbor : maze.get_neighbors(current)) {
            int new_cost = cost_so_far[current] + 1; // assuming uniform cost
            if (cost_so_far.find(neighbor) == cost_so_far.end() || new_cost < cost_so_far[neighbor]) {
                cost_so_far[neighbor] = new_cost;
                queue.push({new_cost, neighbor});
                came_from[neighbor] = current;
            }
        }
    }

    return {};
}

std::vector<Square> greedy_best_first(const Maze &maze, const Square &start, const Square &goal) {
    auto heuristic = [](const Square& a, const Square& b) { return std::abs(a.row - b.row) + std::abs(a.column - b.column); };
    auto compare = [](const std::pair<int, Square>& a, const std::pair<int, Square>& b) { return a.first > b.first; };
    std::priority_queue<std::pair<int, Square>, std::vector<std::pair<int, Square>>, decltype(compare)> queue(compare);
    queue.push({heuristic(start, goal), start});
    std::map<Square, Square> came_from;
    came_from[start] = start;

    while (!queue.empty()) {
        Square current = queue.top().second;
        queue.pop();

        if (current == goal) {
            return reconstruct_path(came_from, start, goal);
        }

        for (const Square& neighbor : maze.get_neighbors(current)) {
            if (came_from.find(neighbor) == came_from.end()) {
                queue.push({heuristic(neighbor, goal), neighbor});
                came_from[neighbor] = current;
            }
        }
    }

    return {};
}

std::vector<Square> wall_follower(const Maze &maze, const Square &start, const Square &goal) {
    auto turn_left = [](const std::pair<int, int>& direction) { return std::make_pair(-direction.second, direction.first); };
    auto turn_right = [](const std::pair<int, int>& direction) { return std::make_pair(direction.second, -direction.first); };
    auto move_forward = [&maze](const Square& square, const std::pair<int, int>& direction) {
        int new_row = square.row + direction.first;
        int new_col = square.column + direction.second;
        if (new_row >= 0 && new_row < maze.height && new_col >= 0 && new_col < maze.width) {
            return maze.get_square(new_row, new_col);
        }
        return square;
    };

    Square current = start;
    std::pair<int, int> direction = {1, 0}; // Start by going right
    std::vector<Square> path = {current};

    while (!(current == goal)) {
        auto left = turn_left(direction);
        auto left_square = move_forward(current, left);
        if (!(current.border & left.first)) {
            direction = left;
            current = left_square;
        } else if (!(current.border & direction.first)) {
            current = move_forward(current, direction);
        } else {
            direction = turn_right(direction);
        }
        path.push_back(current);
    }

    return path;
}

std::vector<Square> dead_end_filling(const Maze &maze, const Square &start, const Square &goal) {
    auto is_dead_end = [](const Square& square) {
        return std::bitset<4>(square.border).count() == 3;
    };

    std::vector<Square> new_squares = maze.squares;
    for (auto& square : new_squares) {
        if (is_dead_end(square)) {
            square.role = 4; // Set to wall
        }
    }

    Maze new_maze(maze.width, maze.height, new_squares);
    return dijkstra(new_maze, start, goal);
}

std::vector<Square> recursive_backtracking(const Maze &maze, const Square &start, const Square &goal) {
    std::vector<Square> path;
    std::set<Square> visited; // Declare visited as std::set<Square>

    std::function<bool(const Square&)> backtrack = [&](const Square& square) {
        if (square == goal) {
            return true;
        }
        visited.insert(square);
        path.push_back(square);

        for (const Square& neighbor : maze.get_neighbors(square)) {
            if (visited.find(neighbor) == visited.end()) {
                if (backtrack(neighbor)) {
                    return true;
                }
            }
        }

        path.pop_back();
        return false;
    };

    backtrack(start);
    return path;
}

void generate_svg(const std::vector<Square> &path, const std::string &output_file) {
    std::ofstream svg_file(output_file);
    svg_file << "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\">\n";
    for (const Square &square : path) {
        svg_file << "<rect x=\"" << square.column * 10 << "\" y=\"" << square.row * 10 << "\" width=\"10\" height=\"10\" fill=\"black\" />\n";
    }
    svg_file << "</svg>\n";
    svg_file.close();
}

void generate_animation(std::vector<std::vector<Square>> steps, const std::string &output_dir, float delay, bool top_down) {
    if (!top_down) {
        std::reverse(steps.begin(), steps.end());
    }

    for (size_t i = 0; i < steps.size(); ++i) {
        std::string filename = output_dir + "/step_" + std::to_string(i) + ".svg";
        generate_svg(steps[i], filename);
        std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(delay * 1000)));
    }
}

std::vector<Square> solve_maze(int width, int height, const std::vector<Square>& squares,
                               int start_row, int start_col, int goal_row, int goal_col,
                               const std::string& algorithm, bool animation, float delay, const std::string& direction) {
    Maze maze(width, height, squares);
    Square start = maze.get_square(start_row, start_col);
    Square goal = maze.get_square(goal_row, goal_col);

    std::vector<Square> path;
    if (algorithm == "bfs") {
        path = bfs(maze, start, goal);
    } else if (algorithm == "dfs") {
        path = dfs(maze, start, goal);
    } else if (algorithm == "dijkstra") {
        path = dijkstra(maze, start, goal);
    } else if (algorithm == "greedy") {
        path = greedy_best_first(maze, start, goal);
    } else if (algorithm == "wall-follower") {
        path = wall_follower(maze, start, goal);
    } else if (algorithm == "dead-end") {
        path = dead_end_filling(maze, start, goal);
    } else if (algorithm == "recursive-bt") {
        path = recursive_backtracking(maze, start, goal);
    } else {
        std::cerr << "Unknown algorithm: " << algorithm << std::endl;
        return {};
    }

    if (animation) {
        std::vector<std::vector<Square>> steps;
        for (size_t i = 1; i <= path.size(); ++i) {
            steps.push_back(std::vector<Square>(path.begin(), path.begin() + i));
        }
        generate_animation(steps, ".", delay, direction == "top-down");
    } else {
        generate_svg(path, "solution.svg");
    }

    return path;
}

extern "C" {
    void solve_maze_c(int width, int height, Square* squares, int start_row, int start_col, int goal_row, int goal_col, const char* algorithm, bool animation, float delay, const char* direction) {
        std::vector<Square> squares_vec(squares, squares + width * height);
        solve_maze(width, height, squares_vec, start_row, start_col, goal_row, goal_col, algorithm, animation, delay, direction);
    }

    void generate_svg_c(const Square* path, int path_length, const char* output_file) {
        std::vector<Square> path_vec(path, path + path_length);
        generate_svg(path_vec, output_file);
    }

    void generate_animation_c(const Square* steps, int* step_lengths, int num_steps, const char* output_dir, float delay, bool top_down) {
        std::vector<std::vector<Square>> steps_vec;
        const Square* current_step = steps;
        for (int i = 0; i < num_steps; ++i) {
            steps_vec.emplace_back(current_step, current_step + step_lengths[i]);
            current_step += step_lengths[i];
        }
        generate_animation(steps_vec, output_dir, delay, top_down);
    }
}
