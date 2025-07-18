import yaml
from typing import Dict


def load_yaml_config(path: str = "config.yaml") -> Dict:

    with open(path, "r") as file:
        return yaml.safe_load(file)
