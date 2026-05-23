from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(sub: str, org_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_valid_time)
    payload = {"sub": sub, "org_id": org_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
