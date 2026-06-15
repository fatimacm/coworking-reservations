from sqlalchemy.orm import Session
from app.models import User, Reservation
from app.schemas import UserCreate, UserLogin, ReservationCreate, ReservationUpdate
from app.security import hash_password, verify_password
from app.validators import (
    normalize_datetime,
    validate_reservation_time,
    validate_no_overlap,
    validate_daily_reservation_limit
)

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
    """
    Authenticates a user using email and password credentials.

    Returns:
    - User instance when credentials are valid.
    - False when authentication fails.
    """
    
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
    """
    Creates a new reservation after applying all business validations.

    Business rules:
    - Reservation dates are normalized before validation.
    - Temporal reservation policies must be satisfied.
    - Overlapping reservations are not allowed.
    - Users cannot exceed the daily reservation limit.
    - Reservations are created with active status by default.
    """

    start_datetime = normalize_datetime(reservation.start_datetime)
    end_datetime = normalize_datetime(reservation.end_datetime)

    validate_reservation_time(
        start_datetime,
        end_datetime
    )

    validate_no_overlap(
        db=db,
        user_id=user_id,
        space_name=reservation.space_name.value,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    )

    validate_daily_reservation_limit(
    db=db,
    user_id=user_id,
    start_datetime=start_datetime,
    end_datetime=end_datetime
    )
    
    db_reservation = Reservation(
        user_id=user_id,
        space_name=reservation.space_name.value,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    )

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    return db_reservation

def update_reservation(db: Session, reservation_id: int, reservation_update: ReservationUpdate, user_id: int):
    """
    Updates an existing reservation and revalidates all business rules.

    Business rules:
    - Only reservations owned by the user can be updated.
    - Updated dates are normalized before validation.
    - Temporal reservation policies must remain valid.
    - Updates cannot create overlaps with other active reservations.
    - Updates cannot cause the user to exceed the daily reservation limit.
    - The current reservation is excluded from overlap and daily limit checks.
    """
    
    db_reservation = get_reservation_by_id(db, reservation_id, user_id)
    if not db_reservation:
        return None
    
    
    for field, value in reservation_update.model_dump(exclude_unset=True).items():
        if hasattr(db_reservation, field):
            if field == "space_name" and value:
                setattr(db_reservation, field, value.value)
            elif field == "status" and value:
                setattr(db_reservation, field, value.value)
            else:
                setattr(db_reservation, field, value)
    
    db_reservation.start_datetime = normalize_datetime(
        db_reservation.start_datetime
    )

    db_reservation.end_datetime = normalize_datetime(
        db_reservation.end_datetime
    )
    
                
    validate_reservation_time(
        db_reservation.start_datetime,
        db_reservation.end_datetime
    )

    validate_no_overlap(
        db=db,
        user_id=user_id,
        space_name=db_reservation.space_name,
        start_datetime=db_reservation.start_datetime,
        end_datetime=db_reservation.end_datetime,
        reservation_id=reservation_id
    )
    
    validate_daily_reservation_limit(
    db=db,
    user_id=user_id,
    start_datetime=db_reservation.start_datetime,
    end_datetime=db_reservation.end_datetime,
    reservation_id=reservation_id
    )
    
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def delete_reservation(db: Session, reservation_id: int, user_id: int):
    """
    Cancels a reservation using a soft delete strategy.

    Business rules:
    - Reservations are not physically removed from the database.
    - Status is changed from active to cancelled.
    - Cancelled reservations are excluded from overlap validations.
    - Cancelled reservations do not count toward the daily reservation limit.
    """

    db_reservation = get_reservation_by_id(db, reservation_id, user_id)
    if not db_reservation:
        return None
    
    db_reservation.status = "cancelled"
    db.commit()
    db.refresh(db_reservation)
    return db_reservation  

def reactivate_reservation(db: Session, reservation_id: int, user_id: int):
    """
    Reactivates a previously cancelled reservation.

    Business rules:
    - Only cancelled reservations can be reactivated.
    - Active reservations cannot be reactivated.
    - Reservation ownership must be respected.
    """
    
    db_reservation = get_reservation_by_id(db, reservation_id, user_id)
    if not db_reservation or db_reservation.status != "cancelled":
        return None
    
    db_reservation.status = "active"
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def get_user_reservations(db: Session, user_id: int, include_cancelled: bool = False):
    """
    Returns reservations belonging to a specific user.

    Business rules:
    - Active reservations are returned by default.
    - Cancelled reservations are included only when include_cancelled is explicitly enabled.
    """
    
    query = db.query(Reservation).filter(Reservation.user_id == user_id)
    
    if not include_cancelled:
        query = query.filter(Reservation.status == "active")
    
    return query.all()