from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import func

from cupidy.db.repository.db import SessionLocal
from cupidy.db.repository.user import (get_users, create_user, get_user_by_email,get_user_by_id,
                                        create_password_reset_request,
                                          make_only_one_usable_otp, OTP_validation,
                                          change_password, create_user_profile, save_profile_photo)
from fastapi.responses import JSONResponse
from cupidy.services.email import send_otp
from datetime import datetime, timedelta
from cupidy.db.models.user import User, UserProfile, ProfilePhoto
from cupidy.services.auth import generate_token

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

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    allow_privacy_policy: bool

    class Config:
        orm_mode = True

class PhotoData(BaseModel):
    title: str
    url: str
    type: Optional[str] = "gallery"  # Default to 'gallery' if 'type' is not provided

class UploadPhotosRequest(BaseModel):
    user_id: int
    photos: List[PhotoData]

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
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = pwd_context.hash(user.password)
        new_user = create_user(db=db, user=user, hashed_password=hashed_password)
        access_token, refresh_token = generate_token({"user_id":new_user.id, "email":new_user.email})
        return {"access_token":access_token, "refresh_token":refresh_token}
    
    except Exception as e:
        logger.error(f"Error during user signup: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin")
def sign_in(userinfo: dict = Body(...), db: Session = Depends(get_db)):
    if "email" not in userinfo or "password" not in userinfo:
        return JSONResponse(content={"error": "Insufficient login information"}, status_code=400)

    user_email = userinfo.get("email")
    user_password = userinfo.get("password")
    db_user = get_user_by_email(db, email=user_email)  # Assuming this function fetches a user by email

    if not db_user:
        return JSONResponse(content={"error": "User not found"}, status_code=404)

    db_user_pw = db_user.password

    # Check if the stored password is a bcrypt hash (typically starts with $2a$, $2b$, or $2y$)
    if db_user_pw.startswith("$2b$") or db_user_pw.startswith("$2a$") or db_user_pw.startswith("$2y$"):
        # Verify hashed password
        if not pwd_context.verify(user_password, db_user_pw):
            return JSONResponse(content={"error": "Incorrect password"}, status_code=403)
    else:
        # Plain-text password comparison
        if db_user_pw != user_password:
            return JSONResponse(content={"error": "Incorrect password"}, status_code=403)
        else:
            # Rehash plain-text password and update it in the database
            new_hashed_password = pwd_context.hash(user_password)
            db_user.password = new_hashed_password
            db.commit()

    # Generate tokens after successful authentication
    access_token, refresh_token = generate_token({"user_id": db_user.id, "email": db_user.email})
    return {"access_token": access_token, "refresh_token": refresh_token}


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
    
@router.post("/upload_photos")
def upload_photos(request: UploadPhotosRequest, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.id == request.user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if len(request.photos) > 6:
            raise HTTPException(status_code=400, detail="You can upload a maximum of 6 photos.")
        
        uploaded_files = []
        for photo_data in request.photos:
            photo = save_profile_photo(photo_data=photo_data.dict(), user_id=request.user_id, db=db)
            uploaded_files.append({
                "title": photo.title,
                "url": photo.url,
                "type": photo.type
            })
        
        return uploaded_files
    except HTTPException as http_exc:
        logger.error(f"HTTP error: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
                "url": photo.url,
                "type": photo.type,
                "created_at": photo.created_at,
                "updated_at": photo.updated_at
            }
            photo_list.append(photo_data)
        
        return photo_list
    except Exception as e:
        logger.error(f"Error retrieving photos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

import logging
# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@router.get("/match/{user_id}")
def get_matching_users(user_id: int, db: Session = Depends(get_db)):
    try:
        # Get the current user's profile
        current_user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not current_user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Calculate age from birthdate
        if not current_user_profile.birthdate:
            raise HTTPException(status_code=400, detail="Birthdate not available for age calculation")
        
        today = datetime.today().date()
        age = today.year - current_user_profile.birthdate.year - (
            (today.month, today.day) < (current_user_profile.birthdate.month, current_user_profile.birthdate.day)
        )
        min_age = age - 4
        max_age = age + 4

        # Process user interests
        if isinstance(current_user_profile.interests, str):
            user_interests = set(interest.strip().lower() for interest in current_user_profile.interests.split(","))
        else:
            user_interests = set(interest.strip().lower() for interest in current_user_profile.interests)

        # Find potential matches
        potential_matches = db.query(UserProfile).filter(
            UserProfile.user_id != user_id,
            func.lower(UserProfile.gender) == current_user_profile.interested_in.lower(),
            UserProfile.birthdate.isnot(None)
        ).all()

        logger.debug(f"Found {len(potential_matches)} potential matches.")

        # Filter by age range and shared interests
        matching_users = []
        other_users = []
        for match in potential_matches:
            match_age = today.year - match.birthdate.year - (
                (today.month, today.day) < (match.birthdate.month, match.birthdate.day)
            )
            if min_age <= match_age <= max_age:
                if isinstance(match.interests, str):
                    match_interests = set(interest.strip().lower() for interest in match.interests.split(","))
                else:
                    match_interests = set(interest.strip().lower() for interest in match.interests)

                common_interests = user_interests.intersection(match_interests)
                logger.debug(f"Common interests for user {match.user_id}: {common_interests}")
                
                # Get both profile and cover photos
                profile_photo = db.query(ProfilePhoto).filter(
                    ProfilePhoto.user_id == match.user_id,
                    ProfilePhoto.type == "profile"
                ).first()

                cover_photo = db.query(ProfilePhoto).filter(
                    ProfilePhoto.user_id == match.user_id,
                    ProfilePhoto.type == "coverPhoto"
                ).first()

                user_data = {
                    "user_id": match.user_id,
                    "name": match.full_name,
                    "age": match_age,
                    "city": match.city,
                    "gender": match.gender,
                    "interested_in": match.interested_in,
                    "zodiac_sign": match.zodiac_sign,
                    "mbti": match.mbti,
                    "country_name": match.country_name,
                    "locality": match.locality,
                    "profile_photo": profile_photo.url if profile_photo else None,
                    "cover_photo": cover_photo.url if cover_photo else None,
                    "shared_interests": list(common_interests)
                }

                if len(common_interests) >= 2:  # Ensure at least 2 common interests
                    matching_users.append(user_data)
                else:
                    other_users.append(user_data)

        # Sort matches by the number of shared interests (most to least)
        matching_users.sort(key=lambda x: len(x["shared_interests"]), reverse=True)

        # Add other users who match the `interested_in` criterion but have no common interests
        other_additional_matches = db.query(UserProfile).filter(
            UserProfile.user_id != user_id,
            func.lower(UserProfile.gender) == current_user_profile.interested_in.lower(),
            ~UserProfile.user_id.in_([user["user_id"] for user in matching_users + other_users])
        ).all()

        logger.debug(f"Found {len(other_additional_matches)} additional users with no shared interests.")

        for match in other_additional_matches:
            match_age = today.year - match.birthdate.year - (
                (today.month, today.day) < (match.birthdate.month, match.birthdate.day)
            )

            # Get both profile and cover photos
            profile_photo = db.query(ProfilePhoto).filter(
                ProfilePhoto.user_id == match.user_id,
                ProfilePhoto.type == "profile"
            ).first()

            cover_photo = db.query(ProfilePhoto).filter(
                ProfilePhoto.user_id == match.user_id,
                ProfilePhoto.type == "coverPhoto"
            ).first()

            other_users.append({
                "user_id": match.user_id,
                "name": match.full_name,
                "age": match_age,
                "city": match.city,
                "gender": match.gender,
                "interested_in": match.interested_in,
                "zodiac_sign": match.zodiac_sign,
                "mbti": match.mbti,
                "country_name": match.country_name,
                "locality": match.locality,
                "profile_photo": profile_photo.url if profile_photo else None,
                "cover_photo": cover_photo.url if cover_photo else None,
                "shared_interests": []
            })

        # Combine matching users with shared interests first, followed by other users
        final_result = matching_users + other_users

        return final_result

    except HTTPException as http_exc:
        logger.error(f"HTTP error: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/detailInfo/{user_id}")
def detail_info(user_id: int, db: Session = Depends(get_db)):
    usr_info, detail = get_user_by_id(db, user_id)
    all_usr_info = {**usr_info.__dict__, **detail.__dict__}
    all_usr_info.pop("password")
    all_usr_info.pop("_sa_instance_state")
    all_usr_info.pop("id")
    return all_usr_info
