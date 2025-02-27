



docker-compose up db


export WEB_USERNAME="admin"
export WEB_PASSWORD="supersecret"
export SQLALCHEMY_DATABASE_URL="postgresql://youruser:yourpassword@localhost/expenses"
uvicorn main:app --reload

=> http://localhost:8000/index.html



psql -U youruser -d expenses -W
