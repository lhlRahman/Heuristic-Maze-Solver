# solver.py
import textwrap
import tempfile
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Set, Tuple
import heapq
import time
from collections import defaultdict, deque
import random
import math


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
    elif algorithm == "a-star":
        solution_steps = a_star_search_steps(maze, maze.entrance, maze.exit)
    elif algorithm == "tremaux":
        solution_steps = tremaux_algorithm(maze, maze.entrance, maze.exit)
    elif algorithm == "bellman-ford":
        solution_steps = bellman_ford_algorithm(maze, maze.entrance, maze.exit)
    elif algorithm == "lee":
        solution_steps = lee_algorithm(maze, maze.entrance, maze.exit)
    elif algorithm == "genetic":
        solution_steps = genetic_algorithm(maze, maze.entrance, maze.exit)
    elif algorithm == "ant-colony":
        solution_steps = ant_colony_optimization(maze, maze.entrance, maze.exit)
    elif algorithm == "best-first":
        solution_steps = best_first_graph_search(maze, maze.entrance, maze.exit)
    elif algorithm == "wavefront":
        solution_steps = wavefront_expansion(maze, maze.entrance, maze.exit)
    elif algorithm == "jump-point":
        solution_steps = jump_point_search(maze, maze.entrance, maze.exit)
    elif algorithm == "fringe":
        solution_steps = fringe_search(maze, maze.entrance, maze.exit)
    elif algorithm == "iddfs":
        solution_steps = iddfs(maze, maze.entrance, maze.exit)
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
    
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start, goal)
    
    open_set_hash = {start}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_neighbors(maze, current):
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
    cost_so_far = defaultdict(lambda: float('inf'))
    cost_so_far[start] = 0
    
    while open_set:
        current_cost, current = heapq.heappop(open_set)
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_neighbors(maze, current):
            new_cost = cost_so_far[current] + 1  # Assuming uniform cost
            if new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(open_set, (new_cost, neighbor))
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
                heapq.heappush(open_set, (heuristic(neighbor, goal), neighbor))
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
            while has_wall(current, direction):
                direction = turn_right(direction)
            current = move_forward(current, direction)

        if current is not None:
            path.append(current)

    return [path] if current == goal else None



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
    stack = [(start, [start])]
    visited = set()

    while stack:
        current, path = stack.pop()
        if current == goal:
            return [path]

        visited.add(current)

        for neighbor in get_neighbors(maze, current):
            if neighbor not in visited and neighbor not in [p[0] for p in stack]:
                stack.append((neighbor, path + [neighbor]))

    return None

def tremaux_algorithm(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    visited = defaultdict(int)
    current = start
    stack = [current]
    path = []

    while stack:
        path.append(current)
        visited[current] += 1

        if current == goal:
            return [path]

        neighbors = get_neighbors(maze, current)
        unvisited_neighbors = [n for n in neighbors if visited[n] == 0]

        if unvisited_neighbors:
            next_square = unvisited_neighbors[0]
            stack.append(current)
            current = next_square
        else:
            current = stack.pop()

    return None

def bellman_ford_algorithm(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    cost_so_far = defaultdict(lambda: float('inf'))
    cost_so_far[start] = 0
    came_from = {start: None}
    for _ in range(len(maze.squares) - 1):
        for current in maze.squares:
            if cost_so_far[current] < float('inf'):
                for neighbor in get_neighbors(maze, current):
                    new_cost = cost_so_far[current] + 1
                    if new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        came_from[neighbor] = current
    return reconstruct_path(came_from, goal) if cost_so_far[goal] < float('inf') else None

def lee_algorithm(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    grid = [[float('inf')] * maze.width for _ in range(maze.height)]
    grid[start.row][start.column] = 0
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(maze, current):
            if grid[neighbor.row][neighbor.column] == float('inf'):
                grid[neighbor.row][neighbor.column] = grid[current.row][current.column] + 1
                queue.append(neighbor)
                came_from[neighbor] = current

    return None

def genetic_algorithm(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    population_size = 100
    generations = 10
    mutation_rate = 0.1

    def random_path(start, goal, maze):
        current = start
        path = [current]
        while current != goal:
            neighbors = get_neighbors(maze, current)
            if not neighbors:
                break
            current = random.choice(neighbors)
            path.append(current)
        return path

    population = [random_path(start, goal, maze) for _ in range(population_size)]

    def fitness(path):
        if path[-1] != goal:
            return float('inf')
        return len(path)

    def crossover(parent1, parent2):
        crossover_point = random.randint(0, min(len(parent1), len(parent2)) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    def mutate(path):
        if random.random() < mutation_rate:
            mutate_point = random.randint(0, len(path) - 1)
            neighbors = get_neighbors(maze, path[mutate_point])
            if neighbors:
                path[mutate_point] = random.choice(neighbors)

    for generation in range(generations):
        population = sorted(population, key=fitness)
        next_population = population[:population_size // 2]
        for i in range(population_size // 2, population_size, 2):
            parent1, parent2 = random.sample(next_population, 2)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1)
            mutate(child2)
            next_population += [child1, child2]
        population = next_population

    best_path = min(population, key=fitness)
    return [best_path] if best_path[-1] == goal else None


def ant_colony_optimization(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    num_ants = 100
    num_iterations = 10
    pheromone_decay = 0.1
    pheromones = defaultdict(lambda: 1.0)

    def get_path():
        current = start
        path = [current]
        while current != goal:
            neighbors = get_neighbors(maze, current)
            probabilities = [pheromones[(current, neighbor)] for neighbor in neighbors]
            total = sum(probabilities)
            probabilities = [p / total for p in probabilities]
            current = random.choices(neighbors, probabilities)[0]
            path.append(current)
        return path

    def update_pheromones(paths):
        for path in paths:
            for i in range(len(path) - 1):
                pheromones[(path[i], path[i + 1])] += 1.0 / len(path)
        for edge in pheromones:
            pheromones[edge] *= (1 - pheromone_decay)

    for _ in range(num_iterations):
        paths = [get_path() for _ in range(num_ants)]
        update_pheromones(paths)

    best_path = min(paths, key=lambda p: heuristic(p[-1], goal))
    return [best_path] if best_path[-1] == goal else None


def best_first_graph_search(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), start))
    came_from: Dict[Square, Optional[Square]] = {start: None}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(maze, current):
            if neighbor not in came_from:
                heapq.heappush(open_set, (heuristic(neighbor, goal), neighbor))
                came_from[neighbor] = current

    return None

def wavefront_expansion(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    grid = [[float('inf')] * maze.width for _ in range(maze.height)]
    grid[start.row][start.column] = 0
    queue = deque([start])
    came_from: Dict[Square, Optional[Square]] = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(maze, current):
            if grid[neighbor.row][neighbor.column] == float('inf'):
                grid[neighbor.row][neighbor.column] = grid[current.row][current.column] + 1
                queue.append(neighbor)
                came_from[neighbor] = current

    return None

def jump_point_search(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from: Dict[Square, Square] = {}
    
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start, goal)
    
    open_set_hash = {start}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_neighbors(maze, current):
            tentative_g_score = g_score[current] + 1
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
    
    return None

def fringe_search(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from: Dict[Square, Square] = {}
    
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start, goal)
    
    open_set_hash = {start}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_neighbors(maze, current):
            tentative_g_score = g_score[current] + 1
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
    
    return None

def iddfs(maze: Maze, start: Square, goal: Square) -> Optional[List[List[Square]]]:
    def dls(node, depth, came_from):
        if depth == 0:
            return node == goal
        if depth > 0:
            for neighbor in get_neighbors(maze, node):
                if neighbor not in came_from:  # Avoid cycles
                    came_from[neighbor] = node
                    if dls(neighbor, depth - 1, came_from):
                        return True
        return False

    for depth in range(len(maze.squares)):
        came_from = {start: None}
        if dls(start, depth, came_from):
            return reconstruct_path(came_from, goal)
    return None

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