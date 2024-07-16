from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime, date

from cupidy.db.repository.db import SessionLocal
from cupidy.db.repository.user import get_users, create_user, get_user_by_email, create_user_profile
from cupidy.db.models.user import User, UserProfile

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserProfileCreate(BaseModel):
    user_id: int
    full_name: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    interested_in: Optional[str] = None
    interests: Optional[List[str]] = None
    zodiac_sign: Optional[str] = None
    mbti: Optional[str] = None
    country_name: Optional[str] = None
    city: Optional[str] = None
    locality: Optional[str] = None

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    allow_privacy_policy: bool

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def testFunction():
    return "Hello Testing123"

import logging
logger = logging.getLogger(__name__)

# Route to get all users
@router.get("/users")
def read_users(db: Session = Depends(get_db)):
    try:
        users = get_users(db)
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Route to sign up a new user
@router.post("/signup", response_model=UserCreate)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = pwd_context.hash(user.password)
        new_user = create_user(db=db, user=user, hashed_password=hashed_password)
        return new_user
    except Exception as e:
        logger.error(f"Error during user signup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Route to add detailed user profile information
@router.post("/detailinfo", response_model=UserProfileCreate)
def add_user_profile(user_profile: UserProfileCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id == user_profile.user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_profile = create_user_profile(db=db, user_profile=user_profile, user_id=db_user.id)
        return new_profile
    except Exception as e:
        logger.error(f"Error adding user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")