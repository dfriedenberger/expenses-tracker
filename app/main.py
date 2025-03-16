from typing import List
from datetime import datetime

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.orm import Session

from expenses.util import get_env_variable, get_week_range, get_month_range, get_year_range
from expenses.util import get_iso_weeks_in_year, get_week_day, get_month, get_next_month, get_last_month
from lib import schemas
from lib import crud
from expenses.database import SessionLocal
from expenses.expense_stats import sum_expenses, cluster_expenses_by_category
from expenses.statistics import calculate_prognosis
from lib import __version__, __date__

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


@app.get("/util/version/")
def get_version():
    return {"version": __version__, "date": __date__}


@app.get("/util/kw/")
def get_kw_year():
    year, week, _ = datetime.today().isocalendar()
    return {"year": year, "week": week}


@app.get("/util/month/")
def get_month_year():
    today = datetime.today()
    return {"month": today.month, "year": today.year}


@app.get("/statistic/week/")
def read_statistic_week(
    year: int = Query(..., description="Jahr der Statistik"),  # ... bedeutet Pflichtparameter
    week: int = Query(..., description="Kalenderwoche der Statistik"),  # ... bedeutet Pflichtparameter
    db: Session = Depends(get_db)
):

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


@app.get("/statistic/month/")
def read_statistic_month(
    year: int = Query(..., description="Jahr der Statistik"),  
    month: int = Query(..., description="Monat der Statistik"), 
    db: Session = Depends(get_db)
):

    next_month_year, next_month = get_next_month(year, month)
    last_month_year, last_month = get_last_month(year, month)

    today = datetime.today().date()
    from_date, to_date = get_month_range(year, month)

    # Get list for ids and names of categories
    categories = crud.get_tags(db, tag_type="category")
    cat_ids = [tag.id for tag in categories]
    cat_names = [tag.name for tag in categories]

    # Get all expenses for the month
    expenses_for_month = crud.get_expenses(db, from_date, to_date)

    # Cluster expenses by category
    expenses_cluster = cluster_expenses_by_category(expenses_for_month, cat_ids)

    data = [sum_expenses(e) for e in expenses_cluster]

    _category_limits = {
        "lebensmittel": 800,
        "tanken": 200,
        "sonstiges": 400
    }

    monthly_limit = sum(_category_limits.values())

    sum_of_expenses = sum(data)
    prognosed_expenses = calculate_prognosis(from_date, to_date, today, monthly_limit)
    savings = 3000 - sum_of_expenses - prognosed_expenses
    if savings < 0:
        savings = 0  # No negative savings

    return {
        "title": f'Auswertung {get_month(month)} {year}',
        "month": month,
        "year": year,
        "last_month": last_month,
        "last_month_year": last_month_year,
        "next_month": next_month,
        "next_month_year": next_month_year,

        # accumulate expenses
        "dataset_label": "Ausgaben (€)",
        "limit": 3000,
        "prognose": round(prognosed_expenses, 2),
        "sum": round(sum_of_expenses, 2),
        "savings": round(savings, 2),

        "limits":  [_category_limits.get(category, 0.0) for category in cat_ids],
        "labels": cat_names,
        "data": data,
        "expenses": expenses_cluster,
    }


@app.get("/statistic/vacation/")
def read_statistic_vacation(
    year: int = Query(..., description="Jahr der Statistik"),
    db: Session = Depends(get_db)
):

    from_date, to_date = get_year_range(year)

    # Get list for ids and names of categories
    categories = crud.get_tags(db, tag_type="vacation")
    cat_ids = [tag.id for tag in categories]
    cat_names = [tag.name for tag in categories]

    # Get all expenses for the month
    expenses_for_year = crud.get_expenses(db, from_date, to_date, tag="urlaub")

    # Cluster expenses by category
    expenses_cluster = cluster_expenses_by_category(expenses_for_year, cat_ids)

    data = [sum_expenses(e) for e in expenses_cluster]
    return {
        "title": f'Urlaubsauswertung {year}',
        "year": year,
        "next_year": year + 1,
        "last_year": year - 1,
        "labels": cat_names,
        "data": data,
        "expenses": expenses_cluster,
    }


# Tag
@app.get("/tags/", response_model=List[schemas.Tag])
def read_tags(db: Session = Depends(get_db)):
    return crud.get_tags(db, sort_order=["category", "tag", "person", "location", "vacation"])


@app.post("/tags/", response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    return crud.create_tag(db=db, tag=tag)


# Currency
@app.get("/currencies/", response_model=List[schemas.Currency])
def read_currencies(db: Session = Depends(get_db)):
    return crud.get_currencies(db)


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
