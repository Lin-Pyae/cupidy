from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext

from cupidy.db.repository.db import SessionLocal
from cupidy.db.repository.user import get_users, create_user, get_user_by_email
from fastapi.responses import JSONResponse


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Route to get all users

@router.get("/")
def testFunction():
    return "Hello Testing123"

import logging

logger = logging.getLogger(__name__)

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
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = create_user(db=db, user=user, hashed_password=hashed_password)
    return new_user

@router.post("/signin")
def sign_in(userinfo: dict = Body(...), db: Session = Depends(get_db)):
    if "email" and "password" not in userinfo:
        return JSONResponse(content={"error":"insufficient login informations"},status_code=400)
    user_email = userinfo.get("email")
    user_password = userinfo.get("password")
    db_user = get_user_by_email(db, email=user_email)
    if not db_user:
        return JSONResponse(content={"message":"user not found"}, status_code=404)
    db_user_pw = db_user.password

    if not pwd_context.verify(user_password,db_user_pw):
        return JSONResponse(content={"message":"incorrect user password"}, status_code=403)
    return JSONResponse(content={"message":"login success"}, status_code=200)
