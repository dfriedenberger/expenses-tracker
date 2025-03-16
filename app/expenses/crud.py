from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB

from . import models, schemas


def get_tags(db: Session, tag_type: str = None, sort_order: list = None):
    query = db.query(models.Tag)

    # Filter
    if tag_type:
        query = query.filter(models.Tag.tag_type == tag_type)

    # Sortierung
    if sort_order:
        order_case = case(
                *[(models.Tag.tag_type == value, index) for index, value in enumerate(sort_order)],
                else_=len(sort_order)  # Falls der Wert nicht in der Liste ist, ans Ende setzen
        )
        query = query.order_by(order_case)

    return query.all()


def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def get_currencies(db: Session):
    return db.query(models.Currency).all()


def create_expense(db: Session, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expenses(db: Session, from_date: date = None, to_date: date = None, tag: str = None):
    query = db.query(models.Expense)

    # Falls "von"- oder "bis"-Datum angegeben wurde, Filter anwenden
    if from_date:
        query = query.filter(models.Expense.date >= from_date)
    if to_date:
        query = query.filter(models.Expense.date <= to_date)

    if tag:  # Filtern nach Tag
        query = query.filter(cast(models.Expense.tags, JSONB).op('@>')(f'["{tag}"]'))

    # Nach dem "date"-Feld absteigend sortieren (neueste zuerst)
    query = query.order_by(models.Expense.date.desc())

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
