from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from database import get_connection
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SECRET_KEY = "admissionbot_secret_123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(user: UserRegister):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed_password = pwd_context.hash(user.password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (user.username, hashed_password)
        )
        conn.commit()
        conn.close()
        return {"message": "User registered successfully!"}
    except Exception as e:
        return {"message": "Registration failed. Database not connected yet."}

@router.post("/login")
def login(user: UserLogin):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE username = %s",
            (user.username,)
        )
        result = cursor.fetchone()
        conn.close()
        if not result or not pwd_context.verify(user.password, result[0]):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
        return {"token": token}
    except HTTPException as e:
        raise e
    except Exception as e:
        return {"message": "Login failed. Database not connected yet."}