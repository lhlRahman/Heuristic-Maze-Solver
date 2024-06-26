# solver.py
import textwrap
import tempfile
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Set, Tuple
import heapq
import time
from collections import deque

from maze_solver.models.border import Border
from maze_solver.models.maze import Maze
from maze_solver.models.role import Role
from maze_solver.models.solution import Solution
from maze_solver.models.square import Square
from maze_solver.view.renderer import SVGRenderer
from maze_solver.view.primitives import Point, Polyline, Rect, Text, tag
from maze_solver.view.decomposer import decompose

@dataclass(frozen=True)
class SVG:
    xml_content: str

    @property
    def html_content(self) -> str:
        return textwrap.dedent("""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>SVG Animation</title>
          <style>
            svg {{ display: none; }}
            svg.active {{ display: block; }}
          </style>
          <script>
            let currentStep = 0;
            const steps = {len(self.xml_content)};
            const delay = {self.delay * 1000};  // Convert to milliseconds

            function showNextStep() {{
              const svgs = document.querySelectorAll('svg');
              svgs[currentStep].classList.remove('active');
              currentStep = (currentStep + 1) % steps;
              svgs[currentStep].classList.add('active');
            }}

            window.onload = function() {{
              document.querySelector('svg').classList.add('active');
              setInterval(showNextStep, delay);
            }}
          </script>
        </head>
        <body>
        {self.xml_content}
        </body>
        </html>""")

    def preview(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".html", delete=False
        ) as file:
            file.write(self.html_content)
        webbrowser.open(f"file://{file.name}")

@dataclass(frozen=True)
class SVGRenderer:
    square_size: int = 100
    line_width: int = 6

    @property
    def offset(self):
        return self.line_width // 2

    def render(self, maze: Maze, solution: Optional[Solution] = None) -> SVG:
        margins = 2 * (self.offset + self.line_width)
        width = margins + maze.width * self.square_size
        height = margins + maze.height * self.square_size
        return SVG(
            tag(
                "svg",
                content=self._get_body(maze, solution),
                xmlns="http://www.w3.org/2000/svg",
                stroke_linejoin="round",
                width="100vw",
                height="100vh",
                viewBox=f"0 0 {width} {height}",
            )
        )

    def render_step(self, maze: Maze, step: List[Square]) -> SVG:
        margins = 2 * (self.offset + self.line_width)
        width = margins + maze.width * self.square_size
        height = margins + maze.height * self.square_size
        return SVG(
            tag(
                "svg",
                content=self._get_body_step(maze, step),
                xmlns="http://www.w3.org/2000/svg",
                stroke_linejoin="round",
                width="100vw",
                height="100vh",
                viewBox=f"0 0 {width} {height}",
            )
        )

    def _get_body(self, maze: Maze, solution: Optional[Solution]) -> str:
        return "".join([
            arrow_marker(),
            background(self.square_size * maze.width, self.square_size * maze.height),
            *map(self._draw_square, maze),
            self._draw_solution(solution) if solution else "",
        ])

    def _get_body_step(self, maze: Maze, step: List[Square]) -> str:
        return "".join([
            arrow_marker(),
            background(self.square_size * maze.width, self.square_size * maze.height),
            *map(self._draw_square, maze),
            self._draw_solution_step(step)
        ])

    def _transform(self, square: Square, extra_offset: int = 0) -> Point:
        return Point(
            x=square.column * self.square_size,
            y=square.row * self.square_size,
        ).translate(
            x=self.offset + extra_offset,
            y=self.offset + extra_offset
        )

    def _draw_square(self, square: Square) -> str:
        top_left: Point = self._transform(square)
        tags = []
        if square.role is Role.EXTERIOR:
            tags.append(exterior(top_left, self.square_size, self.line_width))
        elif square.role is Role.WALL:
            tags.append(wall(top_left, self.square_size, self.line_width))
        elif emoji := ROLE_EMOJI.get(square.role):
            tags.append(label(emoji, top_left, self.square_size // 2))
        tags.append(self._draw_border(square, top_left))
        return "".join(tags)

    def _draw_border(self, square: Square, top_left: Point) -> str:
        return decompose(square.border, top_left, self.square_size).draw(
            stroke_width=self.line_width,
            stroke="black",
            fill="none"
        )

    def _draw_solution(self, solution: Solution) -> str:
        return Polyline(
            [
                self._transform(point, self.square_size // 2)
                for point in solution
            ]
        ).draw(
            stroke_width=self.line_width * 2,
            stroke_opacity="0.5",
            stroke="red",
            fill="none",
            marker_end="url(#arrow)"
        )

    def _draw_solution_step(self, step: List[Square]) -> str:
        return Polyline(
            [
                self._transform(point, self.square_size // 2)
                for point in step if point is not None
            ]
        ).draw(
            stroke_width=self.line_width * 2,
            stroke_opacity="0.5",
            stroke="red",
            fill="none",
            marker_end="url(#arrow)"
        )

ROLE_EMOJI = {
    Role.ENTRANCE: "\N{mouse}",
    Role.EXIT: "\N{chequered flag}",
    Role.ENEMY: "\N{ghost}",
    Role.REWARD: "\N{white medium star}",
}

def arrow_marker() -> str:
    return (
        tag(
            "marker",
            id="arrow",
            viewBox="0 0 10 10",
            refX="5",
            refY="5",
            markerWidth="4",
            markerHeight="4",
            orient="auto-start-reverse"
        ) +
        tag(
            "path",
            content="",
            d="M 0 0 L 10 5 L 0 10 z",
            fill="black"
        )
    )

def background(width: int, height: int) -> str:
    return Rect(Point(0, 0), width, height).draw(fill="white")

def exterior(top_left: Point, size: int, line_width: int) -> str:
    return Rect(top_left, size, size).draw(
        stroke_width=line_width,
        stroke="none",
        fill="white"
    )

def wall(top_left: Point, size: int, line_width: int) -> str:
    return Rect(top_left, size, size).draw(
        stroke_width=line_width,
        stroke="none",
        fill="lightgray"
    )

def label(emoji: str, top_left: Point, offset: int) -> str:
    return Text(emoji, top_left.translate(x=offset, y=offset)).draw(
        font_size=f"{offset}px",
        text_anchor="middle",
        dominant_baseline="middle"
    )

def animate_solution(maze: Maze, solution_steps: List[List[Square]], delay: float, direction: str):
    renderer = SVGRenderer()
    if direction == "bottom-up":
        solution_steps.reverse()
    svgs = [renderer.render_step(maze, step).xml_content for step in solution_steps if step]
    html_content = textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>SVG Animation</title>
      <style>
        svg {{ display: none; }}
        svg.active {{ display: block; }}
      </style>
      <script>
        let currentStep = 0;
        const steps = {len(svgs)};
        const delay = {delay * 1000};  // Convert to milliseconds

        function showNextStep() {{
          const svgs = document.querySelectorAll('svg');
          svgs[currentStep].classList.remove('active');
          currentStep = (currentStep + 1) % steps;
          svgs[currentStep].classList.add('active');
        }}

        window.onload = function() {{
          document.querySelector('svg').classList.add('active');
          setInterval(showNextStep, delay);
        }}
      </script>
    </head>
    <body>
    {''.join(svgs)}
    </body>
    </html>
    """)

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".html", delete=False) as file:
        file.write(html_content)
    webbrowser.open(f"file://{file.name}")

def solve_maze_python(maze_path: Path, output_dir: Path, algorithm: str, animation: bool, delay: float, direction: str) -> None:
    maze = Maze.load(maze_path)
    if algorithm == "bfs":
        solution_steps = bfs(maze, maze.entrance, maze.exit)
    elif algorithm == "dfs":
        solution_steps = dfs(maze, maze.entrance, maze.exit)
    elif algorithm == "dijkstra":
        solution_steps = dijkstra(maze, maze.entrance, maze.exit)
    elif algorithm == "greedy":
        solution_steps = greedy_best_first(maze, maze.entrance, maze.exit)
    elif algorithm == "wall-follower":
        solution_steps = wall_follower(maze, maze.entrance, maze.exit)
    elif algorithm == "dead-end":
        solution_steps = dead_end_filling(maze, maze.entrance, maze.exit)
    elif algorithm == "recursive-bt":
        solution_steps = recursive_backtracking(maze, maze.entrance, maze.exit)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    if solution_steps:
        if animation:
            animate_solution(maze, solution_steps, delay, direction)
        else:
            renderer = SVGRenderer()
            if direction == "bottom-up":
                solution_steps.reverse()
            svg = renderer.render_step(maze, solution_steps[-1])
            svg.preview()
            svg_file_path = output_dir / "solution.svg"
            with open(svg_file_path, 'w') as f:
                f.write(svg.xml_content)
    else:
        print("No solution found")

def a_star_search_steps(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from: Dict[Square, Square] = {}

    g_score = {square: float('inf') for square in maze.squares}
    g_score[start] = 0
    f_score = {square: float('inf') for square in maze.squares}
    f_score[start] = heuristic(start, goal)

    open_set_hash = {start}

    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)

        if current == goal:
            return reconstruct_path(came_from, current)

        neighbors = get_neighbors(maze, current)
        for neighbor in neighbors:
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)

    return None

def bfs(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    queue = deque([start])
    came_from: Dict[Square, Optional[Square]] = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(maze, current):
            if neighbor not in came_from:
                queue.append(neighbor)
                came_from[neighbor] = current

    return None

def dfs(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    stack = [start]
    came_from: Dict[Square, Optional[Square]] = {start: None}

    while stack:
        current = stack.pop()

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(maze, current):
            if neighbor not in came_from:
                stack.append(neighbor)
                came_from[neighbor] = current

    return None

def dijkstra(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from: Dict[Square, Optional[Square]] = {start: None}
    cost_so_far = {start: 0}

    while open_set:
        current_cost, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(maze, current):
            new_cost = cost_so_far[current] + 1  # Assuming uniform cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    return None

def greedy_best_first(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), start))
    came_from: Dict[Square, Optional[Square]] = {start: None}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(maze, current):
            if neighbor not in came_from:
                priority = heuristic(neighbor, goal)
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    return None

def wall_follower(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    def turn_left(direction):
        return (-direction[1], direction[0])

    def turn_right(direction):
        return (direction[1], -direction[0])

    def move_forward(square, direction):
        next_row, next_col = square.row + direction[1], square.column + direction[0]
        if 0 <= next_row < maze.height and 0 <= next_col < maze.width:
            return maze.squares[next_row * maze.width + next_col]
        return None

    def has_wall(square, direction):
        if direction == (0, -1):  # up
            return square.border & Border.TOP
        elif direction == (1, 0):  # right
            return square.border & Border.RIGHT
        elif direction == (0, 1):  # down
            return square.border & Border.BOTTOM
        elif direction == (-1, 0):  # left
            return square.border & Border.LEFT
        return False

    current = start
    direction = (1, 0)  # Start by going right
    path = [current]

    while current != goal:
        left = turn_left(direction)
        left_square = move_forward(current, left)
        if left_square and not has_wall(current, left):
            direction = left
            current = left_square
        elif not has_wall(current, direction):
            current = move_forward(current, direction)
        else:
            direction = turn_right(direction)
            current = move_forward(current, direction)
        
        path.append(current)

    return [path]


def dead_end_filling(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    def is_dead_end(square):
        return bin(square.border.value).count("1") == 3

    new_squares = list(maze.squares)
    for square in maze.squares:
        if is_dead_end(square):
            new_squares[square.index] = Square(square.index, square.row, square.column, square.border, Role.WALL)

    new_maze = Maze(tuple(new_squares))
    return a_star_search_steps(new_maze, start, goal)

def recursive_backtracking(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    path = []
    visited = set()

    def backtrack(square):
        if square == goal:
            return True
        visited.add(square)
        path.append(square)

        for neighbor in get_neighbors(maze, square):
            if neighbor not in visited:
                if backtrack(neighbor):
                    return True

        path.pop()
        return False

    backtrack(start)
    return [path] if path else None

def reconstruct_path(came_from: Dict[Square, Square], current: Square) -> List[List[Square]]:
    total_path = [current]
    path_steps = [total_path[:]]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
        path_steps.append(total_path[:])
    path_steps.reverse()
    return path_steps

def get_neighbors(maze: Maze, square: Square) -> List[Square]:
    neighbors = []
    directions = [
        (0, -1, Border.TOP, Border.BOTTOM),
        (1, 0, Border.RIGHT, Border.LEFT),
        (0, 1, Border.BOTTOM, Border.TOP),
        (-1, 0, Border.LEFT, Border.RIGHT),
    ]
    for dx, dy, own_border, neighbor_border in directions:
        nx, ny = square.column + dx, square.row + dy
        if 0 <= nx < maze.width and 0 <= ny < maze.height:
            neighbor = maze.squares[ny * maze.width + nx]
            if not (square.border & own_border) and not (neighbor.border & neighbor_border):
                neighbors.append(neighbor)
    return neighbors

def heuristic(a: Square, b: Square) -> int:
    return abs(a.row - b.row) + abs(a.column - b.column)
