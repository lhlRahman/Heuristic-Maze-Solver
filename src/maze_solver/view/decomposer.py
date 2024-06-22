from maze_solver.models.border import Border
from maze_solver.view.primitives import (
    DisjointLines,
    Line,
    Point,
    Polyline,
    Primitive
)

def decompose(border: Border, top_left: Point, square_size: int) -> Primitive:
    bottom_left = top_left.translate(y=square_size)
    bottom_right = top_left.translate(x=square_size, y=square_size)
    top_right = top_left.translate(x=square_size)

    left = Line(top_left, bottom_left)
    top = Line(top_left, top_right)
    right = Line(top_right, bottom_right)
    bottom = Line(bottom_left, bottom_right)

    if border == Border.BOTTOM | Border.LEFT | Border.TOP:
        return Polyline(
            [
                bottom_right,
                bottom_left,
                top_left,
                top_right,
            ]
        )

    if border == Border.LEFT | Border.TOP | Border.RIGHT:
        return Polyline(
            [
                bottom_left,
                top_left,
                top_right,
                bottom_right,
            ]
        )

    if border == Border.TOP | Border.RIGHT | Border.BOTTOM:
        return Polyline(
            [
                top_left,
                top_right,
                bottom_right,
                bottom_left,
            ]
        )

    if border == Border.RIGHT | Border.BOTTOM | Border.LEFT:
        return Polyline(
            [
                top_right,
                bottom_right,
                bottom_left,
                top_left,
            ]
        )

    if border == Border.LEFT | Border.TOP:
        return Polyline(
            [
                bottom_left,
                top_left,
                top_right,
            ]
        )

    if border == Border.TOP | Border.RIGHT:
        return Polyline(
            [
                top_left,
                top_right,
                bottom_right,
            ]
        )

    if border == Border.BOTTOM | Border.LEFT:
        return Polyline(
            [
                bottom_right,
                bottom_left,
                top_left,
            ]
        )

    if border == Border.RIGHT | Border.BOTTOM:
        return Polyline(
            [
                top_right,
                bottom_right,
                bottom_left,
            ]
        )

    if border == Border.LEFT | Border.RIGHT:
        return DisjointLines([left, right])

    if border == Border.TOP | Border.BOTTOM:
        return DisjointLines([top, bottom])

    if border == Border.TOP:
        return top

    if border == Border.RIGHT:
        return right

    if border == Border.BOTTOM:
        return bottom

    if border == Border.LEFT:
        return left

    return DisjointLines([])  # Return an empty DisjointLines if no borders are set
