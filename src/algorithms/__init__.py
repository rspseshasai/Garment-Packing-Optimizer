import time
from src.utils.config_loader import load_yaml_config
from .first_fit_row_wise import pack_first_fit_row_wise
from .maxrects_packer import pack_with_maxrects
from .shelf_algorithms import pack_shelf_fit_bwf, pack_shelf_fit_bfdh, pack_shelf_floor_ceiling
from ..utils.logger_utils import logger

# Mapping of algorithm keys to packing functions
ALGORITHM_REGISTRY = {
    "first_fit": pack_first_fit_row_wise,
    "shelf_bwf": pack_shelf_fit_bwf,
    "shelf_bfdh": pack_shelf_fit_bfdh,
    "shelf_floor_ceil": pack_shelf_floor_ceiling,
    "maxrects": pack_with_maxrects,
}

# Load config and get enabled algorithm keys
_config = load_yaml_config()
_enabled_keys = _config.get("algorithms", [])

# Wrap each packer with timing logic
def timed_wrapper(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"Algorithm '{func.__name__}' took {duration:.3f} seconds.")
        return result
    return wrapper

# Prepare list of timed packers
PACKERS = [
    timed_wrapper(ALGORITHM_REGISTRY[key])
    for key in _enabled_keys
    if key in ALGORITHM_REGISTRY
]
