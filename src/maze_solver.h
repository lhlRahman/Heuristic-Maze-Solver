// maze_solver.h
#ifndef MAZE_SOLVER_H
#define MAZE_SOLVER_H

#include <vector>
#include <string>
#include "maze.h"
#include "square.h"

std::vector<Square> bfs(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps);
std::vector<Square> dfs(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps);
std::vector<Square> dijkstra(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps);
std::vector<Square> greedy_best_first(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps);
std::vector<Square> wall_follower(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps);
std::vector<Square> dead_end_filling(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps);
std::vector<Square> recursive_backtracking(const Maze &maze, const Square &start, const Square &goal, std::vector<std::vector<Square>>& steps);

void generate_html(const std::vector<Square>& path, const std::string& filename);
void generate_html_animation(const std::vector<std::vector<Square>>& steps, const Maze& maze, const std::string& output_file, float delay, bool top_down);

extern "C" {
    void solve_maze_c(int width, int height, Square* squares, int start_row, int start_col, int goal_row, int goal_col, const char* algorithm, bool animation, float delay, const char* direction);
    void generate_html_c(const Square* path, int path_length, const char* output_file);
    void generate_html_animation_c(int width, int height, const Square* steps, int* step_lengths, int num_steps, const char* output_dir, float delay, bool top_down);
}

#endif // MAZE_SOLVER_H
