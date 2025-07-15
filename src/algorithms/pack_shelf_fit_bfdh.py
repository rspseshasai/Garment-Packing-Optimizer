"""
Best‑Fit Decreasing Height (BFDH) shelf packing.
"""

import logging
from typing import Any, Dict, List

from .common import compute_piece_metadata

logger = logging.getLogger(__name__)


def pack_shelf_fit_bfdh(input_data: Dict[str, Any]) -> Dict[str, Any]:

    fabric_w = input_data["fabric_width_cm"]
    fabric_l = input_data["fabric_length_cm"]
    # if fabric_l<fabric_w:
    #     temp = fabric_l
    #     fabric_l = fabric_w
    #     fabric_w = temp
    margin   = input_data["fabric_margin_cm"]

    # preprocess
    pieces = [compute_piece_metadata(p) for p in input_data["pieces"]]
    # sort by height descending
    pieces.sort(key=lambda p: p["height_cm"], reverse=True)

    shelves: List[Dict[str, float]] = []
    placements: List[Dict[str, Any]] = []
    placed_area = 0.0
    placed_count = 0

    for piece in pieces:
        w, h = piece["width_cm"], piece["height_cm"]
        best_shelf_idx = None
        best_leftover = float("inf")

        # try to fit into existing shelves (best‐fit)
        for idx, shelf in enumerate(shelves):
            if h <= shelf["height_cm"]:
                rem_w = fabric_w - (shelf["x_cursor"] + w)
                if rem_w >= 0 and rem_w < best_leftover:
                    best_leftover = rem_w
                    best_shelf_idx = idx

        if best_shelf_idx is not None:
            # place in the best shelf
            shelf = shelves[best_shelf_idx]
            x0 = shelf["x_cursor"]
            y0 = shelf["y_cm"]
            shelf["x_cursor"] += w + margin

        else:
            # start a new shelf
            y0 = (shelves[-1]["y_cm"] + shelves[-1]["height_cm"] + margin
                  if shelves else 0.0)
            # no room vertically
            if y0 + h > fabric_l:
                # logger.info("Skipping '%s': no vertical space for new shelf", piece["id"])
                continue
            shelves.append({
                "y_cm": y0,
                "height_cm": h,
                "x_cursor": w + margin,
            })
            x0 = 0.0

        # record placement
        placements.append({
            "id": piece["id"],
            "x_cm": x0,
            "y_cm": y0,
            "normalized_vertices_cm": piece["normalized_vertices_cm"],
        })
        placed_area += piece["area_cm2"]
        placed_count += 1
        # logger.info("Placed '%s' at shelf y=%.1f, x=%.1f", piece["id"], y0, x0)

    total_area = fabric_w * fabric_l
    waste = total_area - placed_area

    return {
        "version":          "Shelf Fit BFDH",
        "placements":       placements,
        "fabric_width_cm":  fabric_w,
        "fabric_length_cm": fabric_l,
        "placed_count":     placed_count,
        "total_count":      len(pieces),
        "placed_area_cm2":  round(placed_area, 2),
        "waste_area_cm2":   round(waste, 2),
    }
