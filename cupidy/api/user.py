from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext

from cupidy.db.repository.db import SessionLocal
from cupidy.db.repository.user import get_users, create_user, get_user_by_email

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password_hash: str = Field(..., min_length=6)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to get all users
@router.get("/users")
def read_users(db: Session = Depends(get_db)):
    users = get_users(db)
    return users

# Route to sign up a new user
@router.post("/signup", response_model=UserCreate)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password_hash)
    new_user = create_user(db=db, user=user, hashed_password=hashed_password)
    return new_user