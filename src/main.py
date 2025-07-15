from pathlib import Path
from typing import Dict, Any, List

from src.algorithms import PACKERS
from src.utils.io_utils import load_input_data
from src.utils.logger_utils import logger
from visualize import plot_packing_results


def display_summary(result: Dict[str, Any]) -> None:
    w_m = result["fabric_width_cm"] / 100
    l_m = result["fabric_length_cm"] / 100
    used_m2 = result["placed_area_cm2"] / 10000
    waste_m2 = result["waste_area_cm2"] / 10000
    utilization = used_m2 / (w_m * l_m) * 100

    logger.info(f"Placed {result['placed_count']}/{result['total_count']} pieces")
    logger.info(f"Fabric: {w_m:.2f} m × {l_m:.2f} m")
    logger.info(f"Total area: {w_m * l_m:.2f} m²")
    logger.info(f"Used area: {used_m2:.3f} m², Waste: {waste_m2:.3f} m², Utilization: {utilization:.1f}%\n")


def main() -> None:
    data_path = Path("../inputs/input2.json")
    input_data = load_input_data(data_path)

    results: List[Dict[str, Any]] = []
    for pack in PACKERS:
        res = pack(input_data)
        display_summary(res)
        results.append(res)

    plot_packing_results(results)


if __name__ == "__main__":
    main()
