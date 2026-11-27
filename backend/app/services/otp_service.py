import secrets
from datetime import datetime, timedelta

from app.security import hash_password, verify_password


OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 5


def generate_otp() -> str:
    """
    Generate a cryptographically secure six-digit OTP.
    """
    return f"{secrets.randbelow(1000000):06d}"


def hash_otp(otp: str) -> str:
    """
    Hash the OTP before storing it in the database.
    """
    return hash_password(otp)


def verify_otp(entered_otp: str, stored_hash: str) -> bool:
    """
    Compare the entered OTP with its stored hash.
    """
    return verify_password(entered_otp, stored_hash)


def get_otp_expiry() -> datetime:
    """
    Return the OTP expiry time.
    """
    return datetime.utcnow() + timedelta(
        minutes=OTP_EXPIRY_MINUTES
    )


def is_otp_expired(expires_at: datetime) -> bool:
    """
    Check whether the OTP has expired.
    """
    return datetime.utcnow() >= expires_at