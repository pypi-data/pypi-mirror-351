from datetime import date
from typing import Optional, Tuple

from timecraftx.day import Day

VALID_WEEK_STARTS = {Day.MONDAY, Day.SUNDAY}


def normalize_week_inputs(
    from_date: Optional[date] = None, week_start: Day = Day.MONDAY
) -> Tuple[date, int]:
    """
    Normalizes and validates the input date and week_start.

    Ensures the week_start is a supported Day enum (MONDAY or SUNDAY), defaults
    from_date to today if None, and returns both the date and the adjusted weekday index.

    For week_start = SUNDAY, adjusts the weekday so Sunday becomes 0 and Saturday 6.

    Args:
        from_date: The reference date. If None, uses today's date.
        week_start: The starting day of the week (MONDAY or SUNDAY).

    Returns:
        A tuple of (normalized date, adjusted weekday index).

    Raises:
        ValueError: If week_start is not an instance of Day.
        ValueError: If week_start is not Day.MONDAY or Day.SUNDAY.
    """
    if not isinstance(week_start, Day):
        raise ValueError("week_start must be an instance of Day enum")

    if week_start not in VALID_WEEK_STARTS:
        raise ValueError("week_start must be Day.MONDAY or Day.SUNDAY")

    if from_date is None:
        from_date = date.today()

    weekday = from_date.weekday()
    if week_start == Day.SUNDAY:
        weekday = (weekday + 1) % 7

    return from_date, weekday
