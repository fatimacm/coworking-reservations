from sqlalchemy.orm import Session
from app.models import User, Reservation
from app.schemas import UserCreate, UserLogin, ReservationCreate, ReservationUpdate
from app.security import hash_password, verify_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password),
        role=user.role.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, user_login: UserLogin):
    user = get_user_by_email(db, user_login.email)
    if not user:
        return False
    if not verify_password(user_login.password, user.hashed_password):
        return False
    return user


def get_reservation_by_id(db: Session, reservation_id: int, user_id: int):
    return db.query(Reservation).filter(
        Reservation.id == reservation_id, 
        Reservation.user_id == user_id
    ).first()

def create_reservation(db: Session, reservation: ReservationCreate, user_id: int):
    db_reservation = Reservation(
        user_id=user_id,
        space_name=reservation.space_name.value,  
        start_datetime=reservation.start_datetime,
        end_datetime=reservation.end_datetime
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def update_reservation(db: Session, reservation_id: int, reservation_update: ReservationUpdate, user_id: int):
    db_reservation = get_reservation_by_id(db, reservation_id, user_id)
    if not db_reservation:
        return None
    
    
    for field, value in reservation_update.dict(exclude_unset=True).items():
        if hasattr(db_reservation, field):
            if field == "space_name" and value:
                setattr(db_reservation, field, value.value)
            else:
                setattr(db_reservation, field, value)
    
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def delete_reservation(db: Session, reservation_id: int, user_id: int):

    db_reservation = get_reservation_by_id(db, reservation_id, user_id)
    if not db_reservation:
        return False
    
    db_reservation.status = "cancelled"
    db.commit()
    db.refresh(db_reservation)
    return db_reservation  

def reactivate_reservation(db: Session, reservation_id: int, user_id: int):
    
    db_reservation = get_reservation_by_id(db, reservation_id, user_id)
    if not db_reservation or db_reservation.status != "cancelled":
        return False
    
    db_reservation.status = "active"
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def get_user_reservations(db: Session, user_id: int, include_cancelled: bool = False):
    query = db.query(Reservation).filter(Reservation.user_id == user_id)
    
    if not include_cancelled:
        query = query.filter(Reservation.status == "active")
    
    return query.all()