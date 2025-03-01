from collections import defaultdict
from typing import List
from .models import Expense


def sum_expenses_by_category(expenses: List[Expense], categories: List[str]) -> List[float]:
    category_sums = defaultdict(float)  # Standardwert 0.0 für neue Kategorien

    for expense in expenses:
        for tag in expense.tags:
            if tag in categories:  # Direkter Check gegen die übergebene Liste
                category_sums[tag] += expense.price

    # Create the list with totals in the same order as the categories
    return [category_sums.get(category, 0.0) for category in categories]
