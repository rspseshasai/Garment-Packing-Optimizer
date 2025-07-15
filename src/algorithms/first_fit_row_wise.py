from typing import Any, Dict, List

from .common import compute_piece_metadata
from ..utils.logger_utils import logger


def pack_first_fit_row_wise(input_data: Dict[str, Any]) -> Dict[str, Any]:

    fabric_w = input_data["fabric_width_cm"]
    fabric_l = input_data["fabric_length_cm"]
    margin = input_data["fabric_margin_cm"]

    pieces = [compute_piece_metadata(p) for p in input_data["pieces"]]

    placements: List[Dict[str, Any]] = []
    x_cursor = 0.0
    y_cursor = 0.0
    max_row_h = 0.0
    placed_area = 0.0
    placed_count = 0

    for piece in pieces:

        w, h = piece["width_cm"], piece["height_cm"]

        if x_cursor + w > fabric_w:
            # start new row
            x_cursor = 0.0
            y_cursor += max_row_h + margin
            max_row_h = 0.0

        if y_cursor + h > fabric_l:
            # logger.info("Skipping piece '%s': no vertical space", piece["id"])
            continue

        placements.append({
            "id": piece["id"],
            "x_cm": x_cursor,
            "y_cm": y_cursor,
            "normalized_vertices_cm": piece["normalized_vertices_cm"],
        })
        # logger.info("Placed piece '%s' at (%.2f, %.2f)", piece["id"], x_cursor, y_cursor)

        x_cursor += w + margin
        max_row_h = max(max_row_h, h)
        placed_area += piece["area_cm2"]
        placed_count += 1

    total_area = fabric_w * fabric_l
    waste = total_area - placed_area

    return {
        "version": "First-Fit Row-Wise",
        "placements": placements,
        "fabric_width_cm": fabric_w,
        "fabric_length_cm": fabric_l,
        "placed_count": placed_count,
        "total_count": len(pieces),
        "placed_area_cm2": round(placed_area, 2),
        "waste_area_cm2": round(waste, 2),
    }
