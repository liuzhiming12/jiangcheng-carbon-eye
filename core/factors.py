"""Load carbon emission factors from JSON config file.

Usage:
    from core.factors import load_factors
    factors = load_factors()
    electricity_factor = factors['electricity']['factor']  # 0.4044
"""

import json
import os

_FACTORS_PATH = os.path.join(os.path.dirname(__file__), 'factors.json')


def load_factors(path: str = None) -> dict:
    """Load carbon emission factors from JSON file.

    Args:
        path: path to factors.json (default: auto-detect next to this file)

    Returns:
        dict with factor data, e.g.:
        {
            'electricity': {'factor': 0.4044, 'unit': 'kgCO₂/kWh', ...},
            'natural_gas': {'factor': 2.17, ...},
            'water': {'factor': 0.28, ...}
        }
    """
    if path is None:
        path = _FACTORS_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Factors file not found: {path}. "
            f"Ensure factors.json exists in the core/ directory."
        )

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('factors', data)
