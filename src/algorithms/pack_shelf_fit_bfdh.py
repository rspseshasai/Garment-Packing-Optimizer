"""
Best‑Fit Decreasing Height (BFDH) shelf packing.
"""

import logging
from typing import Any, Dict, List

from .common import compute_piece_metadata

logger = logging.getLogger(__name__)


def pack_shelf_fit_bfdh(input_data: Dict[str, Any]) -> Dict[str, Any]:

    logger.info("========= Shelf Fit BFDH =========")

    fabric_width = input_data["fabric_width_cm"]
    fabric_length = input_data["fabric_length_cm"]
    fabric_margin = input_data["fabric_margin_cm"]

    # Step 1: Preprocess pieces and sort by height (tallest first)
    piece_metadata = [compute_piece_metadata(piece) for piece in input_data["pieces"]]
    piece_metadata.sort(key=lambda p: p["height_cm"], reverse=True)

    shelves: List[Dict[str, float]] = []
    shelf_piece_ids: List[List[str]] = []
    placements: List[Dict[str, Any]] = []

    total_placed_area = 0.0
    placed_piece_count = 0

    # Step 2: Place each piece
    for piece in piece_metadata:
        piece_width = piece["width_cm"]
        piece_height = piece["height_cm"]

        best_fit_shelf_index = None
        smallest_remaining_width = float("inf")

        # Try fitting into an existing shelf (best fit)
        for index, shelf in enumerate(shelves):
            if piece_height <= shelf["height_cm"]:
                remaining_width = fabric_width - (shelf["x_cursor"] + piece_width)
                if remaining_width >= 0 and remaining_width < smallest_remaining_width:
                    best_fit_shelf_index = index
                    smallest_remaining_width = remaining_width

        # Place in best-fit shelf if found
        if best_fit_shelf_index is not None:
            shelf = shelves[best_fit_shelf_index]
            x_position = shelf["x_cursor"]
            y_position = shelf["y_cm"]
            shelf["x_cursor"] += piece_width + fabric_margin
            shelf_piece_ids[best_fit_shelf_index].append(piece["id"])

        else:
            # Start a new shelf
            y_position = (
                shelves[-1]["y_cm"] + shelves[-1]["height_cm"] + fabric_margin
                if shelves else 0.0
            )
            if y_position + piece_height > fabric_length:
                # Skip if vertical space is insufficient
                continue

            shelves.append({
                "y_cm": y_position,
                "height_cm": piece_height,
                "x_cursor": piece_width + fabric_margin
            })
            shelf_piece_ids.append([piece["id"]])
            x_position = 0.0

        # Record placement
        placements.append({
            "id": piece["id"],
            "x_cm": x_position,
            "y_cm": y_position,
            "normalized_vertices_cm": piece["normalized_vertices_cm"],
        })

        total_placed_area += piece["area_cm2"]
        placed_piece_count += 1

    # Step 3: Print shelf summary
    logger.info(f"Total shelves used: {len(shelves)}")
    for shelf_index, piece_ids in enumerate(shelf_piece_ids):
        y = shelves[shelf_index]["y_cm"]
        h = shelves[shelf_index]["height_cm"]
        logger.info(f"  Shelf {shelf_index} (y = {y} cm, height = {h} cm):")
        for piece_id in piece_ids:
            logger.info(f"    - {piece_id}")

    # Step 4: Return result
    total_fabric_area = fabric_width * fabric_length
    fabric_waste_area = total_fabric_area - total_placed_area

    return {
        "version": "Shelf Fit BFDH",
        "placements": placements,
        "fabric_width_cm": fabric_width,
        "fabric_length_cm": fabric_length,
        "placed_count": placed_piece_count,
        "total_count": len(piece_metadata),
        "placed_area_cm2": round(total_placed_area, 2),
        "waste_area_cm2": round(fabric_waste_area, 2),
    }
