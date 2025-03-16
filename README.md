# Project Setup Guide

## Introduction
**Expenses Tracker** is a lightweight and efficient expense management application built with **FastAPI** and **PostgreSQL**. It allows users to record, categorize, and analyze their expenses with ease. The project provides a RESTful API that integrates seamlessly with frontend applications or can be used as a standalone backend service.

### Key Features
- **FastAPI Backend** – High-performance API with automatic documentation.
- **PostgreSQL Database** – Reliable and scalable data storage.
- **Expense Tracking** – Create, update, and delete expenses.
- **Reporting** – Retrieve expense data with flexible filtering options.
- **Docker Support** – Easily deploy and run with Docker & Docker Compose.

### Getting Started
Follow the setup instructions below to install and configure the application locally or in a production environment. 🚀

---

## Installation & Configuration

### Prerequisites
Ensure you have the following installed on your system:
- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Python 3.9+](https://www.python.org/downloads/) (only for local development)


### Configure .env and liquibase.properties
Use .env.template and liquibase.properties.template and modify your environment

### Create Database 
```sh
docker-compose up db liquibase
```

```sh
docker exec -it <container> bash
lpm add postgresql --global
liquibase update
```


## Running the Application
```sh
docker-compose up -d
```

## Running the Application for development purposes
Start the PostgreSQL database container using Docker Compose:
```sh
docker-compose up -d db
```

Set environment for application
```sh
export WEB_USERNAME="admin"
export WEB_PASSWORD="supersecret"
export SQLALCHEMY_DATABASE_URL="postgresql://youruser:yourpassword@localhost/expenses"
```

Alternatively, environment variables can be loaded from a `.env` file. Refer to this [Stack Overflow discussion](https://stackoverflow.com/questions/43267413/how-to-set-environment-variables-from-env-file) for more details.


Start the application in development mode:
```sh
cd app/
uvicorn main:app --reload
```
Access the application at: [http://localhost:8000](http://localhost:8000)

---

## Updating & Restarting
To pull the latest changes and restart the service:
```sh
git pull origin main
docker compose build
docker compose restart
```

---

## Database Updates
To apply database migrations using Liquibase:
```sh
docker exec -it <container> bash
liquibase <command>
```

---

## Backup & Restore
### Create a Micro Backup
```sh
pg_dump -U <youruser> -t expenses -a -f backup.sql expenses
```

### Restore from Backup
```sh
psql -U <youruser> -d expenses -f backup.sql
```

---

## Versioning
To update the project version:
```sh
python set_version.py (--major | --minor | --patch)
```



