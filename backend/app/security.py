
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings


# Create password hashing object using Argon2
password_hash = PasswordHash.recommended()


# 1. Hash a plain password
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# 2. Verify a password during login
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# 3. Create JWT access token
def create_access_token(
    user_id: str,
    organization_id: str,
    role: str
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "organization_id": organization_id,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    return token


# 4. Verify JWT access token
def verify_access_token(token: str) -> dict:

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=["HS256"]
    )

    return payload
