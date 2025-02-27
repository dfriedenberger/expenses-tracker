



docker-compose up db


export WEB_USERNAME="admin"
export WEB_PASSWORD="supersecret"
uvicorn main:app --reload

=> http://localhost:8000/index.html



psql -U youruser -d expenses -W
