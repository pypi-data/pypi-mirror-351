"""
Module for normalizing period type strings into standardized formats.

This module provides functionality to convert various string representations
of period types into a standardized format. It handles different common
variations of period type names and abbreviations.

Supported period types and their aliases:
- year: "year", "y", "yearly"
- quarter: "quarter", "q", "quarterly"
- month: "month", "m", "monthly"
- week: "week", "w", "weekly"
- day: "day", "d", "daily"

All inputs are normalized to the standard format: "year", "quarter", "month", "week", or "day".
"""

from typing import Literal

PeriodType = Literal["year", "quarter", "month", "week", "day"]


class PeriodTypeNormalizer:
    @classmethod
    def normalize(self, period_type: str) -> PeriodType:
        lower_period_type = period_type.lower()
        match lower_period_type:
            case "year" | "y" | "yearly":
                return "year"
            case "quarter" | "q" | "quarterly":
                return "quarter"
            case "month" | "m" | "monthly":
                return "month"
            case "week" | "w" | "weekly":
                return "week"
            case "day" | "d" | "daily":
                return "day"
            case _:
                raise ValueError(f"Invalid period type: {period_type}")
