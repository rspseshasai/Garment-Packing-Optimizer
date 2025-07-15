import logging
from typing import Any, Dict, List

from .common import compute_piece_metadata

logger = logging.getLogger(__name__)


def pack_shelf_fit_bhf(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Shelf Best Height Fit (SHELF-BHF) algorithm:
    For each piece, find the shelf with closest height where it fits.
    If none fit, create a new shelf.
    """
    logger.info("========= Shelf Fit BHF =========")

    fabric_width = input_data["fabric_width_cm"]
    fabric_length = input_data["fabric_length_cm"]
    fabric_margin = input_data["fabric_margin_cm"]

    piece_metadata = [compute_piece_metadata(piece) for piece in input_data["pieces"]]

    shelves: List[Dict[str, float]] = []
    shelf_piece_ids: List[List[str]] = []
    placements: List[Dict[str, Any]] = []

    total_placed_area = 0.0
    placed_piece_count = 0

    for piece in piece_metadata:
        piece_width = piece["width_cm"]
        piece_height = piece["height_cm"]

        best_shelf_index = None
        smallest_height_diff = float("inf")

        # Try fitting into existing shelves based on best height match
        for index, shelf in enumerate(shelves):
            if piece_height <= shelf["height_cm"]:
                height_diff = shelf["height_cm"] - piece_height
                remaining_width = fabric_width - (shelf["x_cursor"] + piece_width)

                if remaining_width >= 0 and height_diff < smallest_height_diff:
                    best_shelf_index = index
                    smallest_height_diff = height_diff

        # If a matching shelf is found, place the piece there
        if best_shelf_index is not None:
            shelf = shelves[best_shelf_index]
            x_position = shelf["x_cursor"]
            y_position = shelf["y_cm"]
            shelf["x_cursor"] += piece_width + fabric_margin
            shelf_piece_ids[best_shelf_index].append(piece["id"])

        else:
            # Create new shelf
            y_position = (
                shelves[-1]["y_cm"] + shelves[-1]["height_cm"] + fabric_margin
                if shelves else 0.0
            )

            if y_position + piece_height > fabric_length:
                logger.info(f"Skipping '{piece['id']}' – no vertical space left.")
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

    # Shelf summary log
    logger.info(f"Total shelves used: {len(shelves)}")
    for i, shelf in enumerate(shelves):
        logger.info(
            f"  Shelf {i} (y = {shelf['y_cm']} cm, height = {shelf['height_cm']} cm):"
        )
        for pid in shelf_piece_ids[i]:
            logger.info(f"    - {pid}")

    total_area = fabric_width * fabric_length
    waste_area = total_area - total_placed_area

    return {
        "version": "Shelf Fit BHF",
        "placements": placements,
        "fabric_width_cm": fabric_width,
        "fabric_length_cm": fabric_length,
        "placed_count": placed_piece_count,
        "total_count": len(piece_metadata),
        "placed_area_cm2": round(total_placed_area, 2),
        "waste_area_cm2": round(waste_area, 2),
    }
