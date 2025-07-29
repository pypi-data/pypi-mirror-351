from datetime import date, datetime

from .helper import PeriodTransformer


class QuarterPeriodTransformer(PeriodTransformer):
    PERIOD_TYPE: str = "Quarter"

    def _date_to_period_type_datetime(self, dt: datetime) -> datetime:
        first_month_of_quarter = ((dt.month - 1) // 3) * 3 + 1
        return dt.replace(month=first_month_of_quarter, day=1, hour=0, minute=0, second=0, microsecond=0)

    def _str_to_date(self, period: str) -> datetime | None:
        # try to extract year and month from a date string (ie 2024-01-01)
        datetime_from_date_str = self._try_date_str_to_datetime(period)
        if datetime_from_date_str:
            year, month = datetime_from_date_str.year, datetime_from_date_str.month
            first_month_of_quarter_nr = 3 * ((month - 1) // 3) + 1
            return datetime(year, first_month_of_quarter_nr, 1, 0, 0, 0)

        # try to extract year and quarter from a quarter string (ie 2024Q3)
        quarter_str = self._format_quarter_str(period)
        if quarter_str:
            year_str, quarter_nr = quarter_str.split("-")
            # Get the starting month for the quarter
            month = int(quarter_nr) * 3 - 2
            return datetime(int(year_str), month, 1, 0, 0, 0)

        raise ValueError(f"Could not create {self.PERIOD_TYPE} date from {period}")

    def _format_quarter_str(self, period: str) -> str:
        """
        Acceptable formats:
        - 1-2024
        - Q1-2024
        - 2024-1
        - 2024-Q1
        - 2024Q2

        returns str in format YYYY-Q
        """

        period = period.strip()
        period = period.upper()
        if period[0] == "Q":
            period = period[1:]
        period = period.replace("Q", "-")
        period = period.replace("--", "-")
        if period[1] == "-":
            return period[2:] + "-" + period[0]
        if period[4] == "-":
            return period

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
        Quarter 2021-01-01 00:00:00 -> 2021Q1
        """
        quarter = self.period_start_datetime(period)
        quarter_nr = (quarter.month - 1) // 3 + 1
        return f"{quarter.year}Q{quarter_nr}"
