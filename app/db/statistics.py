

def calculate_prognosis(from_date, to_date, today, monthly_limit):

    # Historical months
    prognosis = 0

    # Current month
    if from_date <= today <= to_date:
        # Calculate average expenses per day
        days_in_month = (to_date - from_date).days + 1
        expenses_per_day = monthly_limit / days_in_month

        # Calculate remaining days
        remaining_days = (to_date - today).days + 1

        # Calculate prognosed expenses
        prognosis = expenses_per_day * remaining_days

    # Future months
    if today < from_date:
        prognosis = monthly_limit

    return prognosis
