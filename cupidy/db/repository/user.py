from sqlalchemy.orm import Session
from cupidy.db.models.user import User

#Getting All users from database to test
def get_users(db: Session):
    return db.query(User).all()