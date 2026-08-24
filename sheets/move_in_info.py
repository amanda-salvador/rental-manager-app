"""
sheets/move_in_info.py

Read the "Move in info" tab — one row per property, with utility/insurance links.
"""

import pandas as pd
from sheets.client import get_all_records


def get_move_in_info(property_name: str) -> dict | None:
    """Return the Move in info row for a property, or None if not found."""
    df = get_all_records("move_in_info")
    if df.empty:
        return None
    match = df[df["property"] == property_name]
    if match.empty:
        return None
    return match.iloc[0].to_dict()
