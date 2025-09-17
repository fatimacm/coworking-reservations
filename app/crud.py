from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserLogin
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