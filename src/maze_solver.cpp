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

// Debugging helper
#define DEBUG_PRINT(x) std::cout << x << std::endl;

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

std::vector<Square> bfs(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps) {
    std::queue<Square> queue;
    queue.push(start);
    std::map<Square, Square> came_from;
    came_from[start] = start;

    while (!queue.empty()) {
        Square current = queue.front();
        queue.pop();

        if (current == goal) {
            steps.push_back(reconstruct_path(came_from, start, goal));
            return steps.back();
        }

        for (const Square& neighbor : maze.get_neighbors(current)) {
            if (came_from.find(neighbor) == came_from.end()) {
                queue.push(neighbor);
                came_from[neighbor] = current;
                steps.push_back(reconstruct_path(came_from, start, neighbor));
            }
        }
    }

    return {};
}

std::vector<Square> dfs(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps) {
    std::stack<Square> stack;
    stack.push(start);
    std::map<Square, Square> came_from;
    came_from[start] = start;

    while (!stack.empty()) {
        Square current = stack.top();
        stack.pop();

        if (current == goal) {
            steps.push_back(reconstruct_path(came_from, start, goal));
            return steps.back();
        }

        for (const Square& neighbor : maze.get_neighbors(current)) {
            if (came_from.find(neighbor) == came_from.end()) {
                stack.push(neighbor);
                came_from[neighbor] = current;
                steps.push_back(reconstruct_path(came_from, start, neighbor));
            }
        }
    }

    return {};
}

std::vector<Square> dijkstra(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps) {
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
            steps.push_back(reconstruct_path(came_from, start, goal));
            return steps.back();
        }

        for (const Square& neighbor : maze.get_neighbors(current)) {
            int new_cost = cost_so_far[current] + 1;
            if (cost_so_far.find(neighbor) == cost_so_far.end() || new_cost < cost_so_far[neighbor]) {
                cost_so_far[neighbor] = new_cost;
                queue.push({new_cost, neighbor});
                came_from[neighbor] = current;
                steps.push_back(reconstruct_path(came_from, start, neighbor));
            }
        }
    }

    return {};
}

std::vector<Square> greedy_best_first(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps) {
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
            steps.push_back(reconstruct_path(came_from, start, goal));
            return steps.back();
        }

        for (const Square& neighbor : maze.get_neighbors(current)) {
            if (came_from.find(neighbor) == came_from.end()) {
                queue.push({heuristic(neighbor, goal), neighbor});
                came_from[neighbor] = current;
                steps.push_back(reconstruct_path(came_from, start, neighbor));
            }
        }
    }

    return {};
}

std::vector<Square> wall_follower(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps) {
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
    std::pair<int, int> direction = {1, 0};
    std::vector<Square> path = {current};
    steps.push_back(path);

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
        steps.push_back(path);
    }

    return path;
}

std::vector<Square> dead_end_filling(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps) {
    auto is_dead_end = [](const Square& square) {
        return std::bitset<4>(square.border).count() == 3;
    };

    std::vector<Square> new_squares = maze.squares;
    for (auto& square : new_squares) {
        if (is_dead_end(square)) {
            square.role = 4;
        }
    }

    Maze new_maze(maze.width, maze.height, new_squares);
    return dijkstra(new_maze, start, goal, steps);
}

std::vector<Square> recursive_backtracking(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps) {
    std::vector<Square> path;
    std::set<Square> visited;

    std::function<bool(const Square&)> backtrack = [&](const Square& square) {
        if (square == goal) {
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

std::string generate_html_frame(const std::vector<Square>& squares, int width, int height, int square_size) {
    std::stringstream html_content;
    html_content << "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"" << (width * square_size) << "\" height=\"" << (height * square_size) << "\">\n";
    for (const Square& square : squares) {
        html_content << "<rect x=\"" << (square.column * square_size) << "\" y=\"" << (square.row * square_size) << "\" width=\"" << square_size << "\" height=\"" << square_size << "\" fill=\"black\" />\n";
    }
    html_content << "</svg>\n";
    return html_content.str();
}

void generate_html_animation(const std::vector<std::vector<Square>>& steps, const Maze& maze, const std::string& output_file, float delay, bool top_down) {
    std::ofstream html_file(output_file);
    std::stringstream html_content;

    int square_size = 10;
    int width = maze.width * square_size;
    int height = maze.height * square_size;

    html_content << "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n";
    html_content << "<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n";
    html_content << "<title>SVG Animation</title>\n<style>\n";
    html_content << "svg { display: none; }\n";
    html_content << "svg.active { display: block; }\n";
    html_content << "</style>\n<script>\n";
    html_content << "let currentStep = 0;\n";
    html_content << "const steps = " << steps.size() << ";\n";
    html_content << "const delay = " << (delay * 1000) << ";\n";
    html_content << "function showNextStep() {\n";
    html_content << "  const svgs = document.querySelectorAll('svg');\n";
    html_content << "  svgs[currentStep].classList.remove('active');\n";
    html_content << "  currentStep = (currentStep + 1) % steps;\n";
    html_content << "  svgs[currentStep].classList.add('active');\n";
    html_content << "}\n";
    html_content << "window.onload = function() {\n";
    html_content << "  document.querySelector('svg').classList.add('active');\n";
    html_content << "  setInterval(showNextStep, delay);\n";
    html_content << "}\n";
    html_content << "</script>\n</head>\n<body>\n";

    for (const auto& step : steps) {
        html_content << "<div>\n";
        html_content << generate_html_frame(step, maze.width, maze.height, square_size);
        html_content << "</div>\n";
    }

    html_content << "</body>\n</html>\n";
    html_file << html_content.str();
    html_file.close();
}

void generate_html(const std::vector<Square>& path, const std::string& filename) {
    std::ofstream html_file(filename);
    std::stringstream html_content;

    int square_size = 10;
    int width = 50 * square_size;
    int height = 50 * square_size;

    html_content << "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n";
    html_content << "<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n";
    html_content << "<title>SVG Path</title>\n</head>\n<body>\n";
    html_content << "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"" << width << "\" height=\"" << height << "\">\n";

    for (const Square& square : path) {
        html_content << "<rect x=\"" << square.column * square_size << "\" y=\"" << square.row * square_size << "\" width=\"" << square_size << "\" height=\"" << square_size << "\" fill=\"black\" />\n";
    }

    html_content << "</svg>\n</body>\n</html>\n";
    html_file << html_content.str();
    html_file.close();
}

std::vector<Square> solve_maze(int width, int height, const std::vector<Square>& squares, int start_row, int start_col, int goal_row, int goal_col, const std::string& algorithm, bool animation, float delay, const std::string& direction) {
    Maze maze(width, height, squares);
    DEBUG_PRINT("Maze created");
    Square start = maze.get_square(start_row, start_col);
    DEBUG_PRINT("Start square: (" << start.row << ", " << start.column << ")");
    Square goal = maze.get_square(goal_row, goal_col);
    DEBUG_PRINT("Goal square: (" << goal.row << ", " << goal.column << ")");

    std::vector<Square> path;
    std::vector<std::vector<Square>> steps;

    if (algorithm == "bfs") {
        path = bfs(maze, start, goal, steps);
    } else if (algorithm == "dfs") {
        path = dfs(maze, start, goal, steps);
    } else if (algorithm == "dijkstra") {
        path = dijkstra(maze, start, goal, steps);
    } else if (algorithm == "greedy") {
        path = greedy_best_first(maze, start, goal, steps);
    } else if (algorithm == "wall-follower") {
        path = wall_follower(maze, start, goal, steps);
    } else if (algorithm == "dead-end") {
        path = dead_end_filling(maze, start, goal, steps);
    } else if (algorithm == "recursive-bt") {
        path = recursive_backtracking(maze, start, goal, steps);
    } else {
        std::cerr << "Unknown algorithm: " << algorithm << std::endl;
        return {};
    }

    if (animation) {
        generate_html_animation(steps, maze, "animation.html", delay, direction == "top-down");
    } else {
        generate_html(path, "solution.html");
    }

    return path;
}

extern "C" {
    void solve_maze_c(int width, int height, Square* squares, int start_row, int start_col, int goal_row, int goal_col, const char* algorithm, bool animation, float delay, const char* direction) {
        std::vector<Square> squares_vec(squares, squares + width * height);
        solve_maze(width, height, squares_vec, start_row, start_col, goal_row, goal_col, algorithm, animation, delay, direction);
    }

    void generate_html_c(const Square* path, int path_length, const char* output_file) {
        std::vector<Square> path_vec(path, path + path_length);
        generate_html(path_vec, output_file);
    }

    void generate_html_animation_c(int width, int height, const Square* steps, int* step_lengths, int num_steps, const char* output_dir, float delay, bool top_down) {
        std::vector<std::vector<Square>> steps_vec;
        const Square* current_step = steps;
        for (int i = 0; i < num_steps; ++i) {
            steps_vec.emplace_back(current_step, current_step + step_lengths[i]);
            current_step += step_lengths[i];
        }
        generate_html_animation(steps_vec, Maze(width, height, std::vector<Square>(steps, steps + num_steps)), output_dir, delay, top_down);
    }
}
