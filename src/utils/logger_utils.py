import logging
import os
import sys
import coloredlogs

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(filename)s -- %(message)s'
LOG_DIR = os.path.join('../logs', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, f'garment_packing_optimizer.log')

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)

FIELD_STYLES = {
    'asctime': {'color': 'green'},
    'levelname': {'color': 'black', 'bold': True},
    'filename': {'color': 'magenta'},
}
LEVEL_STYLES = {
    'debug': {'color': 'blue'},
    'info': {'color': 'black'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red'},
    'critical': {'color': 'red', 'bold': True},
}

coloredlogs.install(
    level='INFO',
    logger=logging.getLogger(__name__),
    fmt=LOG_FORMAT,
    level_styles=LEVEL_STYLES,
    field_styles=FIELD_STYLES,
)

logger = logging.getLogger(__name__)