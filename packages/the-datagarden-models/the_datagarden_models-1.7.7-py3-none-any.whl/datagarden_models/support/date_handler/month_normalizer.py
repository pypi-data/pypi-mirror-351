from datetime import date, datetime

from .helper import PeriodTransformer


class MonthPeriodTransformer(PeriodTransformer):
    PERIOD_TYPE: str = "Month"

    def _date_to_period_type_datetime(self, dt: datetime) -> datetime:
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _str_to_date(self, month_str: str) -> datetime | None:
        """
        Extract the first occurrence of 4 consecutive digits from a string.
        Returns None if no 4 consecutive digits are found.

        Examples:
            "2024-03" -> datetime(2024, 3, 1)
            "2024-04-01" -> datetime(2024, 4, 1)
            "01-01-2024" -> datetime(2024, 1, 1)
        """
        if not isinstance(month_str, str):
            return None
        try:
            return datetime.strptime(month_str, "%Y-%m")
        except ValueError:
            pass
        try:
            return datetime.strptime(month_str, "%Y-%m-%d")
        except ValueError:
            pass
        try:
            return datetime.strptime(month_str, "%d-%m-%Y")
        except ValueError:
            pass

        return None

    def date_to_period_type_str(self, period: datetime | date | str) -> str:
        """
        Convert a datetime object to a string. This differs per period type.
        Month 2021-01-01 00:00:00 -> 2021M01
        """
        return self.period_start_datetime(period).strftime("%YM%m")
