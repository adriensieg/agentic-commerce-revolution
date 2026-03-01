"""
Burger filtering logic
"""

import logging
from typing import Any, Dict, List

from library_mcp_ordering.data import BURGERS

logger = logging.getLogger(__name__)


def filter_burgers(
    ingredient: str | None = None,
    max_price: float | None = None,
    max_calories: int | None = None
) -> List[Dict[str, Any]]:
    """Filter burgers based on criteria."""
    logger.info(f"Filtering burgers - ingredient: {ingredient}, max_price: {max_price}, max_calories: {max_calories}")

    filtered = BURGERS.copy()

    if ingredient:
        ingredient_lower = ingredient.lower()
        filtered = [
            b for b in filtered
            if any(ingredient_lower in ing.lower() for ing in b["ingredients"])
        ]
        logger.info(f"After ingredient filter: {len(filtered)} burgers")

    if max_price is not None:
        filtered = [b for b in filtered if b["price"] <= max_price]
        logger.info(f"After price filter: {len(filtered)} burgers")

    if max_calories is not None:
        filtered = [b for b in filtered if b["calories"] <= max_calories]
        logger.info(f"After calories filter: {len(filtered)} burgers")

    logger.info(f"Final filtered result: {len(filtered)} burgers")
    return filtered
