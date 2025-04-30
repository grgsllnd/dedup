import logging
from datetime import datetime
from pathlib import Path

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger that writes to logs/<name>_YYYYMMDD_HHMMSS.log.
    """
    log = logging.getLogger(name)
    if not log.handlers:
        log.setLevel(logging.INFO)
        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / f"{name}_{datetime.now():%Y%m%d_%H%M%S}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        handler.setFormatter(fmt)
        log.addHandler(handler)
    return log