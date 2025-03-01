from typing import List
from datetime import datetime
import locale

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session

from db.util import get_env_variable, get_week_range, get_iso_weeks_in_year
from db import models, schemas
from db import crud
from db.database import engine, SessionLocal
from db.expense_stats import sum_expenses_by_category
from db.tags import TAG_LIST, tags_get_categories, tags_get_limits

# Deutsche Sprache für Datumsformat setzen (falls vom System unterstützt)
locale.setlocale(locale.LC_TIME, "de_DE.utf8")

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Basic Authentication
security = HTTPBasic()


VALID_USERNAME = get_env_variable("WEB_USERNAME")
VALID_PASSWORD = get_env_variable("WEB_PASSWORD")


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != VALID_USERNAME or credentials.password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


app = FastAPI(dependencies=[Depends(verify_credentials)])

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


@app.get("/tags/", response_model=List[schemas.Tag])
def read_tags():
    return TAG_LIST


@app.get("/currency/", response_model=List[schemas.Currency])
def read_currency():
    return [
        {"shortcut": "Kč", "name": "Tschechische Krone", "factor": 0.04}
    ]


@app.get("/util/kw/")
def get_kw():
    year, week, _ = datetime.today().isocalendar()
    return {"year": year, "week": week}


@app.get("/statistic/")
def read_statistic(
    year: int = Query(..., description="Jahr der Statistik"),  # ... bedeutet Pflichtparameter
    week: int = Query(..., description="Kalenderwoche der Statistik"),  # ... bedeutet Pflichtparameter
    db: Session = Depends(get_db)
):
    if year is None or week is None:
        year, week, _ = datetime.today().isocalendar()

    next_week_year = year
    next_week = week + 1
    if next_week > get_iso_weeks_in_year(next_week_year):
        next_week_year = year + 1
        next_week = 1

    last_week_year = year
    last_week = week - 1
    if last_week < 1:
        last_week_year = year - 1
        last_week = get_iso_weeks_in_year(last_week_year)

    from_date, to_date = get_week_range(year, week)

    expenses_for_kw = crud.get_expenses(db, from_date, to_date)

    cat_ids, cat_names = tags_get_categories()

    return {
        "title": f'Auswertung der KW {week}/{year}',
        "subtitle": f'{from_date.strftime("%a, %d.%m.%Y")} - {to_date.strftime("%a, %d.%m.%Y")}',
        "week": week,
        "year": year,
        "last_week": last_week,
        "last_week_year": last_week_year,
        "next_week": next_week,
        "next_week_year": next_week_year,
        "dataset_label": "Ausgaben (€)",
        "suggestedMax": 400,
        "labels": cat_names,
        "data": sum_expenses_by_category(expenses_for_kw, cat_ids),
        "limits": tags_get_limits(cat_ids)
    }


@app.post("/expenses/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db=db, expense=expense)


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
