from datetime import date, timedelta
from typing import Optional

from timecraftx.day import Day
from timecraftx.utils import normalize_week_inputs


def start_of_week(
    from_date: Optional[date] = None, week_start: Day = Day.MONDAY
) -> date:
    """
    Returns the date corresponding to the first day of the week for the given date.

    Args:
        from_date: The reference date. Defaults to today if None.
        week_start: The starting day of the week (MONDAY or SUNDAY).

    Returns:
        A date object representing the start of the week.

    Raises:
        ValueError: If week_start is not an instance of Day.
        ValueError: If week_start is not Day.MONDAY or Day.SUNDAY.
    """
    from_date, weekday = normalize_week_inputs(from_date, week_start)
    return from_date - timedelta(days=weekday)


def end_of_week(from_date: Optional[date] = None, week_start: Day = Day.MONDAY) -> date:
    """
    Returns the date corresponding to the last day of the week for the given date.

    Args:
        from_date: The reference date. Defaults to today if None.
        week_start: The starting day of the week (MONDAY or SUNDAY).

    Returns:
        A date object representing the end of the week.

    Raises:
        ValueError: If week_start is not an instance of Day.
        ValueError: If week_start is not Day.MONDAY or Day.SUNDAY.
    """
    from_date, weekday = normalize_week_inputs(from_date, week_start)
    return from_date + timedelta(days=(6 - weekday))


def _add_days_to_date(from_date: Optional[date] = None, days: int = 1) -> date:
    """
    Adds a given number of days to a date, defaulting to today if no date is provided.

    Args:
        from_date: The date to start from. Defaults to today if None.
        days: Number of days to add. Use a negative value to subtract.

    Returns:
        A date object offset by the specified number of days.
    """
    if from_date is None:
        from_date = date.today()

    return from_date + timedelta(days=days)


def tomorrow(from_date: Optional[date] = None) -> date:
    """
    Returns the date for tomorrow relative to a given date.

    Args:
        from_date: The reference date. Defaults to today if None.

    Returns:
        The date for tomorrow.
    """
    return _add_days_to_date(from_date=from_date, days=1)


def yesterday(from_date: Optional[date] = None) -> date:
    """
    Returns the date for yesterday relative to a given date.

    Args:
        from_date: The reference date. Defaults to today if None.

    Returns:
        The date for yesterday.
    """
    return _add_days_to_date(from_date=from_date, days=-1)
