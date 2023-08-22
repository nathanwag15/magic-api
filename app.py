import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request


CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT, email TEXT, password TEXT);"
)

CREATE_DECKS_TABLE = """CREATE TABLE IF NOT EXISTS decks (user_id INTEGER, deck_name TEXT, image_url TEXT, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);"""

INSERT_USER_RETURN_ID = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id;"

INSERT_DECK = (
    "INSERT INTO decks (user_id, deck_name, image_url) VALUES (%s, %s, %s);"
    )

GLOBAL_NUMBER_OF_DAYS = (
    """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"""
)

GLOBAL_AVG = """SELECT AVG(temperature) as average FROM temperatures;"""

load_dotenv()


app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.post("/api/user")
def create_room():
    data = request.get_json()
    name = data["name"]
    email = data["email"]
    password = data["password"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(INSERT_USER_RETURN_ID, (name, email, password))
            room_id = cursor.fetchone()[0]
    return {"id": room_id, "message": f"User {name} created."}, 201
     
@app.post("/api/deck")
def add_temp():
    data = request.get_json()
    deck_name = data["deck_name"]
    user_id = data["user_id"]
    image_url = data["image_url"]
    
    with connection: 
        with connection.cursor() as cursor:
            cursor.execute(CREATE_DECKS_TABLE)
            cursor.execute(INSERT_DECK, (user_id, deck_name, image_url))
            
    return {"message": "Deck added."}, 201


@app.get("/api/average")
def get_global_avg():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GLOBAL_AVG)
            average = cursor.fetchone()[0]
            cursor.execute(GLOBAL_NUMBER_OF_DAYS)
            days  = cursor.fetchone()[0]
    return {"average": round(average, 2), "days": days}

    



@app.get("/")
def home():
    return "Hello, world!"