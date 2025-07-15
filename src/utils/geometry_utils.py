from typing import List, Tuple


def calculate_bounding_box(
    vertices: List[List[float]]
) -> Tuple[float, float, float, float]:

    xs, ys = zip(*vertices)
    return min(xs), min(ys), max(xs), max(ys)


def calculate_polygon_area(vertices: List[List[float]]) -> float:

    area = 0.0
    n = len(vertices)
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        area += x0 * y1 - x1 * y0
    return abs(area) * 0.5
