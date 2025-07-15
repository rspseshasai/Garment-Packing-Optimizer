from typing import Any, Dict

from src.utils.geometry_utils import calculate_bounding_box, calculate_polygon_area


def compute_piece_metadata(piece: Dict[str, Any]) -> Dict[str, Any]:

    piece_vertices = piece["vertices_cm"]
    x_min, y_min, x_max, y_max = calculate_bounding_box(piece_vertices)
    normalized = [[x - x_min, y - y_min] for x, y in piece_vertices]
    return {
        "id": piece["id"],
        "width_cm": x_max - x_min,
        "height_cm": y_max - y_min,
        "area_cm2": calculate_polygon_area(piece_vertices),
        "normalized_vertices_cm": normalized,
    }
