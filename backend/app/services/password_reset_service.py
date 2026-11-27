from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Organization, User, PasswordResetOTP
from app.security import hash_password
from app.services.otp_service import (
    generate_otp,
    hash_otp,
    verify_otp,
    get_otp_expiry,
    MAX_OTP_ATTEMPTS
)
from app.services.email_service import send_password_reset_otp


OTP_RESEND_WAIT_SECONDS = 60
MAX_OTP_REQUESTS_PER_HOUR = 3

GENERIC_RESPONSE = (
    "If an active account matches the supplied details, "
    "a password reset code will be sent to its email address."
)


def request_password_reset(
    db: Session,
    organization_code: str,
    email: str
) -> str:
    """
    Generate and email a password reset OTP when an account exists.
    Always return a generic response to avoid revealing account existence.
    """

    organization_code = organization_code.strip().upper()
    email = email.strip().lower()

    organization = db.scalar(
        select(Organization).where(
            Organization.organization_code == organization_code,
            Organization.is_active.is_(True)
        )
    )

    if not organization:
        return GENERIC_RESPONSE

    user = db.scalar(
        select(User).where(
            User.organization_id == organization.organization_id,
            User.email == email,
            User.is_active.is_(True)
        )
    )

    if not user:
        return GENERIC_RESPONSE

    now = datetime.utcnow()

    # Find the most recent OTP request for this user.
    latest_otp = db.scalar(
        select(PasswordResetOTP)
        .where(
            PasswordResetOTP.organization_id == organization.organization_id,
            PasswordResetOTP.user_id == user.user_id
        )
        .order_by(PasswordResetOTP.created_at.desc())
        .limit(1)
    )

    # Prevent another request within 60 seconds.
    if latest_otp:
        seconds_since_last_request = (
            now - latest_otp.created_at
        ).total_seconds()

        if seconds_since_last_request < OTP_RESEND_WAIT_SECONDS:
            return GENERIC_RESPONSE

    # Limit requests to three per hour.
    one_hour_ago = now - timedelta(hours=1)

    request_count = db.scalar(
        select(func.count())
        .select_from(PasswordResetOTP)
        .where(
            PasswordResetOTP.organization_id == organization.organization_id,
            PasswordResetOTP.user_id == user.user_id,
            PasswordResetOTP.created_at >= one_hour_ago
        )
    )

    if request_count >= MAX_OTP_REQUESTS_PER_HOUR:
        return GENERIC_RESPONSE

    # Invalidate any previously unused OTPs.
    db.query(PasswordResetOTP).filter(
        PasswordResetOTP.organization_id == organization.organization_id,
        PasswordResetOTP.user_id == user.user_id,
        PasswordResetOTP.is_used.is_(False)
    ).update(
        {"is_used": True},
        synchronize_session=False
    )

    # Generate a new six-digit OTP.
    otp = generate_otp()

    otp_record = PasswordResetOTP(
        organization_id=organization.organization_id,
        user_id=user.user_id,
        otp_hash=hash_otp(otp),
        expires_at=get_otp_expiry(),
        attempts=0,
        is_used=False
    )

    db.add(otp_record)
    db.commit()

    # Send the original OTP to the user's email.
    try:
        send_password_reset_otp(user.email, otp)

    except Exception:
        # Invalidate the OTP if email delivery fails.
        otp_record.is_used = True
        db.commit()

    return GENERIC_RESPONSE


def reset_password_with_otp(
    db: Session,
    organization_code: str,
    email: str,
    entered_otp: str,
    new_password: str
) -> str:
    """
    Verify the latest OTP and update the user's password.
    """

    organization_code = organization_code.strip().upper()
    email = email.strip().lower()

    organization = db.scalar(
        select(Organization).where(
            Organization.organization_code == organization_code,
            Organization.is_active.is_(True)
        )
    )

    if not organization:
        raise ValueError("Invalid or expired OTP.")

    user = db.scalar(
        select(User).where(
            User.organization_id == organization.organization_id,
            User.email == email,
            User.is_active.is_(True)
        )
    )

    if not user:
        raise ValueError("Invalid or expired OTP.")

    # Only the newest unused OTP can be verified.
    otp_record = db.scalar(
        select(PasswordResetOTP)
        .where(
            PasswordResetOTP.organization_id == organization.organization_id,
            PasswordResetOTP.user_id == user.user_id,
            PasswordResetOTP.is_used.is_(False)
        )
        .order_by(PasswordResetOTP.created_at.desc())
        .limit(1)
    )

    if not otp_record:
        raise ValueError("Invalid or expired OTP.")

    now = datetime.utcnow()

    if otp_record.expires_at <= now:
        otp_record.is_used = True
        db.commit()
        raise ValueError("OTP has expired. Request a new one.")

    if otp_record.attempts >= MAX_OTP_ATTEMPTS:
        otp_record.is_used = True
        db.commit()
        raise ValueError("Too many incorrect attempts. Request a new OTP.")

    # Check the entered OTP against its stored hash.
    if not verify_otp(entered_otp, otp_record.otp_hash):
        otp_record.attempts += 1

        if otp_record.attempts >= MAX_OTP_ATTEMPTS:
            otp_record.is_used = True

        db.commit()
        raise ValueError("Invalid OTP.")

    # OTP is correct. Consume it and update the password.
    user.password_hash = hash_password(new_password)
    otp_record.is_used = True

    db.commit()

    return "Password reset successfully."