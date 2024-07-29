from sqlalchemy.orm import Session
from cupidy.db.models.user import User, UserProfile, ProfilePhoto, PasswordResetRequest
from pydantic import EmailStr
from datetime import datetime, date
import os
from fastapi import UploadFile
from uuid import uuid4

# # Directory where images will be stored url format
# UPLOAD_DIR = "uploads/"

# # Ensure the upload directory exists
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# def save_profile_photo(file: UploadFile, user_id: int, db: Session):
#     # Count existing photos for the user to determine the next photo number
#     photo_count = db.query(ProfilePhoto).filter(ProfilePhoto.user_id == user_id).count()
    
#     # Generate a unique filename based on user ID and the next photo number
#     file_extension = file.filename.split(".")[-1]
#     filename = f"user_{user_id}_photo_{photo_count + 1}.{file_extension}"
#     filepath = os.path.join(UPLOAD_DIR, filename)
    
#     # Save the file
#     with open(filepath, "wb") as f:
#         f.write(file.file.read())
    
#     # Create a database entry
#     photo = ProfilePhoto(
#         user_id=user_id,
#         title=file.filename,
#         url=filepath,
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow()
#     )
#     db.add(photo)
#     db.commit()
#     db.refresh(photo)
#     return photo

#Saving User Photos in database
def save_profile_photo(file: UploadFile, user_id: int, db: Session):
    # Read the file content as binary data
    file_data = file.file.read()
    
    # Create a database entry with the binary data
    photo = ProfilePhoto(
        user_id=user_id,
        title=file.filename,
        blob=file_data,
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
        allow_privacy_policy=user.allow_privacy_policy,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
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
def create_password_reset_request(db: Session, user_id: int, otp: str, expires_at):
    db_reset_request = PasswordResetRequest(
        user_id=user_id,
        otp=otp,
        created_at=datetime.now(),
        expires_at=expires_at,
        is_used = False
    )
    db.add(db_reset_request)
    db.commit()
    db.refresh(db_reset_request)
    return db_reset_request

def make_only_one_usable_otp(db: Session, user_id: int):
    db.query(PasswordResetRequest).filter(
        PasswordResetRequest.user_id == user_id, PasswordResetRequest.is_used == False).update(
        {PasswordResetRequest.is_used: True},
        synchronize_session=False
    )
    db.commit()

def OTP_validation(db: Session, otp: str):
    user_requested_otp = db.query(PasswordResetRequest).filter(
                        PasswordResetRequest.otp == otp, PasswordResetRequest.is_used == False).first()
    
    if not user_requested_otp:
        raise Exception("Invalid OTP")
    
    if datetime.now() > user_requested_otp.expires_at:
        raise Exception("OTP expired")
    
    user_requested_otp.is_used = True

    db.commit()

def change_password(db: Session, user_id, new_password):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise Exception("User not found")
    
    user.password = new_password
    db.commit()