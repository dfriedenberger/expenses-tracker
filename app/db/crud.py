from datetime import date
from sqlalchemy.orm import Session
from . import models, schemas


def create_expense(db: Session, expense: schemas.ExpenseCreate):
    print("create_expense", expense.dict())

    db_expense = models.Expense(**expense.dict())
    print("db_expense", db_expense)

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expenses(db: Session, from_date: date = None, to_date: date = None):
    query = db.query(models.Expense)

    # Falls "von"- oder "bis"-Datum angegeben wurde, Filter anwenden
    if from_date:
        query = query.filter(models.Expense.date >= from_date)
    if to_date:
        query = query.filter(models.Expense.date <= to_date)

    return query.all()


def get_expense(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()


def update_expense(db: Session, expense_id: int, expense: schemas.ExpenseUpdate):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if db_expense is None:
        return None
    for key, value in expense.dict().items():
        setattr(db_expense, key, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if db_expense:
        db.delete(db_expense)
        db.commit()
        return db_expense
    return None
