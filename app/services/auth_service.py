from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories import auth_repository as repo
from app.schemas.auth_schema import TokenResponse


def login(db: Session, user_email: str, password: str) -> TokenResponse:
    user = repo.get_user_by_email(db, user_email)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(sub=user.user_email, org_id=user.org_id)
    return TokenResponse(access_token=token)
