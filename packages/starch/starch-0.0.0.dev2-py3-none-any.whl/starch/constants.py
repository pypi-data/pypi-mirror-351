"""Constants

This module contains constants used throughout the Starch code package.
"""
# ─── import statements ────────────────────────────────────────────────── ✦✦ ──
# standard library imports

from pathlib import Path
from typing import Final

# third-party imports
from platformdirs import (
    user_cache_path, user_config_path, user_data_path, user_log_path
)

    
# ─── constants ────────────────────────────────────────────────────────── ✦✦ ──
__author__: Final[str] = "k.lebryce"
__version__: Final[str] = "0.0.0"
__package__: Final[str] = "starch"

CACHE_DIR: Final[Path] = user_cache_path(
    __package__.capitalize(), __author__, ensure_exists=True
)

CONFIG_DIR: Final[Path] = user_config_path(
    __package__.capitalize(), __author__, ensure_exists=True
)

DATA_DIR: Final[Path] = user_data_path(
    __package__.capitalize(), __author__, ensure_exists=True
)

LOG_DIR: Final[Path] = user_log_path(
    __package__.capitalize(), __author__, ensure_exists=True
)

CONFILE: Final[Path] = CONFIG_DIR / "config.json"
LOGFILE: Final[Path] = LOG_DIR / "starch.log"
