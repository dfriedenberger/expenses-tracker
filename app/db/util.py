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


def get_month_range(year: int, month: int):
    # Erster Tag des Monats
    start_date = date(year, month, 1)

    # Letzter Tag des Monats
    if month == 12:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    return start_date, end_date


def get_iso_weeks_in_year(year: int) -> int:
    """Returns the number of ISO calendar weeks in a given year."""
    last_week = date(year, 12, 28).isocalendar()[1]  # KW von 28. Dez. bestimmen
    return last_week


def get_week_day(day: date):
    # Statisches Array für die deutschen Wochentags-Kürzel
    week_days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    # Den Index des Wochentages (0 = Montag, 6 = Sonntag)
    day_index = day.weekday()  # Montag=0, Sonntag=6

    # Rückgabe der Kurzform des Wochentages
    return week_days[day_index]


def get_month(month: int):
    # Statisches Array für die deutschen Monatsnamen
    months = [
        "Januar",
        "Februar",
        "März",
        "April",
        "Mai",
        "Juni",
        "Juli",
        "August",
        "September",
        "Oktober",
        "November",
        "Dezember"
    ]

    # Rückgabe des Monatsnamens
    return months[month - 1]


def get_next_month(year, month):
    next_month_year = year
    next_month = month + 1
    if next_month > 12:
        next_month_year = year + 1
        next_month = 1
    return next_month_year, next_month


def get_last_month(year, month):
    last_month_year = year
    last_month = month - 1
    if last_month < 1:
        last_month_year = year - 1
        last_month = 12
    return last_month_year, last_month
