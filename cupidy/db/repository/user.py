from sqlalchemy.orm import Session
from cupidy.db.models.user import User, UserProfile, ProfilePhoto, PasswordResetRequest
from pydantic import EmailStr

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
def create_user_profile(db: Session, user_profile):
    db_profile = UserProfile(
        user_id=user_profile.user_id,
        full_name=user_profile.full_name,
        birthdate=user_profile.birthdate,
        gender=user_profile.gender,
        interested_in=user_profile.interested_in,
        interests=user_profile.interests,
        zodiac_sign=user_profile.zodiac_sign,
        mbti=user_profile.mbti,
        country_name=user_profile.country_name,
        city=user_profile.city,
        locality=user_profile.locality
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