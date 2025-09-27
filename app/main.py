from fastapi import Depends, FastAPI, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import UserCreate, UserResponse, UserLogin
from app.models import User
from app.crud import create_user, authenticate_user, get_user_by_email 
from app.auth import create_access_token
from datetime import datetime
from app.dependencies import get_current_user 
from fastapi.security import OAuth2PasswordRequestForm


app = FastAPI(title="Coworking Reservations", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Coworking Reservations API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if a user with that email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email is already registered"
        )
    
    # Create user
    return create_user(db=db, user=user)

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),  
    db: Session = Depends(get_db)
):
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    
    user = authenticate_user(db, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}, 
        )
    
    access_token = create_access_token(user=user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Protected endpoint that returns information about the authenticated user"""
    return current_user