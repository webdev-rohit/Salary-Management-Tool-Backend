from typing import Optional

from sqlalchemy.orm import Session

from app.models.users import User


def get_user_by_email(db: Session, user_email: str) -> Optional[User]:
    return db.query(User).filter_by(user_email=user_email).first()
