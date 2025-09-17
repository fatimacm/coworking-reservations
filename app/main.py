from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import User 
from app.schemas import UserCreate, UserResponse, UserLogin  # ← Nuevos imports
from app.crud import create_user, authenticate_user  # ← Nuevos imports
from app.security import hash_password, verify_password  # ← Nuevos imports


app = FastAPI(title="Coworking Reservations", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Coworking Reservations API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "details": str(e)}

@app.get("/users-count")
def count_users(db: Session = Depends(get_db)):
    count = db.query(User).count()
    return {"users_count": count, "table": "users table working!"}
    
# ENDPOINTS DE PRUEBA
""" @app.post("/test-hash")
def test_password_hashing():
    password = "changedpsswd"
    hashed = hash_password(password)
    verification = verify_password(password, hashed)
    return {
        "original": password,
        "hashed": hashed,
        "verification_correct": verification,
        "verification_wrong": verify_password("password_incorrecta", hashed)
    }

@app.post("/test-user", response_model=UserResponse)
def create_test_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)

@app.post("/test-auth")
def test_authentication(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login)
    if user:
        return {"authentication": "success", "user_id": user.id, "username": user.username}
    return {"authentication": "failed"}

 """