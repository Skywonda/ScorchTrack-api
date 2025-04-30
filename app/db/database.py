from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True, 
    pool_size=10,      
    max_overflow=20 
)

SessionLocal = scoped_session(sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
))

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    from app.db import models  
    
    models.Base.metadata.create_all(bind=engine)
    print("All database tables created successfully")

def drop_tables():
    from app.db import models
    
    models.Base.metadata.drop_all(bind=engine)
    print("All database tables dropped successfully")