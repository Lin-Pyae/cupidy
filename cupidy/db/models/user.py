from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..repository.db import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    profile = relationship("Profile", back_populates="user", uselist=False)
    user_profile_detail = relationship("UserProfileDetail", back_populates="user", uselist=False)
    photos = relationship("Photo", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"
    
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    gender = Column(String)
    location = Column(String)
    profile_picture_url = Column(String)
    name = Column(String)
    birthday = Column(Date)
    
    user = relationship("User", back_populates="profile")

class UserProfileDetail(Base):
    __tablename__ = "user_profile_details"
    
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True, unique=True)
    bio = Column(Text)
    looking_for = Column(String)
    mbti_type = Column(String)
    interests = Column(Text)
    school = Column(String)
    zodiac_sign = Column(String)
    
    user = relationship("User", back_populates="user_profile_detail")

class Photo(Base):
    __tablename__ = "photos"
    
    photo_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    photo_url = Column(String, nullable=False)
    
    user = relationship("User", back_populates="photos")