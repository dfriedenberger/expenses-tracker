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
        orm_mode = True


class TagBase(BaseModel):
    tag_type: str
    id: str
    name: str


class Tag(TagBase):

    class Config:
        from_attributes = True
        orm_mode = True


class Currency(BaseModel):
    iso4217: str
    symbol: str
    name: str
    factor: float
