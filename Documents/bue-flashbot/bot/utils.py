import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

os.makedirs(LOG_DIR, exist_ok=True)


def get_log_path(prefix):
    date_str = datetime.now().strftime('%Y%m%d')
    return os.path.join(LOG_DIR, f"{prefix}_{date_str}.log")


def setup_logger(name, prefix):
    log_path = get_log_path(prefix)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(log_path, mode='a')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def detect_mode(args):
    if args.sim:
        return 'SIM'
    elif args.live:
        return 'LIVE'
    elif args.historical:
        return 'HISTORICAL'
    return 'SIM' 