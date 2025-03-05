



docker-compose up db


export WEB_USERNAME="admin"
export WEB_PASSWORD="supersecret"
export SQLALCHEMY_DATABASE_URL="postgresql://youruser:yourpassword@localhost/expenses"
uvicorn main:app --reload

=> http://localhost:8000/index.html



psql -U youruser -d expenses -W


# restart 

git pull origin main
docker compose build
docker compose restart


Update database

docker exec -it <container> bash

lpm add postgresql --global
liquibase update


# micro backup

pg_dump -U youruser -t expenses -a -f backup.sql expenses

psql -U youruser -d expenses -f backup.sql