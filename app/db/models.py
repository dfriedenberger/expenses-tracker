from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float)
    currency = Column(String, default=None)
    price_currency = Column(Float, default=None)
    date = Column(DateTime)
    tags = Column(JSON)
