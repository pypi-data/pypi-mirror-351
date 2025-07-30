"""Options

This module provides interfaces for managing various options that
affect the way Starch determines how it should format your comments.
"""

# ─── import statements ────────────────────────────────────────────────── ✦✦ ──

# standard library imports
import logging
import json

from pathlib import Path
from typing import Dict, List, Optional, Union

# local imports
from .constants import (
    DATA_DIR, LOG_DIR, CONFIG_DIR, CACHE_DIR, LOGFILE, CONFILE
)

# ─── logger setup ─────────────────────────────────────────────────────── ✦✦ ──

logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
logger = logging.getLogger(__package__)


# ─── interfaces ───────────────────────────────────────────────────────── ✦✦ ──

class Configuration:
    """
    A singleton that serves the central configurator for Starch's formatting
    engine.
    """

    # ─── singleton pattern enforcement ────────────────────────────────────────
    def __new__(cls):
        """Ensure that only one instance of Configuration exists."""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Configuration, cls).__new__(cls)
        else:
            return cls.instance


    def __init__(self, filepath: Optional[Union[str, Path]] = None) -> None:
        """Constructor for the Configuration class."""
        self._config_dir: Path = CONFIG_DIR

        self._config_filepath: Path = (
            Path(filepath) if isinstance(filepath, str)
            else filepath if isinstance(filepath, Path)
            else CONFILE
        )
        
        if not self._config_filepath.exists():
            print("No configuration file found.")
            print("Creating a new configuration file with default settings.")

            try:
                self._config_filepath.touch(exist_ok=True)
                print("Configuration file created at: ", self._config_filepath)
            except Exception as e:
                print(f"Error creating configuration file: {e}")
                self._config_filepath = self._config_dir / "config.json"

        self._options: Dict[str, Union[str, List[str]]] = {
            "cpp": {
                "length": 100,
                "prefix": "// ─── ",
                "suffix": " ✦✦ ──"
            },
            "haskell": {
                "length": 90,
                "prefix": "-- ─── ",
                "suffix": " ✦✦ ──"
            },
            "python": {
                "length": 79,
                "prefix": "# ─── ",
                "suffix": " ✦✦ ──"
            },
            "rust": {
                "length": 100,
                "prefix": "// ─── ",
                "suffix": " ✦✦ ──"
            },
            "swift": {
                "length": 100,
                "prefix": "// ─── ",
                "suffix": " ✦✦ ──"
            }
        }

        try:
            self.load_config()

            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")


    # ─── property accessors ───────────────────────────────────────────────────

    @property
    def config_filepath(self) -> Path:
        """Return the path to the configuration file."""
        return self._config_filepath

    @config_filepath.setter
    def config_filepath(self, value: Union[str, Path]) -> None:
        """Set the path to the configuration file."""
        self._config_filepath = (
            Path(value) if isinstance(value, str)
            else value if isinstance(value, Path)
            else self._config_dir / "config.json"
        )

    @config_filepath.deleter
    def config_filepath(self) -> None:
        return UserWarning(
            "Deleting the configuration file path is not allowed."
        )

    @property
    def options(self) -> Dict[str, Union[str, List[str]]]:
        return self._options

    @options.setter
    def options(
        self,
        value: Dict[str, Union[str, List[str]]]
    ) -> None:
        self._options = value

    @options.deleter
    def options(self) -> None:
        return UserWarning(
            "Deleting the options dictionary is not allowed."
        )


    # ─── interface methods ────────────────────────────────────────────────────

    def load_config(self) -> None:
        """Load the configuration from the file."""
        try:
            with open(self._config_filepath, "r") as f:
                self._options = json.load(f)

            logger.info(
                f"Configuration loaded from {self._config_filepath}"
            )
        except FileNotFoundError as e:
            logger.error(
                f"Configuration file {self._config_filepath} not found."
            )
            raise e
        except json.JSONDecodeError as e:
            logger.error(
                f"Error decoding JSON from {self._config_filepath}: {e}"
            )
            raise e        
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise e


    def save_config(self) -> None:
        """Save the options dicionary to the configuration file."""
        try:
            with open(self._config_filepath, "w") as f:
                json.dump(self._options, f, indent=2)
                logger.info(f"Configuration saved to {self._config_filepath}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise e

# ─── API ──────────────────────────────────────────────────────────────── ✦✦ ──
config = Configuration()
