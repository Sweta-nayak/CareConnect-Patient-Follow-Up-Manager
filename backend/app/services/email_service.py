import smtplib
from email.message import EmailMessage

from app.config import settings


def send_password_reset_otp(
    recipient_email: str,
    otp: str
) -> None:

    # Create the email message
    message = EmailMessage()

    message["Subject"] = "CareConnect - Password Reset OTP"
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient_email

    # Email content
    message.set_content(
        f"""
Hello,

We received a request to reset your CareConnect account password.

Your password reset OTP is:

{otp}

This OTP is valid for 5 minutes.

For your security:
- Do not share this OTP with anyone.
- If you did not request a password reset, ignore this email.

Regards,
CareConnect Team
        """
    )

    # Connect to Gmail SMTP and send the email
    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=20
        ) as server:

            server.starttls()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_APP_PASSWORD
            )

            server.send_message(message)

    except Exception as error:
        print(f"Password reset email sending failed: {error}")
        raise