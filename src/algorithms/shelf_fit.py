"""
Shelf‐Fit packing algorithm (smart first‐fit by width).
"""

import logging
from typing import Any, Dict, List

from .common import compute_piece_metadata

logger = logging.getLogger(__name__)


def pack_shelf_fit(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Arrange pieces on “shelves,” each shelf holding same‐height pieces.

    Args:
        input_data: dict with fabric dims, margin, and pieces.

    Returns:
        A result dict with placements and statistics.
    """
    fabric_w = input_data["fabric_width_cm"]
    fabric_l = input_data["fabric_length_cm"]
    margin = input_data["fabric_margin_cm"]

    pieces = [compute_piece_metadata(p) for p in input_data["pieces"]]
    pieces.sort(key=lambda p: p["width_cm"], reverse=True)

    placements: List[Dict[str, Any]] = []
    shelves: List[Dict[str, Any]] = []
    placed_area = 0.0
    placed_count = 0

    for piece in pieces:
        w, h = piece["width_cm"], piece["height_cm"]
        placed = False

        # try existing shelves
        for shelf in shelves:
            if shelf["x_cursor"] + w <= fabric_w and h <= shelf["height_cm"]:
                x0 = shelf["x_cursor"]
                y0 = shelf["y_cm"]
                shelf["x_cursor"] += w + margin
                placements.append({
                    "id": piece["id"],
                    "x_cm": x0,
                    "y_cm": y0,
                    "normalized_vertices_cm": piece["normalized_vertices_cm"],
                })
                placed_area += piece["area_cm2"]
                placed_count += 1
                placed = True
                break

        if not placed:
            # start a new shelf
            next_y = (shelves[-1]["y_cm"] + shelves[-1]["height_cm"] + margin
                      if shelves else 0.0)
            if next_y + h > fabric_l:
                continue
            shelves.append({
                "y_cm": next_y,
                "height_cm": h,
                "x_cursor": w + margin,
            })
            placements.append({
                "id": piece["id"],
                "x_cm": 0.0,
                "y_cm": next_y,
                "normalized_vertices_cm": piece["normalized_vertices_cm"],
            })
            placed_area += piece["area_cm2"]
            placed_count += 1

    total_area = fabric_w * fabric_l
    waste = total_area - placed_area

    return {
        "version": "Shelf Fit",
        "placements": placements,
        "fabric_width_cm": fabric_w,
        "fabric_length_cm": fabric_l,
        "placed_count": placed_count,
        "total_count": len(pieces),
        "placed_area_cm2": round(placed_area, 2),
        "waste_area_cm2": round(waste, 2),
    }
