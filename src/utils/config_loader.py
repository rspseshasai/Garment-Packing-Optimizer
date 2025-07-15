import yaml
from typing import Dict


def load_yaml_config(path: str = "config.yaml") -> Dict:
    """
    Load configuration from a YAML file.
    """
    with open(path, "r") as file:
        return yaml.safe_load(file)
