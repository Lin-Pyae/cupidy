from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with actual URL eg:DatabaseServer://username:password@server/DatabaseName
DATABASE_URL = "postgresql://postgres:admin123@localhost:5433/cupidy"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    from cupidy.db.models.user import User, UserProfile, ProfilePhoto, PasswordResetRequest 
    Base.metadata.create_all(bind=engine)