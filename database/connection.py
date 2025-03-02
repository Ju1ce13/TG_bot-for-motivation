from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)