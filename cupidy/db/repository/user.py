from sqlalchemy.orm import Session
from cupidy.db.models.user import User, UserProfile, ProfilePhoto, PasswordResetRequest
from pydantic import EmailStr
from datetime import datetime, date
import os
from fastapi import UploadFile
from uuid import uuid4

# Directory where images will be stored
UPLOAD_DIR = "uploads/"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_profile_photo(file: UploadFile, user_id: int, db: Session):
    # Count existing photos for the user to determine the next photo number
    photo_count = db.query(ProfilePhoto).filter(ProfilePhoto.user_id == user_id).count()
    
    # Generate a unique filename based on user ID and the next photo number
    file_extension = file.filename.split(".")[-1]
    filename = f"user_{user_id}_photo_{photo_count + 1}.{file_extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save the file
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    
    # Create a database entry
    photo = ProfilePhoto(
        user_id=user_id,
        title=file.filename,
        url=filepath,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo

# Getting all users from the database to test
def get_users(db: Session):
    return db.query(User).all()

# Getting a user by email
def get_user_by_email(db: Session, email: EmailStr):
    return db.query(User).filter(User.email == email).first()

# Creating a new user
def create_user(db: Session, user, hashed_password: str):
    db_user = User(
        email=user.email,
        password=hashed_password,
        allow_privacy_policy=user.allow_privacy_policy
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Adding detailed user profile information
def create_user_profile(db: Session, user_profile, user_id: int):
    db_profile = UserProfile(
        user_id=user_id,
        full_name=user_profile.full_name,
        birthdate=user_profile.birthdate,
        gender=user_profile.gender,
        interested_in=user_profile.interested_in,
        interests=user_profile.interests,
        zodiac_sign=user_profile.zodiac_sign,
        mbti=user_profile.mbti,
        country_name=user_profile.country_name,
        city=user_profile.city,
        locality=user_profile.locality,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

# Adding a profile photo
def add_profile_photo(db: Session, photo):
    db_photo = ProfilePhoto(
        user_profile_id=photo.user_profile_id,
        title=photo.title,
        url=photo.url
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

# Creating a password reset request
def create_password_reset_request(db: Session, user_id: int, reset_token: str, expires_at):
    db_reset_request = PasswordResetRequest(
        user_id=user_id,
        reset_token=reset_token,
        expires_at=expires_at
    )
    db.add(db_reset_request)
    db.commit()
    db.refresh(db_reset_request)
    return db_reset_request