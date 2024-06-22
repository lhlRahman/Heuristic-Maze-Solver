from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

class Primitive(ABC):
    @abstractmethod
    def draw(self, **kwargs) -> str:
        pass

@dataclass(frozen=True)
class Point:
    x: int
    y: int
    
    def translate(self, x=0, y=0) -> "Point":
        return Point(self.x + x, self.y + y)

def tag(name: str, content: str = "", **attrs) -> str:
    attr_str = " ".join(f'{key.replace("_", "-")}="{value}"' for key, value in attrs.items())
    return f'<{name} {attr_str}>{content}</{name}>'

@dataclass(frozen=True)
class Line(Primitive):
    start: Point
    end: Point

    def draw(self, stroke_width: int = 1, stroke: str = "black", fill: str = "none") -> str:
        return f'<line x1="{self.start.x}" y1="{self.start.y}" x2="{self.end.x}" y2="{self.end.y}" ' \
               f'stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />'

@dataclass(frozen=True)
class Polyline(Primitive):
    points: List[Point]

    def draw(self, stroke_width: int = 1, stroke: str = "black", fill: str = "none", stroke_opacity: str = "1.0", marker_end: str = "") -> str:
        points_str = " ".join(f"{p.x},{p.y}" for p in self.points)
        marker_end_str = f' marker-end="{marker_end}"' if marker_end else ""
        return f'<polyline points="{points_str}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" stroke-opacity="{stroke_opacity}"{marker_end_str} />'

@dataclass(frozen=True)
class Polygon(Primitive):
    points: List[Point]

    def draw(self, stroke_width: int = 1, stroke: str = "black", fill: str = "none") -> str:
        points_str = " ".join(f"{p.x},{p.y}" for p in self.points)
        return f'<polygon points="{points_str}" stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />'

@dataclass(frozen=True)
class Rect(Primitive):
    top_left: Point
    width: int
    height: int

    def draw(self, stroke_width: int = 1, stroke: str = "black", fill: str = "none") -> str:
        return f'<rect x="{self.top_left.x}" y="{self.top_left.y}" width="{self.width}" height="{self.height}" ' \
               f'stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />'

@dataclass(frozen=True)
class Text(Primitive):
    content: str
    position: Point

    def draw(self, font_size: str = "12px", text_anchor: str = "start", dominant_baseline: str = "alphabetic") -> str:
        return f'<text x="{self.position.x}" y="{self.position.y}" font-size="{font_size}" ' \
               f'text-anchor="{text_anchor}" dominant-baseline="{dominant_baseline}">{self.content}</text>'

@dataclass(frozen=True)
class DisjointLines(Primitive):
    lines: List[Line]

    def draw(self, stroke_width: int = 1, stroke: str = "black", fill: str = "none") -> str:
        return "".join(line.draw(stroke_width=stroke_width, stroke=stroke, fill=fill) for line in self.lines)
