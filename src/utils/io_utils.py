import json
from pathlib import Path
from typing import Any, Dict
from .logger_utils import logger


def load_input_data(path: Path) -> Dict[str, Any]:
    logger.info("Loading input from %s", path)
    raw = path.read_text()
    data = json.loads(raw)
    count = len(data.get("pieces", []))
    logger.info("%d pieces loaded\n", count)
    return data
