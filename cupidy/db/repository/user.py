from sqlalchemy.orm import Session
from cupidy.db.models.user import User
from pydantic import EmailStr

#Getting All users from database to test
def get_users(db: Session):
    return db.query(User).all()

# Getting a user by email
def get_user_by_email(db: Session, email: EmailStr):
    return db.query(User).filter(User.email == email).first()

# Creating a new user
def create_user(db: Session, user, hashed_password: str):
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user