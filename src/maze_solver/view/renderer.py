# renderer.py
import textwrap
import tempfile
import webbrowser
from dataclasses import dataclass
from typing import Optional, List

from maze_solver.models.maze import Maze
from maze_solver.models.role import Role
from maze_solver.models.solution import Solution
from maze_solver.models.square import Square
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
    Role.ENTRANCE: "\N{mouse face}",
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
