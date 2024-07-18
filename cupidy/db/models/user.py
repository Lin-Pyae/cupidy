from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from cupidy.db.repository.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    allow_privacy_policy = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

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
    photos = relationship("ProfilePhoto", back_populates="user_profile")

class ProfilePhoto(Base):
    __tablename__ = "profile_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ForeignKey to User
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)  # ForeignKey to UserProfile
    title = Column(String)
    url = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="photos")
    user = relationship("User", back_populates="photos")

class PasswordResetRequest(Base):
    __tablename__ = "password_reset_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, nullable=False)
    
    # Relationship back to User
    user = relationship("User", back_populates="password_reset_requests")