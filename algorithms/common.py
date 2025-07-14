"""
Shared helpers for all packing algorithms.
"""

from typing import Any, Dict

from utils.geometry_utils import calculate_bounding_box, calculate_polygon_area


def compute_piece_metadata(piece: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute width, height, area, and normalized vertices for one piece.

    Args:
        piece: dict with keys 'id' and 'vertices_cm'.

    Returns:
        {
            'id': str,
            'width_cm': float,
            'height_cm': float,
            'area_cm2': float,
            'normalized_vertices_cm': List[List[float]]
        }
    """
    original = piece["vertices_cm"]
    x_min, y_min, x_max, y_max = calculate_bounding_box(original)
    normalized = [[x - x_min, y - y_min] for x, y in original]
    return {
        "id": piece["id"],
        "width_cm": x_max - x_min,
        "height_cm": y_max - y_min,
        "area_cm2": calculate_polygon_area(original),
        "normalized_vertices_cm": normalized,
    }
