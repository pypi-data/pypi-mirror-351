# SPDX-FileCopyrightText: 2025 Dimitris Kardarakos
# SPDX-License-Identifier: AGPL-3.0-only

import logging
from pathlib import Path
from datetime import datetime
from xdg.BaseDirectory import xdg_state_home

LOG_LEVEL = "DEBUG"

log_dir_path = Path(f"{xdg_state_home}/geekar")

if not log_dir_path.is_dir():
    log_dir_path.mkdir()


log_file_path = Path(
    f"{log_dir_path.resolve()}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

formatter = logging.Formatter("[%(levelname)s] %(asctime)s : %(message)s")
file_handler = logging.FileHandler(log_file_path, mode="w", encoding="utf-8")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
