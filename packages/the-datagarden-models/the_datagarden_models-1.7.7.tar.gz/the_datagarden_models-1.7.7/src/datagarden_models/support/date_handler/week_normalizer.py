from datetime import date, datetime, timedelta

from .helper import PeriodTransformer


class WeekPeriodTransformer(PeriodTransformer):
    PERIOD_TYPE: str = "Week"

    def _date_to_period_type_datetime(self, dt: datetime) -> datetime:
        """Returns the first day of the week for a given datetime object."""
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return dt - timedelta(days=dt.weekday())

    def _str_to_date(self, period: str) -> datetime:
        # try to extract year and month and day from a date string (ie 2024-01-01)
        datetime_from_date_str = self._try_date_str_to_datetime(period)
        if datetime_from_date_str:
            return datetime_from_date_str

        # try to extract year and quarter from a quarter string (ie 2024Q3)
        week_str = self._format_week_str(period)
        if week_str:
            year, week_nr = week_str.split("-")
            # Get the starting month for the quarter
            try:
                return datetime.fromisocalendar(int(year), int(week_nr), 1)
            except ValueError:
                pass

        raise ValueError(f"Could not create {self.PERIOD_TYPE} date from {period}")

    def _format_week_str(self, period: str) -> str:
        """
        Acceptable formats:
        - 1-2024
        - 01-2024
        - W1-2024
        - W01-2024
        - 2024-1
        - 2024-01
        - 2024-W1
        - 2024-W01
        - 2024W2
        - 2024W02
        (all formats are case insensitive)

        returns str in format YYYY-WW
        """
        week, year = None, None
        period = period.strip().upper()

        if period[0] == "W":
            period = period[1:]
        period = period.replace("W", "-").replace("--", "-")

        if period[1] == "-":
            year = period[2:]
            week = "0" + period[0]
        elif period[2] == "-":
            year = period[3:]
            week = period[0:2]
        elif period[4] == "-":
            year = period[0:4]
            week = period[5:]
            if len(week) == 1:
                week = "0" + week
        else:
            raise ValueError(f"Could not create {self.PERIOD_TYPE} date from {period}")

        if not year or not week:
            raise ValueError(f"Could not create {self.PERIOD_TYPE} date from {period}")

        return f"{year}-{week}"

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
        Week 2021-01-01 00:00:00 -> 2021W01
        """
        week = self.period_start_datetime(period)
        week_nr = week.isocalendar().week
        return f"{week.year}W{week_nr:02d}"
