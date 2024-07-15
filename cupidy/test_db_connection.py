# To Test Connection with Database
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.repository.db import Base, DATABASE_URL

def test_connection():
    try:
        # Create an engine and connect to the database
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Test the connection by querying the database
        result = session.execute(text("SELECT 1"))
        if result.scalar() == 1:
            print("Connection to the database was successful!")
        else:
            print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_connection()