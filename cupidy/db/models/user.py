from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from cupidy.db.repository.db import Base
from datetime import datetime, date

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    allow_privacy_policy = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    # Relationship to UserProfile
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    # Relationship to ProfilePhoto
    photos = relationship("ProfilePhoto", back_populates="user")

    # Relationship to PasswordResetRequest
    password_reset_requests = relationship("PasswordResetRequest", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String)
    birthdate = Column(Date)
    gender = Column(String)
    interested_in = Column(String)
    interests = Column(Text)  # Using Text for array-like data
    zodiac_sign = Column(String)
    mbti = Column(String)
    country_name = Column(String)
    city = Column(String)
    locality = Column(String)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationship back to User
    user = relationship("User", back_populates="profile")
    # Relationship to ProfilePhoto
    # photos = relationship("ProfilePhoto", back_populates="user_profile")

class ProfilePhoto(Base):
    __tablename__ = "profile_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ForeignKey to User
    # user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)  # ForeignKey to UserProfile
    title = Column(String)
    blob = Column(LargeBinary, nullable=False)
    # url = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    # user_profile = relationship("UserProfile", back_populates="photos")
    user = relationship("User", back_populates="photos")

class PasswordResetRequest(Base):
    __tablename__ = "password_reset_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reset_token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationship back to User
    user = relationship("User", back_populates="password_reset_requests")