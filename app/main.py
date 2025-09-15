from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import User 

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
