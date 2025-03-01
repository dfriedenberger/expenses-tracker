from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class ExpenseBase(BaseModel):
    title: str
    price: float
    currency: Optional[str] = None
    price_currency: Optional[float] = None
    date: date
    tags: List[str]


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int

    class Config:
        from_attributes = True


class Tag(BaseModel):
    tag_typ: str
    id: str
    name: str


class Currency(BaseModel):
    shortcut: str
    name: str
    factor: float
