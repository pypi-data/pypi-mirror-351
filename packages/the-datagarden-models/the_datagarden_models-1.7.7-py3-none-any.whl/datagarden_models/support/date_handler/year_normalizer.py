from datetime import date, datetime

from .helper import PeriodTransformer


class YearPeriodTransformer(PeriodTransformer):
    PERIOD_TYPE: str = "Year"

    def _date_to_period_type_datetime(self, dt: datetime) -> datetime:
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    def _str_to_date(self, year_str: str) -> datetime | None:
        """
        Extract the first occurrence of 4 consecutive digits from a string.
        Returns None if no 4 consecutive digits are found.

        Examples:
            "2024-01-01" -> "2024"
            "2024" -> "2024"
            "1-1-2024" -> "2024"
        """
        if not isinstance(year_str, str):
            return None

        year = ""
        for char in year_str:
            if char.isdigit():
                year += char
                if len(year) == 4:
                    return datetime(int(year), 1, 1)
            else:
                year = ""

        return None

    def date_to_period_type_str(self, period: datetime | date | str) -> str:
        """
        Convert a datetime object to a string. This differs per period type.
        Year 2021-01-01 00:00:00 -> 2021
        """
        return self.period_start_datetime(period).strftime("%Y")
