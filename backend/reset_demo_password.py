
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Organization, User
from app.security import hash_password


# New password for our fictional demo Admin
new_password = "GreenValley@123"

db = SessionLocal()

try:
    # Find Green Valley Hospital
    organization = db.scalar(
        select(Organization).where(
            Organization.organization_code == "GREENVALLEY001"
        )
    )

    if not organization:
        print("Organization not found")

    else:
        # Find its Admin user
        user = db.scalar(
            select(User).where(
                User.organization_id == organization.organization_id,
                User.email == "admin@greenvalley.com"
            )
        )

        if not user:
            print("Admin user not found")

        else:
            # Generate a new Argon2 password hash
            user.password_hash = hash_password(new_password)

            # Save the updated password hash
            db.commit()

            print("Password reset successful!")
            print("Email:", user.email)
            print("New password:", new_password)

except Exception as error:
    db.rollback()
    print("Password reset failed:", error)

finally:
    db.close()
