from __future__ import annotations

import logging
from pathlib import Path
from time import strftime


def setup_logger(log_dir: str = "logs") -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("signin_service")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    logfile = logging.FileHandler(Path(log_dir) / f"run-{strftime('%Y%m%d')}.log", encoding="utf-8")
    logfile.setFormatter(formatter)
    logger.addHandler(logfile)

    return logger

