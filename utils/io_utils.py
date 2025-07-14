"""
I/O utilities for loading garment‐packing input data.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def load_input_data(path: Path) -> Dict[str, Any]:
    """
    Load and return input data from a JSON file.

    Args:
        path: Path to the JSON input file.

    Returns:
        A dictionary with keys 'fabric_width_cm', 'fabric_length_cm',
        'fabric_margin_cm', and 'pieces'.
    """
    logger.info("Loading input from %s", path)
    raw = path.read_text()
    data = json.loads(raw)
    count = len(data.get("pieces", []))
    logger.info("  → %d pieces loaded", count)
    return data
