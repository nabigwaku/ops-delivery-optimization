"""utils.py — Shared helper functions."""

import yaml
from pathlib import Path


def load_config(config_path: str = None) -> dict:
    """Load config.yaml from project root."""
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def pct(value: float, decimals: int = 1) -> str:
    """Format a float (0–1) as a percentage string."""
    return f"{value * 100:.{decimals}f}%"


def usd(value: float) -> str:
    """Format a float as a USD string."""
    return f"${value:,.2f}"
