"""
Main script to run all packing algorithms and visualize results.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

from src.utils.io_utils import load_input_data
from src.algorithms import PACKERS
from visualize import plot_packing_results


def display_summary(result: Dict[str, Any]) -> None:
    """
    Print a human‐readable summary of one packing result.

    Args:
        result: dict returned by a pack_* function.
    """
    w_m = result["fabric_width_cm"] / 100
    l_m = result["fabric_length_cm"] / 100
    used_m2 = result["placed_area_cm2"] / 10000
    waste_m2 = result["waste_area_cm2"] / 10000
    utilization = used_m2 / (w_m * l_m) * 100

    print(f"\n=== {result['version']} Summary ===")
    print(f"Placed {result['placed_count']}/{result['total_count']} pieces")
    print(f"Fabric: {w_m:.2f} m × {l_m:.2f} m")
    print(f"Total area: {w_m * l_m:.2f} m²")
    print(f"Used area: {used_m2:.3f} m², Waste: {waste_m2:.3f} m², Utilization: {utilization:.1f}%")


def main() -> None:
    """Load input, run all packers, print summaries, and plot layouts."""
    data_path = Path("../inputs/input1.json")
    input_data = load_input_data(data_path)

    results: List[Dict[str, Any]] = []
    for pack in PACKERS:
        res = pack(input_data)
        display_summary(res)
        results.append(res)

    plot_packing_results(results)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    main()
