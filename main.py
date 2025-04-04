from db.db import create_connection
from schema.schema import UserCreate
from pydantic import ValidationError

conn = create_connection()

if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT 1+1")
    results = cursor.fetchall()
    print(results)

    cursor.close()
    conn.close()

user_data = {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "Password123",
    "first_name": "John",
    "last_name": "Doe",
}

try:
    user = UserCreate(**user_data)
    print(user)
except ValidationError as e:
    print(e.json())
