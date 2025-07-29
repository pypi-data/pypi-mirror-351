from abc import ABC, abstractmethod

# from core.helpers.datetime_methods import utc_datetime
from datetime import date, datetime
from datetime import timezone as dt_timezone


def utc_datetime(dt: date | datetime) -> datetime:
    """
    Convert a date, datetime, or date string to a UTC-aware datetime object.
    """
    # not isinstance(dt, datetime) is needed as datatime obejct are also instances of date
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime(dt.year, dt.month, dt.day)

    if not isinstance(dt, datetime):
        raise TypeError(f"Invalid date format: {dt}, dt needs to be of type datetime, date or str")

    # Ensure the datetime is timezone-aware and in UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_timezone.utc)
    else:
        dt = dt.astimezone(dt_timezone.utc)

    return dt


class PeriodTransformer(ABC):
    """
    Public methods:
        period_start_datetime: returns first day for period of a given period type in datetime format.
        period_start_str: returns first day for period of a given period type in string format.
        date_to_period_type_str: returns str representation of a period for a given period type.
        validate: returns True if period is valid for the period type, False otherwise.
    """

    PERIOD_TYPE: str

    def period_start_datetime(self, period: str | date | datetime) -> datetime:
        """Returns first day for period of a given period type in datetime format."""
        if isinstance(period, str):
            converted_period = self._str_to_date(period)
            if not converted_period:
                raise ValueError(f"Could not create {self.PERIOD_TYPE} date from {period}")
        else:
            converted_period = datetime(period.year, period.month, period.day)

        utc_converted_period = utc_datetime(dt=converted_period)
        return self._date_to_period_type_datetime(utc_converted_period)

    def period_start_str(self, period: str | date | datetime) -> str:
        return self._date_to_str(self.period_start_datetime(period))

    def validate(self, period) -> bool:
        try:
            self.period_start_datetime(period)
            return True
        except ValueError:
            return False

    @abstractmethod
    def _str_to_date(self, period: str) -> datetime | None:
        """
        Convert a string to a datetime object. This differs per period type.
        Quarter 2021Q3 -> 2021-07-01 00:00:00
        Month 2021-03 -> 2021-03-01 00:00:00
        Year 2021-10-10 -> 2021-01-01 00:00:00
        etc.
        """
        pass

    def _date_to_str(self, period: datetime) -> str:
        """
        Convert a datetime object to a regular string in format YYYY-MM-DD
        """
        return period.strftime("%Y-%m-%d")

    @abstractmethod
    def date_to_period_type_str(self, period: datetime | date | str) -> str:
        """
        Convert a datetime object to a string. This differs per period type.
        Quarter 2021-07-01 00:00:00 -> 2021Q3
        Month 2021-03-01 00:00:00 -> 2021-03
        Week 2021-01-09 00:00:00 -> 2021W02
        Year 2021-01-01 00:00:00 -> 2021
        etc.
        """
        pass

    @abstractmethod
    def _date_to_period_type_datetime(self, period: datetime) -> datetime:
        """
        Convert a datetime object to the period type datetime object.
        Year: 2024-01-01 00:00:00 -> 2024-01-01 00:00:00
        Quarter: 2024-02-01 00:00:00 -> 2024-01-01 00:00:00
        Month: 2024-01-02 00:00:00 -> 2024-01-01 00:00:00
        Week: 2024-01-09 00:00:00 -> 2024-01-08 00:00:00
        Day: 2024-10-10 00:00:00 -> 2024-10-10 00:00:00
        """
        pass
