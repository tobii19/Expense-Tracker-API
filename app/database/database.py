from sqlalchemy.orm import declarative_base,sessionmaker
from sqlalchemy import create_engine
from core.config import DATABASE_URL

Base = declarative_base()

engine = create_engine(DATABASE_URL)

SesionLocal = sessionmaker(autocommit = False,autoflush=False,bind=engine)

def get_db():
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()
        
