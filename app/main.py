from typing import List
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

from db import models, schemas
from db import crud
from db.database import engine, SessionLocal

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/expenses/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db=db, expense=expense)


@app.get("/tags/", response_model=List[schemas.Tag])
def read_tags():
    return [
        {"id": "urlaub", "name": "Urlaub"},
        {"id": "tanken", "name": "Tanken"},
        {"id": "lebensmittel", "name": "Lebensmittel"},
        {"id": "sport", "name": "Sport"},
        {"id": "versicherung", "name": "Versicherung"},
        {"id": "auto", "name": "Auto"}
    ]


@app.get("/currency/", response_model=List[schemas.Currency])
def read_currency():
    return [
        {"shortcut": "Kč", "name": "Tschechische Krone", "factor": 0.04}
    ]


@app.get("/expenses/", response_model=List[schemas.Expense])
def read_expenses(db: Session = Depends(get_db)):
    return crud.get_expenses(db)


@app.get("/expenses/{expense_id}", response_model=schemas.Expense)
def read_expense(expense_id: int, db: Session = Depends(get_db)):
    return crud.get_expense(db, expense_id=expense_id)


@app.put("/expenses/{expense_id}", response_model=schemas.Expense)
def update_expense(expense_id: int, expense: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    return crud.update_expense(db=db, expense_id=expense_id, expense=expense)


@app.delete("/expenses/{expense_id}", response_model=schemas.Expense)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    return crud.delete_expense(db=db, expense_id=expense_id)


app.mount("/", StaticFiles(directory="static"), name="static")
