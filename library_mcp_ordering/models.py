"""
Data models for burger filtering and widget configuration
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BurgerWidget:
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str


class BurgerFilterInput(BaseModel):
    """Schema for burger filtering."""

    ingredient: str | None = Field(
        None,
        description="Filter by ingredient (e.g., 'beef', 'chicken', 'veggie')",
    )
    max_price: float | None = Field(
        None,
        alias="maxPrice",
        description="Maximum price in dollars",
    )
    max_calories: int | None = Field(
        None,
        alias="maxCalories",
        description="Maximum calories",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "ingredient": {
            "type": "string",
            "description": "Filter by ingredient (e.g., 'beef', 'chicken', 'veggie')",
        },
        "maxPrice": {
            "type": "number",
            "description": "Maximum price in dollars",
        },
        "maxCalories": {
            "type": "integer",
            "description": "Maximum calories",
        },
    },
    "additionalProperties": False,
}

logger.info("Models and schemas loaded")
