import logging
from copy import deepcopy
from typing import Any, Dict
from typing import List

from .common import compute_piece_metadata

logger = logging.getLogger(__name__)


def pack_shelf_fit_bwf(input_data: Dict[str, Any], version: str = "Shelf Fit BWF") -> Dict[str, Any]:
    logger.info(f"========= {version} =========")

    fabric_width = input_data["fabric_width_cm"]
    fabric_length = input_data["fabric_length_cm"]
    fabric_margin = input_data["fabric_margin_cm"]

    pieces = [compute_piece_metadata(p) for p in input_data["pieces"]]

    shelves: List[Dict[str, float]] = []
    shelf_piece_ids: List[List[str]] = []
    placements: List[Dict[str, Any]] = []

    total_placed_area = 0.0
    placed_piece_count = 0

    for piece in pieces:
        piece_width = piece["width_cm"]
        piece_height = piece["height_cm"]

        best_fit_index = None
        min_remaining_width = float("inf")

        # Try all existing shelves
        for idx, shelf in enumerate(shelves):
            if piece_height <= shelf["height_cm"]:
                remaining_width = fabric_width - (shelf["x_cursor"] + piece_width)
                if 0 <= remaining_width < min_remaining_width:
                    best_fit_index = idx
                    min_remaining_width = remaining_width

        if best_fit_index is not None:
            # Place in best fitting shelf
            shelf = shelves[best_fit_index]
            x_position = shelf["x_cursor"]
            y_position = shelf["y_cm"]
            shelf["x_cursor"] += piece_width + fabric_margin
            shelf_piece_ids[best_fit_index].append(piece["id"])
        else:
            # Create new shelf
            y_position = (
                shelves[-1]["y_cm"] + shelves[-1]["height_cm"] + fabric_margin
                if shelves else 0.0
            )
            if y_position + piece_height > fabric_length:
                logger.info(f"Skipping '{piece['id']}' – no vertical space.")
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

    logger.info(f"Total shelves used: {len(shelves)}")
    for i, ids in enumerate(shelf_piece_ids):
        logger.info(f"  Shelf {i} (y = {shelves[i]['y_cm']}, height = {shelves[i]['height_cm']}):")
        for pid in ids:
            logger.info(f"    - {pid}")

    total_area = fabric_width * fabric_length
    waste_area = total_area - total_placed_area

    return {
        "version": version,
        "placements": placements,
        "fabric_width_cm": fabric_width,
        "fabric_length_cm": fabric_length,
        "placed_count": placed_piece_count,
        "total_count": len(pieces),
        "placed_area_cm2": round(total_placed_area, 2),
        "waste_area_cm2": round(waste_area, 2),
    }


def pack_shelf_fit_bfdh(input_data: Dict[str, Any]) -> Dict[str, Any]:
    sorted_input = deepcopy(input_data)

    # Sort pieces by height descending
    pieces_with_meta = [
        (piece, compute_piece_metadata(piece)) for piece in sorted_input["pieces"]
    ]
    pieces_with_meta.sort(key=lambda x: x[1]["height_cm"], reverse=True)
    sorted_input["pieces"] = [piece for piece, _ in pieces_with_meta]

    # Call base BWF algorithm
    return pack_shelf_fit_bwf(sorted_input, "Shelf Fit BFDH")
