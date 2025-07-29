"""
Module for handling period and period types. Main task is to normalize string and date representations
of periods in compliance with the period type.

For example for period type "week" the following strings are valid:
- 2024-W01
- 2024W01
- 2024-W1
- 2024W1
- 2024-01-01
- 2024-01-01

and all converted to either "2024W01" or "2024-01-01" or datetime(2024, 1, 1, 0, 0, 0).

as jan 1 is the monday of the first week of 2024.

Simmilar conversion are done for other period types.
"2024" or "2024-01-01" for year
"2024Q3" or "2024-07-01" for quarter
"2024M03" or "2024-03-01" for month
"2024-01-01" for day

the datetime format always returns the first day of the givenperiod.
"""

from .day_normalizer import DayPeriodTransformer
from .month_normalizer import MonthPeriodTransformer
from .period_type_normalizer import PeriodTypeNormalizer
from .quarter_normalizer import QuarterPeriodTransformer
from .week_normalizer import WeekPeriodTransformer
from .year_normalizer import YearPeriodTransformer

PERIOD_TYPES = {
    "year": "year",
    "quarter": "quarter",
    "month": "month",
    "week": "week",
    "day": "day",
    "y": "year",
    "q": "quarter",
    "m": "month",
    "w": "week",
    "d": "day",
}


class GetPeriodTypeTransformer:
    """
    Get the period transformer for a given period type.

    Period types are:
        - year
        - quarter
        - month
        - week
        - day
    and can be abbreviated to:
        - y, q, m, w, d

    period types are case insensitive.

    Methods:
        - get_transformer(period_type: str) -> PeriodTransformer
        returns the transformer for the given period type.
    """

    @staticmethod
    def get_transformer(period_type):
        period_type = PERIOD_TYPES.get(period_type.lower())
        match period_type:
            case "year":
                return YearPeriodTransformer()
            case "quarter":
                return QuarterPeriodTransformer()
            case "month":
                return MonthPeriodTransformer()
            case "week":
                return WeekPeriodTransformer()
            case "day":
                return DayPeriodTransformer()
            case _:
                raise ValueError(f"Unsupported period type: {period_type}")


__all__ = ["GetPeriodTypeTransformer", "PeriodTypeNormalizer"]
