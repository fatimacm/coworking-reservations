# app/validators.py

from datetime import datetime, time, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Reservation

BUSINESS_OPEN = time(8, 0)
BUSINESS_CLOSE = time(20, 0)
MIN_DURATION_MINUTES = 30
MAX_DURATION_MINUTES = 8 * 60
MAX_DAILY_DURATION_MINUTES = 8 * 60

def normalize_datetime(dt: datetime) -> datetime:
    return dt.replace(second=0, microsecond=0)

def validate_not_in_past(start_datetime: datetime):
    now = datetime.now(start_datetime.tzinfo)

    if start_datetime < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservations cannot be created in the past."
        )

def validate_reservation_time(start_datetime: datetime, end_datetime: datetime):
    start_datetime = normalize_datetime(start_datetime)
    end_datetime = normalize_datetime(end_datetime)
    
    validate_not_in_past(start_datetime)

    if end_datetime <= start_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End datetime must be after start datetime."
        )

    if start_datetime.date() != end_datetime.date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservations must start and end on the same day."
        )

    if start_datetime.time() < BUSINESS_OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservations cannot start before 08:00."
        )

    if end_datetime.time() > BUSINESS_CLOSE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservations cannot end after 20:00."
        )

    duration_minutes = (end_datetime - start_datetime).total_seconds() / 60

    if duration_minutes < MIN_DURATION_MINUTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum reservation duration is 30 minutes."
        )

    if duration_minutes > MAX_DURATION_MINUTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum reservation duration is 8 hours."
        )
        
def validate_no_overlap(
    db: Session,
    user_id: int,
    space_name: str,
    start_datetime,
    end_datetime,
    reservation_id: int | None = None
):
    query = db.query(Reservation).filter(
        Reservation.status == "active",
        Reservation.start_datetime < end_datetime,
        Reservation.end_datetime > start_datetime,
        or_(
            Reservation.space_name == space_name,
            Reservation.user_id == user_id
        )
    )

    if reservation_id is not None:
        query = query.filter(Reservation.id != reservation_id)

    existing_reservation = query.first()

    if existing_reservation:
        if existing_reservation.space_name == space_name:
            detail = "This space is already reserved during the selected time range."
        else:
            detail = "User already has another reservation during the selected time range."

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

def validate_daily_reservation_limit(
    db: Session,
    user_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    reservation_id: int | None = None
):
    day_start = start_datetime.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    day_end = start_datetime.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999
    )

    query = db.query(Reservation).filter(
        Reservation.user_id == user_id,
        Reservation.status == "active",
        Reservation.start_datetime >= day_start,
        Reservation.start_datetime <= day_end
    )

    if reservation_id is not None:
        query = query.filter(Reservation.id != reservation_id)

    existing_reservations = query.all()

    existing_minutes = sum(
        (reservation.end_datetime - reservation.start_datetime).total_seconds() / 60
        for reservation in existing_reservations
    )

    new_minutes = (end_datetime - start_datetime).total_seconds() / 60

    total_minutes = existing_minutes + new_minutes

    if total_minutes > MAX_DAILY_DURATION_MINUTES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Daily reservation limit exceeded. Users cannot reserve more than 8 hours per day."
        )
