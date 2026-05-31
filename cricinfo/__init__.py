"""Python interface for live Cricbuzz cricket data."""

__title__ = "cricinfo"
__version__ = "1.3.0"
__author__ = "Pranith Pashikanti"
__license__ = "GPLv2"

from .cricbuzz import Cricbuzz, CricbuzzError

__all__ = ["Cricbuzz", "CricbuzzError"]
