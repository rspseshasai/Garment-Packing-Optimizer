from src.utils.config_loader import load_yaml_config
from .first_fit_row_wise import pack_first_fit_row_wise
from .maxrects_packer import pack_with_maxrects
from .shelf_algorithms import pack_shelf_fit_bwf, pack_shelf_fit_bfdh, pack_shelf_fit_bhf

ALGORITHM_REGISTRY = {
    "first_fit": pack_first_fit_row_wise,
    "shelf_bwf": pack_shelf_fit_bwf,
    "shelf_bfdh": pack_shelf_fit_bfdh,
    "shelf_bhf": pack_shelf_fit_bhf,
    "maxrects": pack_with_maxrects,
}

# Load config and select only enabled algorithms
_config = load_yaml_config()
_enabled_keys = _config.get("algorithms", [])

PACKERS = [ALGORITHM_REGISTRY[key] for key in _enabled_keys if key in ALGORITHM_REGISTRY]
