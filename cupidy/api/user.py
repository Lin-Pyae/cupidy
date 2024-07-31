from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime, date

from cupidy.db.repository.db import SessionLocal
from cupidy.db.repository.user import (get_users, create_user, get_user_by_email,
                                        create_password_reset_request,
                                          make_only_one_usable_otp, OTP_validation,
                                          change_password, create_user_profile, save_profile_photo)
from fastapi.responses import JSONResponse
from cupidy.services.email import send_otp
from datetime import datetime, timedelta
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

@router.post("/signin")
def sign_in(userinfo: dict = Body(...), db: Session = Depends(get_db)):
    if "email" not in userinfo or "password" not in userinfo:
        return JSONResponse(content={"error": "Insufficient login information"}, status_code=400)

    user_email = userinfo.get("email")
    user_password = userinfo.get("password")
    db_user = get_user_by_email(db, email=user_email)
    if not db_user:
        return JSONResponse(content={"error": "User not found"}, status_code=404)

    db_user_pw = db_user.password

    if not pwd_context.verify(user_password, db_user_pw):
        return JSONResponse(content={"error": "Incorrect password"}, status_code=403)

    return JSONResponse(content={"message": "Login successful"}, status_code=200)


@router.post("/otp-request")
def reset_otp_request(useremail: dict = Body(...), db: Session = Depends(get_db)):
    if "email" not in useremail:
        return JSONResponse(content={"error":"email not provided"},status_code=400)
    user = get_user_by_email(db, email=useremail["email"])
    if not user:
        return JSONResponse(content={"message":"user not found"}, status_code=404)
    # sending otp mail to user
    otp = send_otp(user.email)

    # make the latest requested otp to be usable
    make_only_one_usable_otp(db,user.id)

    expires_at = datetime.now() + timedelta(minutes=5)
    create_password_reset_request(db, user.id, otp, expires_at)
    return JSONResponse(content={"message":f"OTP {otp} has sent successfully"}, status_code=200)

        
@router.post("/otp-validate")
def otp_validation(otp: dict=Body(...), db: Session=Depends(get_db)):
    if "otp" not in otp:
        return JSONResponse(content={"error":"otp not provided"},status_code=400)
    try:
        OTP_validation(db, otp["otp"])
    except Exception as e:
        return JSONResponse(content={"error":str(e)}, status_code=400)
    return JSONResponse(content={"message":"OTP valid to change password"}, status_code=200)

@router.post("/password-reset")
def reset_password(detail: dict=Body(...), db: Session=Depends(get_db)):
    is_enough_info = set(["new_password","user_id"]) <= set(detail.keys())
    if not is_enough_info:
        return JSONResponse(content={"error":"not enough informations provided"}, status_code=400)
    
    new_pass = pwd_context.hash(detail["new_password"])
    try:
        change_password(db, detail["user_id"], new_pass)
    except Exception as e:
        return JSONResponse(content={"error":str(e)}, status_code=400)
    return JSONResponse(content={"message":"Successfully changed password"}, status_code=200)

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