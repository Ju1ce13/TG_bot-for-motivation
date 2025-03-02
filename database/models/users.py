from database.models.models import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer)
    name = Column(String, nullable=False)
    grade = Column(String, default="Джун")
    role = Column(String, nullable=False, default='user')
    balance = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
