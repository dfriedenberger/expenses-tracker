from collections import defaultdict
from typing import List
from .models import Expense


def cluster_expenses_by_category(expenses: List[Expense], categories: List[str]) -> List[List[Expense]]:
    category_cluster = defaultdict(list)

    for expense in expenses:
        for tag in expense.tags:
            if tag in categories:  # Direkter Check gegen die übergebene Liste
                category_cluster[tag].append(expense)
    return [category_cluster.get(category, []) for category in categories]


def sum_expenses(expenses: List[Expense]) -> float:
    sums = 0.0
    for expense in expenses:
        sums += expense.price

    return sums
