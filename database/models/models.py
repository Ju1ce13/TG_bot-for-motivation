from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from database.connection import engine

Base = declarative_base()
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

