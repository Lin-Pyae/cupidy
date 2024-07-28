from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime, date

from cupidy.db.repository.db import SessionLocal
from cupidy.db.repository.user import get_users, create_user, get_user_by_email, create_user_profile, save_profile_photo
from cupidy.db.models.user import User, UserProfile, ProfilePhoto

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
    
# # Route to upload a profile photo url format
# @router.post("/upload_photos")
# def upload_photos(user_id: int = Form(...), files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
#     try:
#         db_user = db.query(User).filter(User.id == user_id).first()
#         if not db_user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         if len(files) > 6:
#             raise HTTPException(status_code=400, detail="You can upload a maximum of 6 files.")
        
#         uploaded_files = []
#         for file in files:
#             photo = save_profile_photo(file=file, user_id=user_id, db=db)
#             uploaded_files.append({"filename": photo.title, "url": photo.url})
        
#         return uploaded_files
#     except HTTPException as http_exc:
#         logger.error(f"HTTP error: {http_exc.detail}")
#         raise http_exc
#     except Exception as e:
#         logger.error(f"Unexpected error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/upload_photos")
def upload_photos(user_id: int = Form(...), files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if len(files) > 6:
            raise HTTPException(status_code=400, detail="You can upload a maximum of 6 files.")
        
        uploaded_files = []
        for file in files:
            photo = save_profile_photo(file=file, user_id=user_id, db=db)
            uploaded_files.append({"filename": photo.title})
        
        return uploaded_files
    except HTTPException as http_exc:
        logger.error(f"HTTP error: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# # Route to get all photos of a user url format
# @router.get("/users/{user_id}/photos")
# def get_user_photos(user_id: int, db: Session = Depends(get_db)):
#     try:
#         db_user = db.query(User).filter(User.id == user_id).first()
#         if not db_user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         photos = db.query(ProfilePhoto).filter(ProfilePhoto.user_id == user_id).all()
#         return photos
#     except Exception as e:
#         logger.error(f"Error retrieving photos: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")

import base64

@router.get("/users/{user_id}/photos")
def get_user_photos(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        photos = db.query(ProfilePhoto).filter(ProfilePhoto.user_id == user_id).all()
        
        photo_list = []
        for photo in photos:
            photo_data = {
                "id": photo.id,
                "title": photo.title,
                "blob": base64.b64encode(photo.blob).decode('utf-8'),  # Encode as base64 string
                "created_at": photo.created_at,
                "updated_at": photo.updated_at
            }
            photo_list.append(photo_data)
        
        return photo_list
    except Exception as e:
        logger.error(f"Error retrieving photos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")