from typing import List
from datetime import datetime

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session

from db.util import get_env_variable, get_week_range, get_iso_weeks_in_year, get_week_day
from db import schemas
from db import crud
from db.database import SessionLocal
from db.expense_stats import sum_expenses, cluster_expenses_by_category

# Create database tables, is controled by liqui base
# models.Base.metadata.create_all(bind=engine)

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




@app.get("/currency/", response_model=List[schemas.Currency])
def read_currency():
    return [
        {"iso4217": "DKK", "name": "Dänische Krone", "symbol": "kr", "factor": 0.13},
        {"iso4217": "CHF", "name": "Schweizer Franken", "symbol": "CHF", "factor": 1.04},
        {"iso4217": "NOK", "name": "Norwegische Krone", "symbol": "kr", "factor": 0.087},
        {"iso4217": "SEK", "name": "Schwedische Krone", "symbol": "kr", "factor": 0.089},
        {"iso4217": "GBP", "name": "Britisches Pfund", "symbol": "£", "factor": 1.17},
        {"iso4217": "PLN", "name": "Polnischer Złoty", "symbol": "zł", "factor": 0.23},
        {"iso4217": "CZK", "name": "Tschechische Krone", "symbol": "Kč", "factor": 0.04},
        {"iso4217": "BGN", "name": "Bulgarischer Lew", "symbol": "лв", "factor": 0.51},
        {"iso4217": "ISK", "name": "Isländische Krone", "symbol": "kr", "factor": 0.0066},
        {"iso4217": "HUF", "name": "Ungarischer Forint", "symbol": "Ft", "factor": 0.0026},
        {"iso4217": "RON", "name": "Rumänischer Leu", "symbol": "lei", "factor": 0.20},
        {"iso4217": "RSD", "name": "Serbischer Dinar", "symbol": "дин", "factor": 0.0085},
        {"iso4217": "UAH", "name": "Ukrainische Hrywnja", "symbol": "₴", "factor": 0.025},
        {"iso4217": "MDL", "name": "Moldauischer Leu", "symbol": "L", "factor": 0.052},
        {"iso4217": "GEL", "name": "Georgischer Lari", "symbol": "₾", "factor": 0.35},
        {"iso4217": "ALL", "name": "Albanischer Lek", "symbol": "Lek", "factor": 0.0094},
        {"iso4217": "MKD", "name": "Mazedonischer Denar", "symbol": "ден", "factor": 0.016},
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

    categories = crud.get_tags(db, tag_type="category")
    cat_ids = [tag.id for tag in categories]
    cat_names = [tag.name for tag in categories]

    expenses_cluster = cluster_expenses_by_category(expenses_for_kw, cat_ids)

    data = [sum_expenses(e) for e in expenses_cluster]

    _category_limits = {
        "lebensmittel": 200,
        "tanken": 50,
        "sonstiges": 100
    }

    return {
        "title": f'Auswertung der KW {week}/{year}',
        "subtitle": f'{get_week_day(from_date)}, {from_date.strftime("%d.%m.%Y")} - {get_week_day(to_date)}, {to_date.strftime("%d.%m.%Y")}',
        "week": week,
        "year": year,
        "last_week": last_week,
        "last_week_year": last_week_year,
        "next_week": next_week,
        "next_week_year": next_week_year,
        "dataset_label": "Ausgaben (€)",
        "suggestedMax": 400,
        "labels": cat_names,
        "data": data,
        "limits": [_category_limits.get(category, 0.0) for category in cat_ids],
        "expenses": expenses_cluster,
    }


# Tag
@app.get("/tags/", response_model=List[schemas.Tag])
def read_tags(db: Session = Depends(get_db)):
    tags = crud.get_tags(db)
    print(tags)
    return tags


# Expenses
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


app.mount("/", StaticFiles(directory="static",html = True), name="static")
