import os
from datetime import datetime, timedelta, date


# Retrieving an environment variable with error handling
def get_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise RuntimeError(f"Fehlende Umgebungsvariable: {var_name}")
    return value


def get_monday_of_week(year: int, week: int):
    # 4. Januar ist immer in der ersten ISO-Kalenderwoche
    fourth_jan = datetime(year, 1, 4)

    # Bestimmen des Montags der ersten Kalenderwoche
    first_monday = fourth_jan - timedelta(days=fourth_jan.weekday())

    # Montag der gewünschten Kalenderwoche berechnen
    monday = first_monday + timedelta(weeks=week - 1)

    return monday.date()


def get_week_range(year: int, week: int):

    # Erster Montag des Jahres finden (ISO-Woche beginnt am Montag)
    start_date = get_monday_of_week(year, week)

    end_date = start_date + timedelta(days=6)  # Sonntag ist 6 Tage nach Montag

    return start_date, end_date


def get_iso_weeks_in_year(year: int) -> int:
    """Returns the number of ISO calendar weeks in a given year."""
    last_week = date(year, 12, 28).isocalendar()[1]  # KW von 28. Dez. bestimmen
    return last_week
