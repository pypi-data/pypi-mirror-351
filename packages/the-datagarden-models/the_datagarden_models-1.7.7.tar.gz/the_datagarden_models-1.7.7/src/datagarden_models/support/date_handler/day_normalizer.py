from datetime import date, datetime

from .helper import PeriodTransformer


class DayPeriodTransformer(PeriodTransformer):
    PERIOD_TYPE: str = "Day"

    def _date_to_period_type_datetime(self, dt: datetime) -> datetime:
        """Returns the first day of the week for a given datetime object."""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def _str_to_date(self, period: str) -> datetime:
        # try to extract year and month and day from a date string (ie 2024-01-01)
        datetime_from_date_str = self._try_date_str_to_datetime(period)
        if datetime_from_date_str:
            return datetime_from_date_str

        raise ValueError(f"Could not create {self.PERIOD_TYPE} date from {period}")

    def _try_date_str_to_datetime(self, period: str) -> datetime | None:
        """
        Tries to convert a date string to a datetime object.
        Accepts the following formats:
        - YYYY-MM-DD
        - DD-MM-YYYY
        If it fails to convert, returns None.
        """
        period = period.strip()
        try:
            return datetime.strptime(period, "%Y-%m-%d")
        except ValueError:
            pass

        try:
            return datetime.strptime(period, "%d-%m-%Y")
        except ValueError:
            pass

        return None

    def date_to_period_type_str(self, period: datetime | date | str) -> str:
        """
        Convert a datetime object to a string. This differs per period type.
        Day 2021-01-01 00:00:00 -> 2021-01-01
        """
        return self.period_start_str(period)
