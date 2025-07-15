from pathlib import Path
from typing import Dict, Any, List

from src.algorithms import PACKERS
from src.utils.config_loader import load_yaml_config
from src.utils.io_utils import load_input_data
from visualize import plot_packing_results, print_summary_table


def main() -> None:
    config = load_yaml_config()
    data_path = Path(config.get("input_file", "../inputs/input1.json"))
    input_data = load_input_data(data_path)

    results: List[Dict[str, Any]] = []
    for pack in PACKERS:
        res = pack(input_data)
        results.append(res)

    print_summary_table(results)
    plot_packing_results(results)


if __name__ == "__main__":
    main()
