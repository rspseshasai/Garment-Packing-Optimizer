from typing import Any, Dict, List

from rectpack import MaxRectsBssf, PackingMode, newPacker

from .common import compute_piece_metadata
from ..utils.logger_utils import logger


def pack_with_maxrects(input_data: Dict[str, Any]) -> Dict[str, Any]:

    # logger.info(f"\n")
    # logger.info(f"========= ========= MaxRects BSSF ========= =========")
    fabric_w = input_data["fabric_width_cm"]
    fabric_l = input_data["fabric_length_cm"]
    margin = input_data["fabric_margin_cm"]
    placement_order = 1

    usable_w = fabric_w - 2 * margin
    usable_l = fabric_l - 2 * margin

    packer = newPacker(
        mode=PackingMode.Offline,
        pack_algo=MaxRectsBssf,
        rotation=True
    )

    pieces_meta: List[Dict[str, Any]] = []
    for p in input_data["pieces"]:
        meta = compute_piece_metadata(p)
        packer.add_rect(meta["width_cm"], meta["height_cm"], rid=meta["id"])
        pieces_meta.append(meta)

    packer.add_bin(usable_w, usable_l)
    packer.pack()

    placements: List[Dict[str, Any]] = []
    placed_area = 0.0

    for (_bin, x, y, w, h, rid) in packer.rect_list():
        meta = next(m for m in pieces_meta if m["id"] == rid)
        rotated = (w, h) != (meta["width_cm"], meta["height_cm"])
        verts = meta["normalized_vertices_cm"]
        if rotated:
            # swap x/y in normalized vertices
            verts = [[y0, x0] for x0, y0 in verts]

        placements.append({
            "id": rid,
            "x_cm": x + margin,
            "y_cm": y + margin,
            "width_cm": w,
            "height_cm": h,
            "is_rotated": rotated,
            "normalized_vertices_cm": verts,
            "placement_order": placement_order
        })
        placement_order += 1
        placed_area += meta["area_cm2"]
        # logger.info("Placed piece '%s' at (%.2f, %.2f)", rid, x + margin, y + margin)

    total_area = fabric_w * fabric_l
    waste = total_area - placed_area

    return {
        "version": "MaxRects BSSF",
        "placements": placements,
        "fabric_width_cm": fabric_w,
        "fabric_length_cm": fabric_l,
        "placed_count": len(placements),
        "total_count": len(pieces_meta),
        "placed_area_cm2": round(placed_area, 2),
        "waste_area_cm2": round(waste, 2),
    }
