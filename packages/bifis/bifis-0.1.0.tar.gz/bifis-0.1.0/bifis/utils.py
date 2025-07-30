"""
Utility classes and constants for the BiFIS framework.

This module provides:
- Configuration file handling through the Config class
- Enhanced command-line argument parsing with Rich console integration
- Global constants for random number generation and data types
- Standardized console output via Rich
"""

# 🐍 Python
import json
import argparse

# 📊 Data
import numpy as np
from rich.console import Console


class Config:
    """
    Configuration manager that loads settings from JSON files.

    Provides dictionary-like access to configuration parameters with
    additional utility methods for checking parameter existence.

    Attributes:
        _config (dict): Internal dictionary holding configuration values

    Examples:
        >>> config = Config("config.json")
        >>> print(config["domain"])
        [0, 1, 0, 1]
        >>> config.exists("sampling_method")
        True
    """

    def __init__(self, path) -> None:
        """
        Initialize configuration by loading from a JSON file.

        Args:
            path (str): Path to the JSON configuration file
        """

        with open(path, "r") as jsonfile:
            self._config = json.load(jsonfile)

        console.print("✅ Config {} loaded...".format(path))

    def __getitem__(self, key):
        """
        Access configuration values using dictionary syntax.

        Args:
            key (str): Configuration parameter name

        Returns:
            The value associated with the key

        Raises:
            KeyError: If the key doesn't exist in the configuration
        """

        return self._config[key]

    def __setitem__(self, key, data):
        """
        Set configuration values using dictionary syntax.

        Args:
            key (str): Configuration parameter name
            data: Value to store
        """

        self._config[key] = data

    def exists(self, key: str) -> bool:
        """
        Check if a configuration parameter exists.

        Args:
            key (str): Configuration parameter name to check

        Returns:
            bool: True if parameter exists, False otherwise
        """

        return True if key in self._config else False

    def to_dict(self) -> dict:
        """
        Convert configuration to a standard dictionary.

        Returns:
            dict: The configuration as a plain dictionary
        """

        return self._config


class RichArgumentParser(argparse.ArgumentParser):
    """
    Enhanced argument parser with Rich console formatting.

    Extends the standard argparse.ArgumentParser with Rich console
    integration for more visually appealing command-line interfaces.
    """

    def _print_message(self, message, file=None):
        """
        Override default message printing to use Rich console.

        Args:
            message (str): Message to print
            file: Ignored, output always goes to Rich console
        """

        console.print(message)

    def add_argument_group(self, *args, **kwargs):
        """
        Add an argument group with enhanced formatting.

        Args:
            *args: Arguments to pass to parent method
            **kwargs: Keyword arguments to pass to parent method

        Returns:
            argparse._ArgumentGroup: The created argument group
        """

        group = super().add_argument_group(*args, **kwargs)
        group.title = f"[cyan]{group.title.title()}[/cyan]"
        return group


class RichRawTextHelpFormatter(argparse.RawTextHelpFormatter):
    """
    Custom help formatter that applies Rich styling to help text.

    Enhances the standard RawTextHelpFormatter by adding yellow
    highlighting to help text lines.
    """

    def _split_lines(self, text, width):
        """
        Split text into lines and apply Rich formatting.

        Args:
            text (str): The help text to format
            width (int): Maximum line width

        Returns:
            list: Formatted lines with Rich markup
        """

        return [f"[yellow]{line}[/yellow]" for line in text.splitlines()]


# Global constants
SEED = 42  # Random seed for reproducibility
TYPE = np.float64  # Default numeric data type

# Initialize random number generator with seed
rng = np.random.default_rng(seed=SEED)

# Initialize Rich console for output
console = Console()
