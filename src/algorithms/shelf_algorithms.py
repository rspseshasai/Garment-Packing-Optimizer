import logging
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from .common import compute_piece_metadata
from ..utils.logger_utils import logger


class Shelf:
    """Represents a horizontal shelf for placing rectangles."""

    def __init__(self, y: float, height: float, margin: float, fabric_width: Optional[float] = None):
        self.y = y
        self.height = height
        self.margin = margin
        self.x_cursor = 0.0
        self.piece_ids: List[str] = []

        # only used by Floor–Ceiling variant
        self.ceil_x: Optional[float] = fabric_width
        self.closed: bool = False

    def can_place_floor(self, width: float, height: float, fabric_width: float) -> bool:
        return height <= self.height and (self.x_cursor + width) <= fabric_width

    def place_on_floor(self, piece_id: str, width: float) -> float:
        x_pos = self.x_cursor
        self.x_cursor += width + self.margin
        self.piece_ids.append(piece_id)
        return x_pos

    def can_place_ceiling(self, width: float, height: float) -> bool:
        if not self.closed or self.ceil_x is None:
            return False
        return height <= self.height and (self.ceil_x - width) >= self.x_cursor

    def place_on_ceiling(self, piece_id: str, width: float, height: float) -> Tuple[float, float]:
        assert self.ceil_x is not None
        x_pos = self.ceil_x - width
        y_pos = self.y + self.height - height
        self.ceil_x -= width + self.margin
        self.piece_ids.append(piece_id)
        return x_pos, y_pos


def _shelf_fit_base(
    metas: List[Dict[str, Any]],
    fabric_width: float,
    fabric_length: float,
    margin: float
) -> Tuple[List[Dict[str, Any]], List[Shelf], float, int]:
    """
    Core Best‑Width Fit shelf logic.
    Returns (placements, shelves, placed_area, placed_count).
    """
    placements: List[Dict[str, Any]] = []
    shelves: List[Shelf] = []
    placed_area = 0.0
    placed_count = 0
    placement_order = 1
    for meta in metas:
        pid = meta["id"]
        width = meta["width_cm"]
        height = meta["height_cm"]

        # 1) Find best existing shelf by minimal leftover width
        best_idx: Optional[int] = None
        best_leftover = fabric_width + 1
        for i, shelf in enumerate(shelves):
            if shelf.can_place_floor(width, height, fabric_width):
                leftover = fabric_width - (shelf.x_cursor + width)
                if leftover < best_leftover:
                    best_leftover = leftover
                    best_idx = i

        # 2) Place on chosen shelf or open new one
        if best_idx is not None:
            shelf = shelves[best_idx]
            x = shelf.place_on_floor(pid, width)
            y = shelf.y
        else:
            y = (shelves[-1].y + shelves[-1].height + margin) if shelves else 0.0
            if y + height > fabric_length:
                # logger.info("Skipping '%s': no vertical space", pid)
                continue
            shelf = Shelf(y, height, margin)
            shelves.append(shelf)
            x = shelf.place_on_floor(pid, width)

        # 3) Record placement
        placements.append({
            "id": pid,
            "x_cm": x,
            "y_cm": y,
            "normalized_vertices_cm": meta["normalized_vertices_cm"],
            "placement_order" : placement_order,
        })
        # logger.info("Placed '%s' at (%.2f, %.2f)", pid, x, y)
        placement_order += 1
        placed_area += meta["area_cm2"]
        placed_count += 1

    return placements, shelves, placed_area, placed_count


def pack_shelf_fit_bwf(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Shelf Fit – Best Width Fit.
    Greedily places each piece in the shelf with least leftover width.
    """
    version = "Shelf Fit BWF"
    # logger.info("========= %s =========", version)

    fw = input_data["fabric_width_cm"]
    fl = input_data["fabric_length_cm"]
    m = input_data["fabric_margin_cm"]
    metas = [compute_piece_metadata(p) for p in input_data["pieces"]]

    placements, shelves, area, count = _shelf_fit_base(metas, fw, fl, m)
    waste = fw * fl - area

    return {
        "version": version,
        "placements": placements,
        "shelves": [{"y_cm": s.y, "height_cm": s.height} for s in shelves],
        "fabric_width_cm": fw,
        "fabric_length_cm": fl,
        "placed_count": count,
        "total_count": len(metas),
        "placed_area_cm2": round(area, 2),
        "waste_area_cm2": round(waste, 2),
    }


def pack_shelf_fit_bfdh(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Shelf Fit – Best Fit Decreasing Height.
    Sorts pieces by height descending, then applies BWF logic.
    """
    version = "Shelf Fit BFDH"
    # logger.info("========= %s =========", version)

    data = deepcopy(input_data)
    metas = [compute_piece_metadata(p) for p in data["pieces"]]
    metas.sort(key=lambda m: m["height_cm"], reverse=True)

    placements, shelves, area, count = _shelf_fit_base(
        metas,
        data["fabric_width_cm"],
        data["fabric_length_cm"],
        data["fabric_margin_cm"]
    )
    waste = data["fabric_width_cm"] * data["fabric_length_cm"] - area

    return {
        "version": version,
        "placements": placements,
        "shelves": [{"y_cm": s.y, "height_cm": s.height} for s in shelves],
        "fabric_width_cm": data["fabric_width_cm"],
        "fabric_length_cm": data["fabric_length_cm"],
        "placed_count": count,
        "total_count": len(metas),
        "placed_area_cm2": round(area, 2),
        "waste_area_cm2": round(waste, 2),
    }


def pack_shelf_floor_ceiling(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Shelf Fit – Floor–Ceiling variant.
    Sorts by longest side descending, uses open-shelf floor first,
    then closed-shelf ceiling, then opens new shelf.
    """
    version = "Shelf Floor-Ceiling"
    # logger.info("========= %s =========", version)
    placement_order = 1

    data = deepcopy(input_data)
    fw = data["fabric_width_cm"]
    fl = data["fabric_length_cm"]
    m = data["fabric_margin_cm"]

    # 1) Sort by longest side descending
    metas = [compute_piece_metadata(p) for p in data["pieces"]]
    metas.sort(key=lambda m: max(m["width_cm"], m["height_cm"]), reverse=True)

    placements: List[Dict[str, Any]] = []
    shelves: List[Shelf] = []
    total_area = 0.0
    placed_count = 0
    next_shelf_y = 0.0

    for meta in metas:
        pid = meta["id"]
        w0, h0 = meta["width_cm"], meta["height_cm"]
        poly0 = meta["normalized_vertices_cm"]

        # logger.info("Attempting '%s' (w:%.1f, h:%.1f)", pid, w0, h0)
        placed = False

        # 2) Try open-shelf floor
        if shelves and not shelves[-1].closed:
            sh = shelves[-1]
            # logger.info("  Floor check at y=%.1f, height=%.1f, x_cursor=%.1f", sh.y, sh.height, sh.x_cursor)
            for w, h, rot in ((w0, h0, False), (h0, w0, True)) if w0 != h0 else ((w0, h0, False),):
                # logger.info("    Floor attempt (%s): %0.fx×%0.fx", "rotated" if rot else "upright", w, h)
                if sh.can_place_floor(w, h, fw):
                    poly = [[y, x] for x, y in poly0] if rot else poly0
                    x = sh.place_on_floor(pid, w)
                    y = sh.y
                    # logger.info("    Placed on floor at (%.1f, %.1f)", x, y)
                    placed = True
                    break
                else:
                    # logger.info("    Does not fit on floor")
                    pass


        # 3) Close shelf if floor failed
        if not placed and shelves and not shelves[-1].closed:
            shelves[-1].closed = True
            # logger.info("  Closing shelf at y=%.1f", shelves[-1].y)

        # 4) Try closed-shelf ceilings
        if not placed:
            for sh in shelves:
                if not sh.closed:
                    continue
                # logger.info("  Ceiling check at y=%.1f, height=%.1f, ceil_x=%.1f", sh.y, sh.height, sh.ceil_x)
                for w, h, rot in ((w0, h0, False), (h0, w0, True)):
                    # logger.info("    Ceiling attempt (%s): %0.fx×%0.fx", "rotated" if rot else "upright", w, h)
                    if sh.can_place_ceiling(w, h):
                        poly = [[y, x] for x, y in poly0] if rot else poly0
                        x, y = sh.place_on_ceiling(pid, w, h)
                        # logger.info("    Placed on ceiling at (%.1f, %.1f)", x, y)
                        placed = True
                        break
                    else:
                        # logger.info("    Does not fit on ceiling")
                        pass
                if placed:
                    break

        # 5) Open a new shelf if still unplaced
        if not placed:
            # choose orientation to minimize shelf height
            if h0 > w0:
                shelf_h, shelf_w, rot = w0, h0, True
                poly = [[y, x] for x, y in poly0]
            else:
                shelf_h, shelf_w, rot = h0, w0, False
                poly = poly0

            if next_shelf_y + shelf_h > fl:
                # logger.warning("Skipping '%s' – no vertical space for new shelf", pid)
                continue

            sh = Shelf(next_shelf_y, shelf_h, m, fw)
            shelves.append(sh)
            # logger.info("  Opened new shelf at y=%.1f, height=%.1f", next_shelf_y, shelf_h)
            x = sh.place_on_floor(pid, shelf_w)
            y = sh.y
            # logger.info("    Placed on floor at (%.1f, %.1f)", x, y)
            next_shelf_y += shelf_h + m

        # record final placement
        if placed or not shelves or shelves[-1].piece_ids[-1] == pid:
            placements.append({
                "id": pid,
                "x_cm": x,
                "y_cm": y,
                "normalized_vertices_cm": poly,
                "placement_order": placement_order
            })
            total_area += meta["area_cm2"]
            placed_count += 1
            placement_order += 1

    waste = fw * fl - total_area
    return {
        "version": version,
        "placements": placements,
        "shelves": [{"y_cm": s.y, "height_cm": s.height} for s in shelves],
        "fabric_width_cm": fw,
        "fabric_length_cm": fl,
        "placed_count": placed_count,
        "total_count": len(metas),
        "placed_area_cm2": round(total_area, 2),
        "waste_area_cm2": round(waste, 2),
    }
