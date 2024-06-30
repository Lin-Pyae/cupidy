from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from cupidy.db.repository.db import SessionLocal
from cupidy.db.repository.user import get_users

router = APIRouter()

@router.get("/")
def example():
    return {"hello": "world"}

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to get all users
@router.get("/users")
def read_users(db: Session = Depends(get_db)):
    users = get_users(db)
    return users