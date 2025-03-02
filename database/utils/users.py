from sqlalchemy.orm import Session
from database.models.users import User

def get_user(db: Session, tg_id: int) -> User:
    """Get a user by Telegram ID."""
    return db.query(User).filter(User.tg_id == tg_id).first()

def get_user_by_id(db: Session, id: int) -> User:
    """Get a user by ID."""
    return db.query(User).filter(User.id == id).first()

def create_user(db: Session, name: str, tg_id: int) -> User:
    """Create a new user."""
    user = User(name=name, tg_id=tg_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_balance(db: Session, user_id: int, amount: int) -> User:
    """Update user balance."""
    user = db.query(User).filter(User.id == user_id).first()
    user.balance += amount
    db.commit()
    db.refresh(user)
    return user

def update_user_dislikes(db: Session, user_id: int, amount: int) -> User:
    """Update user dislikes."""
    user = db.query(User).filter(User.id == user_id).first()
    user.dislikes += amount
    db.commit()
    db.refresh(user)
    return user

def update_user_grade(db: Session, user_id: int, grade: str) -> User:
    """Update user grade."""
    user = db.query(User).filter(User.id == user_id).first()
    user.grade = grade
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> None:
    """Delete a user."""
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()

def get_all_users(db: Session) -> list[User]:
    """Get all users."""
    return db.query(User).all()