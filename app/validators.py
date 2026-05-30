# app/validators.py

from datetime import datetime, time
from fastapi import HTTPException, status

BUSINESS_OPEN = time(8, 0)
BUSINESS_CLOSE = time(20, 0)
MIN_DURATION_MINUTES = 30
MAX_DURATION_MINUTES = 8 * 60


def validate_reservation_time(start_datetime: datetime, end_datetime: datetime):
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