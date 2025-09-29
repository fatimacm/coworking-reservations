from fastapi import Depends, FastAPI, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import UserCreate, UserResponse, UserLogin, ReservationResponse, ReservationCreate, ReservationUpdate
from app.models import User, Reservation
from app.crud import create_user, authenticate_user, get_user_by_email, get_user_reservations, create_reservation, get_reservation_by_id, update_reservation, delete_reservation
from app.auth import create_access_token
from datetime import datetime
from app.dependencies import get_current_user 
from fastapi.security import OAuth2PasswordRequestForm
from typing import List


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


@app.get("/reservations", response_model=List[ReservationResponse])
def get_my_reservations(
    include_cancelled: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_reservations(db, current_user.id, include_cancelled)

@app.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_my_reservation(
    reservation: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_reservation(db, reservation, current_user.id)

@app.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_my_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    reservation = get_reservation_by_id(db, reservation_id, current_user.id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@app.put("/reservations/{reservation_id}", response_model=ReservationResponse)
def update_my_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    reservation = update_reservation(db, reservation_id, reservation_update, current_user.id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@app.delete("/reservations/{reservation_id}", response_model=ReservationResponse)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if reservation.status == "cancelled":
        return reservation  

    reservation.status = "cancelled"
    db.commit()
    db.refresh(reservation)

    return reservation